# スケーリング

このガイドは、デプロイがすでに[本番環境にデプロイする](deploying-to-production.md)のベースライン(複数のインスタンス、共有ファイルストレージ、チューニング済みの PostgreSQL、オブザーバビリティの整備)に従っていることを前提とします。このガイドでは、負荷がかかった状態でそのベースラインをチューニングする方法を説明します。

## API トラフィックとバックグラウンド処理を分離する {#separate-api-traffic-from-background-work}

デフォルトでは、すべてのインスタンスが API トラフィックを処理**し**、バックグラウンドワーカーも実行します。クラスターが大きくなると、バックグラウンド処理の急増(BOM のインポート、脆弱性のミラーリング)が同じノードのワーカースレッドを飽和させ、リクエスト処理のレイテンシーが悪化し始めます。

API トラフィックだけを処理するインスタンスでは、[`dt.config.profile`](../../reference/configuration/properties.md#dtconfigprofile) で `web` プロファイルを有効にします。

```ini linenums="1"
dt.config.profile=web
```

このプロファイルを有効にしていないインスタンスは、デフォルトの動作のままバックグラウンドワーカーを実行します。

!!! note
    スケジューリング、脆弱性分析、通知などのバックグラウンド処理を進めるには、少なくとも 1 つのワーカーノードが稼働している必要があります。本番環境では、1 つのインスタンスの障害でバックグラウンド処理が完全に停止しないように、**少なくとも 2 つのワーカーノード**を実行してください。

### 例 {#example}

```yaml linenums="1"
services:
  web:
    image: ghcr.io/dependencytrack/hyades-apiserver
    environment:
      DT_CONFIG_PROFILE: "web"
      DT_DATASOURCE_URL: "jdbc:postgresql://postgres:5432/dtrack"
      DT_DATASOURCE_USERNAME: "dtrack"
      DT_DATASOURCE_PASSWORD: "dtrack"

  worker:
    image: ghcr.io/dependencytrack/hyades-apiserver
    environment:
      DT_DATASOURCE_URL: "jdbc:postgresql://postgres:5432/dtrack"
      DT_DATASOURCE_USERNAME: "dtrack"
      DT_DATASOURCE_PASSWORD: "dtrack"
```

2 つのグループは個別にスケールします。`web` はリクエスト量に基づいて、`worker` はバックグラウンド処理の滞留量に基づいてスケールします。

## バックグラウンド処理のスループットを上げる {#increase-background-throughput}

永続実行エンジンには、バックグラウンド処理のスループットを調整する 3 つの手段があり、それぞれ異なる症状に対処します。その背後にあるモデルについては、[同時実行制御](../../concepts/architecture/design/durable-execution.md#concurrency-control)を参照してください。

!!! warning "並行性を上げてもスループットが上がるとは限らない"
    Dependency-Track はスループットを重視しており、エンジンはデータベースとのやり取りのコストを分散するために(マイクロ)バッチ処理に大きく依存しています。ワークロードごとに異なる最適点を超えると、並行性を上げることでスループットが低下する場合があります。スレッドが同じデータベース接続、ロック、CPU を奪い合い、処理が分散することでバッチが小さくなるためです。`max-concurrency` を上げるのは、ワークロードの処理能力が不足していることがメトリクスで確認できた場合だけにし、変更のたびにスループットが改善したことを確認してください。

**ワーカーの並行性。** あるワークロードがそのワーカーを飽和させている(たとえば脆弱性分析)一方で、ほかのワークロードに余裕がある場合は、ワーカーノードでそのワーカーの `max-concurrency` を上げます。

```ini
dt.dex-engine.activity-worker.vuln-analysis.max-concurrency=20
```

ワーカーとそのデフォルト値の一覧については、[永続実行エンジンのリファレンス](../../reference/configuration/dex-engine.md#workers)を参照してください。

**キューの容量。** クラスター全体で取り込みが処理を上回っている場合(持続的な負荷のもとでキューの深さが際限なく増える場合)は、キューの容量を下げてバックプレッシャーをかけます。キューが容量に達すると、スケジューラーはタスクの作成を一時停止し、BOM をアップロードするクライアントにまでスロットリングを波及させます。

容量は、管理パネルの *Workflows > Task Queues* から、または REST API を使って実行時に変更できます。デフォルト値は[タスクキューのリファレンス](../../reference/configuration/dex-engine.md#task-queues)に記載されています。

**低レベルのエンジンチューニング。** 書き込みバッファーのフラッシュのレイテンシー、実行履歴キャッシュのミス、通知アウトボックスの遅延がメトリクスに表れている場合は、エンジンが公開しているさらに多くの調整項目を利用できます。[`dt.dex-engine.*`](../../reference/configuration/properties.md#dtdex-enginetask-event-bufferflush-interval-ms) と [`notification.outbox-relay.*`](../../reference/configuration/properties.md#dtnotificationoutbox-relaypoll-interval-ms) のプロパティを参照してください。

## ワーカーを水平スケールする {#scale-workers-horizontally}

垂直方向の調整項目をチューニングした後もアクティビティの滞留が増え続ける場合は、永続実行エンジンが提供する需要シグナルに基づいてワーカーインスタンスを水平スケールします。CPU やメモリーだけに基づいてスケールしないでください。アクティビティワーカーは I/O バウンド(データベース、レジストリの呼び出し、脆弱性データソース)で、ほとんどの時間を待機に費やすため、タスクがキューに溜まっていても CPU 使用率は低いままです。

エンジンは、このための Prometheus メトリクスを 3 つ公開しています。[Prometheus メトリクスのスクレイプを有効にする](configuring-observability.md#enabling-prometheus-metrics-scraping)と、管理サーバーがこれらのメトリクスを提供します。

| メトリクス | わかること | 用途 |
|---|---|---|
| `dt_dex_engine_activity_task_queue_backlog{queueName}` | キューごとの、スケジュール可能なアクティビティタスクのおおよその数。上限は 10000。 | 主要なスケールアップのトリガー。 |
| `dt_dex_engine_activity_task_queue_backlog_age_seconds{queueName}` | キューごとの、スケジュール可能なアクティビティタスクのうち最も古いものの経過時間。 | SLO に沿った補助的なトリガー。 |
| `dt_dex_engine_task_worker_concurrency_utilization{workerType,name}` | ワーカーの並行処理スロットのうち、現在使用中の割合(0–1)。 | スケールダウンの抑止条件。 |

滞留数がインスタンスあたりの目標値を超えたとき、または最も古いタスクの待機時間が SLO を超えたときにスケールアップします。スケールダウンは、すべてのインスタンスでワーカースロットの使用率が低い閾値を下回り続けている場合だけにします。

!!! note "インスタンスとキューをまたいで集約する"
    すべてのインスタンスが滞留数と経過時間のゲージを公開します。ほとんどのデプロイではすべてのアクティビティワーカーをまとめて実行するため、適切な HPA のシグナルは「いずれかのキューでスケールアップが必要」です。`max(...)`(`by` 句なし)で 1 つの値にまとめます。たとえば `max(dt_dex_engine_activity_task_queue_backlog)` のようにします。`by (queueName)` を追加するのは、ワーカーの種類を別々の Deployment に分割し、キューごとにスケールしたい場合だけです。

!!! note "滞留数はおおよその値"
    エンジンはクエリーのコストを抑えるため、キューごとの数を 10000 で打ち切ります。上限を超えると、値は 10000 で頭打ちになります。スケーリングの判断に使うには十分な精度です。

<!-- vale Google.Headings = NO -->
### KEDA の例 {#keda-example}
<!-- vale Google.Headings = YES -->

[KEDA](https://keda.sh) を使うと、これらのメトリクスに基づいて Deployment をスケールできます。次の `ScaledObject` はワーカーノード(`web` プロファイルなし)を対象とし、すべてのキューにわたる最悪の滞留数に基づいてスケールし、最悪の最古タスクの経過時間を補助的なトリガーとして使います。各クエリーでは、一時的な急増(1 回の大きな BOM のアップロード)で無駄なスケールの増減が起きないように、メトリクスを `avg_over_time(...[5m:30s])` で囲んでいます。

??? example "`ScaledObject` のマニフェスト"
    ```yaml linenums="1"
    apiVersion: keda.sh/v1alpha1
    kind: ScaledObject
    metadata:
      name: dependencytrack-worker
    spec:
      scaleTargetRef:
        name: dependencytrack-worker
      minReplicaCount: 2
      maxReplicaCount: 5
      triggers:
        - type: prometheus
          metadata:
            serverAddress: http://prometheus.monitoring:9090
            query: avg_over_time(max(dt_dex_engine_activity_task_queue_backlog)[5m:30s])
            threshold: "1000"
        - type: prometheus
          metadata:
            serverAddress: http://prometheus.monitoring:9090
            query: avg_over_time(max(dt_dex_engine_activity_task_queue_backlog_age_seconds)[5m:30s])
            threshold: "300"
    ```

## コネクションプールを一元化する {#pool-connections-centrally}

- **おおむね 5 インスタンスまで**(デフォルトのプールサイズ 30 の場合): インスタンスごとのプールで問題ありません。
- **それを超える場合:** PgBouncer などの一元的なプーラーに切り替え、ローカルのプールをオフにします。多数のインスタンスがそれぞれ独自のプールを維持すると、データベースの接続数が PostgreSQL の `max_connections` を超えるペースが、Postgres の垂直スケールで追いつけるペースよりも速くなります。

`max_connections` の計算については、[コンピューティングリソースとデータベースを用意する](deploying-to-production.md#provision-compute-and-database)で説明しています。

プールのプロパティについては、[データソース](../../reference/configuration/datasources.md#connection-pool-properties)を参照してください。PgBouncer のセットアップについては、[コネクションプーリングの集約](configuring-database.md#centralised-connection-pooling)を参照してください。

## 垂直スケールする {#scale-vertically}

大きな BOM によって GC の負荷が上がる場合は、インスタンスを追加する前にメモリーを追加します。並行性の設定に余裕があるにもかかわらずワーカーのスループットが頭打ちになる場合は、CPU を追加します。

JVM のデフォルト値を置き換えずに上書きするには、`EXTRA_JAVA_OPTIONS` を拡張します。たとえば、レイテンシーの影響を受けやすいフロントエンドのトラフィック向けに GC の停止時間の目標を厳しくするには、次のようにします。

```ini
EXTRA_JAVA_OPTIONS="-XX:MaxGCPauseMillis=100"
```

同梱されている JVM のデフォルト値とその意味については、[JVM オプション](../../reference/configuration/application.md#jvm-options) を参照してください。

## エンジンのデータベースを分離する {#isolate-the-engine-database}

永続実行エンジンのキューのバキュームや WAL のアクティビティが、I/O や autovacuum の帯域をめぐってメインデータベースと競合し始めたら、エンジンを別の PostgreSQL サーバーに向けます。デフォルトでは、エンジンはメインの Dependency-Track データベースを共有します([`dt.dex-engine.datasource.name`](../../reference/configuration/properties.md#dtdex-enginedatasourcename)`=default`)。

```ini
# Configure a separate data source for the engine.
dt.datasource.engine.url=jdbc:postgresql://engine-postgres:5432/engine
dt.datasource.engine.username=engine
dt.datasource.engine.password=engine
dt.datasource.engine.pool.enabled=true
dt.datasource.engine.pool.max-size=10

# Point the engine at the separate data source.
dt.dex-engine.datasource.name=engine
```

エンジンは独自のスキーマを管理しており、メインのデータベースクラスターを共有する必要はありません。データソースの設定の詳細については、[データソース](../../reference/configuration/datasources.md)を参照してください。

## データベースをチューニングする {#tune-the-database}

大規模な環境では、Dependency-Track 自体のチューニングよりも、PostgreSQL のチューニング(autovacuum、WAL の圧縮、`shared_buffers` などの設定)のほうが重要になることがよくあります。推奨事項については、[データベースを設定する](configuring-database.md#advanced-tuning)を参照してください。
