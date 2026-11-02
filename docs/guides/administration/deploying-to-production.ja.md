# 本番環境にデプロイする

このガイドでは、実際のワークロードで Dependency-Track を運用するための基本的な構成を説明します。各コンポーネントの組み合わせ方の概要については、[デプロイのトポロジー](../../concepts/architecture/deployment.md)を参照してください。負荷に応じたデプロイのチューニングについては、[スケーリング](scaling.md)を参照してください。Kubernetes 固有のガイダンスについては、[Kubernetes にデプロイする](deploying-to-kubernetes.md)を参照してください。

## コンテナーイメージのバージョンを固定する {#pin-container-image-versions}

すべての Dependency-Track コンテナーを、完全な `X.Y.Z` 形式のリリースタグ(またはイメージダイジェスト)に固定します。本番環境にスナップショットタグや `latest` タグをデプロイしないでください。利用できるレジストリ、イメージの座標、タグの規則については、[コンテナーイメージ](../../reference/container-images.md)を参照してください。

## コンピューティングリソースとデータベースを用意する {#provision-compute-and-database}

### API サーバーのインスタンス {#api-server-instances}

インスタンスあたりの妥当な出発点は **2 GB のメモリーと 4 つの CPU コア**です。そこから、観測した負荷に基づいてスケールアップします。

知っておくべき下限が 2 つあります。

- **メモリーが 1 GB 未満**の場合、インスタンスが意味のある負荷に耐えられる可能性は低くなります。
- **CPU コアが 2 つ未満**の場合、システムが前提とする高い並行性を活かせません(バックグラウンドワーカー、永続実行エンジン、リクエスト処理のすべてが同じスレッドを奪い合います)。

正確なサイジングはワークロードの形態によって決まります。同時に利用するフロントエンドのユーザー数、ポートフォリオ内のプロジェクト数、BOM のアップロード頻度などです。利用パターンは、調達のみのデプロイ、CI/CD 主導のデプロイ、混在したデプロイで大きく異なるため、スケーリングする前に観測してください。実際の負荷を示すメトリクスについては、[オブザーバビリティを設定する](configuring-observability.md)を参照してください。

