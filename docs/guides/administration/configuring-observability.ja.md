# オブザーバビリティを設定する

Dependency-Track は、専用の管理サーバーを通じてヘルスチェックとメトリクスのエンドポイントを公開します。管理サーバーは、メインのアプリケーションサーバーとは独立して別のポートで稼働します。

!!! tip
    オブザーバビリティに関するすべての設定プロパティは、[設定リファレンス](../../reference/configuration/properties.md)の *Observability* カテゴリーに記載されています。

## Kubernetes のヘルスプローブを設定する {#configuring-kubernetes-health-probes}

管理サーバーは、[MicroProfile Health] 仕様に準拠したヘルスチェックのエンドポイントを公開します。これらのエンドポイントは Kubernetes の[プローブの種類][probe types]に直接対応します。

Deployment マニフェストに次のプローブを追加します。[`dt.management.port`](../../reference/configuration/properties.md#dtmanagementport)(デフォルト: `9000`)を変更した場合は、ポートを調整してください。

```yaml linenums="1"
containers:
  - name: apiserver
    livenessProbe:
      httpGet:
        path: /health/live
        port: 9000
      initialDelaySeconds: 15
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /health/ready
        port: 9000
      initialDelaySeconds: 15
      periodSeconds: 10
    startupProbe:
      httpGet:
        path: /health/started
        port: 9000
      initialDelaySeconds: 10
      failureThreshold: 30
      periodSeconds: 5
```

`/health/started` の起動プローブは、[初期化タスク](../../reference/configuration/init-tasks.md)の実行中はタスクごとの進捗を報告し、メインサーバーの準備が整うと正常な状態になります。集約エンドポイント `/health` は、すべてのチェックを合わせた状態を返します。

## Prometheus メトリクスのスクレイプを有効にする {#enabling-prometheus-metrics-scraping}

メトリクスはデフォルトで無効です。[`dt.metrics.enabled`](../../reference/configuration/properties.md#dtmetricsenabled) で有効にします。

```ini
dt.metrics.enabled=true
```

有効にすると、メトリクスは管理ポートの `/metrics` で [Prometheus text exposition format] で提供されます。

HTTP Basic 認証でエンドポイントを保護するには、[`dt.metrics.auth.username`](../../reference/configuration/properties.md#dtmetricsauthusername) と [`dt.metrics.auth.password`](../../reference/configuration/properties.md#dtmetricsauthpassword) の両方を設定します。

Prometheus の設定にスクレイプ対象を追加します。

```yaml linenums="1"
scrape_configs:
  - job_name: dependency-track
    metrics_path: /metrics
    static_configs:
      - targets:
          - "apiserver:9000"
    # Uncomment if you enabled authentication:
    # basic_auth:
    #   username: "metrics"
    #   password: "changeme"
```

## Grafana でメトリクスを可視化する {#visualizing-metrics-with-grafana}

プロジェクトは、サポート対象の成果物として Grafana ダッシュボードを公開していません。メンテナーが自分たちの用途で使っているダッシュボードは、[API サーバーのリポジトリ][dashboards]にあります。

!!! warning
    これらのダッシュボードはサポート対象外であり、現在のリリースで公開されているメトリクスに追従していることも保証されません。パネルが、名前が変更されたメトリクスや削除されたメトリクスを参照していることがあります。

出発点として利用してください。デプロイのメトリクスとアラートの要件に合わせて、独自のダッシュボードを構築してください。

## ログレベルを調整する {#adjusting-log-levels}

デフォルトでは、Dependency-Track はアプリケーションのロガーでは `INFO` レベル、それ以外のすべてのロガーでは `WARN` レベルでログを出力します。特定の領域のトラブルシューティングを行うには、該当するロガーのログレベルを上げます。

```properties
dt.logging.level."org.dependencytrack"=DEBUG
```

特別なロガー名 `ROOT` は、明示的に設定されていないすべてのロガーに適用されます。

```properties
dt.logging.level."ROOT"=ERROR
```

これらのプロパティを環境変数として指定する方法については、[環境変数との対応](../../reference/configuration/application.md#environment-variable-mapping)のドキュメントを参照してください。

## ログの設定を変更する {#changing-the-logging-configuration}

Dependency-Track はログの出力に [Logback] を使います。デフォルトの設定では、人間が読みやすいテキスト形式で stdout にログを書き込みます。

コンテナーイメージには、JSON 形式の設定 `logback-json.xml` も同梱されており、アプリケーションの作業ディレクトリに配置されています。Splunk、Elasticsearch、Loki などの集中ログ管理システムにログを送る場合は、通常 JSON 形式の出力のほうが適しています。Logback にそのファイルを指定して有効にします。

```ini
EXTRA_JAVA_OPTIONS="-Dlogback.configurationFile=logback-json.xml"
```

コンテナーがこのフラグを JVM のコマンドラインに追加するように、`EXTRA_JAVA_OPTIONS` で設定します。詳しくは [JVM オプションのリファレンス](../../reference/configuration/application.md#jvm-options)を参照してください。

完全に独自の設定を使うには、独自のファイルをコンテナーにマウントし、同じ方法で参照します。パスは相対パス(作業ディレクトリを基準に解決されます)と絶対パスのどちらでも指定できます。ファイルの形式については [Logback の設定マニュアル][Logback]で説明しています。

[Logback]: https://logback.qos.ch/manual/configuration.html
[MicroProfile Health]: https://download.eclipse.org/microprofile/microprofile-health-4.0.1/microprofile-health-spec-4.0.1.html
[Prometheus text exposition format]: https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format
[dashboards]: https://github.com/DependencyTrack/dependency-track/tree/main/dev/monitoring/grafana/dashboards
[probe types]: https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/