!!! warning "JVM ヒープはコンテナーのメモリーに応じて拡大する"
    メモリーを追加すると、JVM ヒープの上限(デフォルトはコンテナーのメモリーの 80%)が上がります。過剰にリソースを割り当てる前に、大きなヒープが効果を上げていることを `top` や `docker stats` ではなく Prometheus のヒープメトリクスで確認してください。背後の動作については [JVM オプション](../../reference/configuration/application.md#jvm-options)を参照してください。

### データベース {#database}

Dependency-Track は PostgreSQL 上で動作し、API サーバーよりも先に PostgreSQL がボトルネックになります。マネージドサービス、または監視と自動バックアップを備えたセルフホストのインスタンスを使い、メジャーバージョンを固定してください。

妥当な出発点は **8 GB のメモリーと 4 つの CPU コア**です。評価用のワークロードであっても、4 GB と 2 コアを下回らないようにしてください。メモリーの主な消費元は `shared_buffers`(通常は RAM の約 25%)と接続ごとの作業メモリー(`work_mem` × プールサイズの合計)であるため、メモリーの負荷はデータ量とクラスターの規模の両方に応じて高まります。

データベースは専用のホストで実行してください。PostgreSQL を API サーバーのインスタンスと同じホストに配置すると、両者が同じ CPU、メモリー、I/O を奪い合い、その競合が負荷時の予測できないレイテンシーとして現れます。

高速なディスクを使ってください。理想は NVME ですが、少なくとも SSD を使います。ワーキングセットがメモリーに収まらなくなると、PostgreSQL はランダムなディスクアクセスに頼ることになり、HDD はこれをうまく処理できません。ストレージに関するガイダンスについては、[データベースを設定する](configuring-database.md)を参照してください。

データベースのホストをサイジングする際は、インスタンスごとのコネクションプールを考慮してください。PostgreSQL の `max_connections` は、クラスター全体のすべてのプールの合計に、マイグレーション、バックアップ、管理者のセッション用の余裕を加えた値をまかなう必要があります。

```text
max_connections >= (instance_count × dt.datasource.pool.max-size) + headroom
```

[`dt.datasource.pool.max-size`](../../reference/configuration/properties.md#dtdatasourcepoolmax-size) のデフォルトは 30 です。

ホスティングの選択肢、チューニング、アップグレードのガイダンスについては、[データベースを設定する](configuring-database.md)を参照してください。サポートされているバージョンと必要な拡張機能については、[データベースのリファレンス](../../reference/configuration/database.md)を参照してください。

## 複数のインスタンスを実行する {#run-more-than-one-instance}

単一障害点を避け、ローリング再起動を可能にするために、同じデータベースに対して少なくとも 2 つのインスタンスを実行してください。インスタンスは PostgreSQL を通じてのみ連携し、デプロイにクラスタリングプロトコルやピアツーピアのネットワークは関与しません。このモデルについては[協調](../../concepts/architecture/deployment.md#coordination)を、インスタンスが停止した場合の動作については[インスタンスの障害からの復旧](../../concepts/architecture/deployment.md#recovery-from-instance-failure)を参照してください。

すべてのインスタンスはファイルストレージを共有する必要があります。デフォルトの `local` プロバイダーは共有の永続ボリューム(NFS など)で動作し、`s3` プロバイダーは共有ボリュームが現実的でない環境で動作します。[ファイルストレージ](../../reference/configuration/file-storage.md)を参照してください。

## シークレットをコンテナーの外で管理する {#manage-secrets-outside-the-container}

2 種類のシークレットを別々に管理します。

- **インフラストラクチャのシークレット**(データベースのパスワード、LDAP のバインドパスワード)は起動時に読み込まれます。平文の環境変数として渡すのではなく、ファイルとしてマウントし、`${file::/path/to/file}` で参照してください。[ファイルから値を読み込む](../../reference/configuration/application.md#loading-values-from-files)を参照してください。
- **連携用のシークレット**(Jira、Snyk、Trivy、OSS Index などの API トークン)は、Dependency-Track の実行時のシークレットストアに保存されます。サポートされているバックエンドについては、[シークレット管理を設定する](configuring-secret-management.md)を参照してください。

データベースのシークレットプロバイダーはエンベロープ暗号化を使います。各シークレットは固有のデータ暗号化鍵(DEK)を持ち、鍵暗号化鍵(KEK)が DEK を保護します。デフォルトでは、各インスタンスは初回起動時に KEK のキーセットファイルをディスク上に生成します。クラスター内のすべてのインスタンスは同じ KEK を共有する必要があり、不一致を検出すると起動を拒否します。キーセットファイルを一度だけ用意してすべてのインスタンスにマウントするか、環境変数で KEK を直接指定してください。両方の方法については、[シークレット管理を設定する](configuring-secret-management.md#key-management)を参照してください。

## 認証を設定する {#configure-authentication}

Dependency-Track を ID プロバイダーに接続します。ローカルの管理対象ユーザーは評価専用です。

- OIDC プロバイダー(Keycloak、Entra ID、Google など)については、[OpenID Connect を設定する](configuring-oidc.md)を参照してください。
- LDAP と Active Directory については、[LDAP を設定する](configuring-ldap.md)を参照してください。

## API サーバーの前段に TLS を置く {#front-the-api-server-with-tls}

TLS は API サーバー自体ではなく、リバースプロキシまたは Ingress コントローラーで処理してください。監査ログと通知のリンクが公開 URL に解決されるように、`X-Forwarded-Proto` と `X-Forwarded-For` を転送します。

各インスタンスは 2 つのポートで待ち受けます。公開 REST API 用の `8080` と、ヘルスチェックとメトリクス用の `9000` です。ユーザー向けのトラフィックは `8080` に、プローブとメトリクスのスクレイパーは `9000` に向けてください。ヘルスエンドポイントの仕様については、[オブザーバビリティを設定する](configuring-observability.md#configuring-kubernetes-health-probes)を参照してください。

## オブザーバビリティを設定する {#set-up-observability}

ポート `9000` の `/metrics` から Prometheus のメトリクスをスクレイプし、同じポートの `/health/live`、`/health/ready`、`/health/started` に対して liveness、readiness、startup の各プローブを設定します。最初の実際のワークロードが届く前に両方を接続してください。これらがなければ、キャパシティに関する判断は推測にすぎません。完全な設定手順については、[オブザーバビリティを設定する](configuring-observability.md)を参照してください。

## バックアップとアップグレードを計画する {#plan-for-backup-and-upgrade}

本番稼働の前に、2 つの手順を決めてリハーサルしておきます。

- **バックアップと復元。** Dependency-Track が永続化するものはすべて、標準的な PostgreSQL のバックアップでカバーできます。何をバックアップするか、復元が実行中のワークフローにどう影響するか、復元訓練をどう実施するかについては、[バックアップと復元](backing-up.md)を参照してください。
- **アップグレード。** リリースノートで許可されている場合、新しいバージョンはダウンタイムなしでロールアウトできます。手順と、代わりに全停止のメンテナンスウィンドウが必要になる条件については、[稼働中のインスタンスをアップグレードする](upgrading-instances.md)を参照してください。

## デプロイを検証する {#verify-the-deployment}

デプロイをユーザーに公開する前に、次のことを行います。

1. すべてのインスタンスで `/health/ready` が `UP` を返すことを確認します。
2. 設定した ID プロバイダーを使ってサインインします。
3. サンプルの BOM をアップロードし、脆弱性分析が完了することを確認します。一連の流れは[クイックスタート](../../tutorials/quickstart.md)で説明しています。
4. メトリクスがスクレイパーに届き、ヘルスプローブがロードバランサーを通過することを確認します。
