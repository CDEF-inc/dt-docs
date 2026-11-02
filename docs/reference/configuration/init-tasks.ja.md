# 初期化タスク

初期化タスクは、API サーバーが起動時、メインサーバーがトラフィックの処理を始める前に実行する 1 回限りの処理です。データベーススキーマを準備し、デフォルトのオブジェクトを投入し、永続実行エンジンを一貫した状態にします。

## ライフサイクル {#lifecycle}

初期化タスクは、HTTP リスナーが起動する前、かつバックグラウンドワーカーが初期化される前に実行されます。初期化タスクは起動をブロックします。いずれかのタスクが失敗すると JVM が終了し、コンテナーはトラフィックの処理を開始しません。

管理サーバーは初期化タスクの実行前に起動し、[起動用のヘルスエンドポイント](../../guides/administration/configuring-observability.md#configuring-kubernetes-health-probes)を `/health/started` で公開します。このエンドポイントは、実行中のタスクごとの状態(`STARTED`、`COMPLETED`、`FAILED`)を報告します。

デフォルトでは、初期化タスクはすべての API サーバーコンテナーで実行されます。インスタンス間で協調するため、実行側はセッションレベルの PostgreSQL [アドバイザリーロック][advisory lock]を取得します。これにより、各タスクを一度に実行するコンテナーは 1 つだけになります。残りのコンテナーはロックを待ち、その後、実行すべき処理が残っていないことを確認します。

!!! warning
    セッションレベルのアドバイザリーロックは、`transaction` プーリングモードの PgBouncer と互換性がありません。トランザクションモードのコネクションプーラーを使う場合は、PostgreSQL に直接接続する別の[初期化用データソース](#data-source)を設定してください。

## タスク {#tasks}

| タスク | 目的 | 有効化プロパティ |
|------|---------|-----------------|
| データベースのマイグレーション | Dependency-Track のスキーマに対して [Flyway](database.md#schema-migrations) のマイグレーションを実行します。必要な[拡張機能](database.md#extensions)を作成します。 | [`dt.init-task.database-migration.enabled`](properties.md#dtinit-taskdatabase-migrationenabled) |
| データベースのパーティションのメンテナンス | [時系列メトリクス](../../concepts/time-series-metrics.md)に必要な[テーブルパーティション][table partitions]を作成します。 | [`dt.init-task.database-partition-maintenance.enabled`](properties.md#dtinit-taskdatabase-partition-maintenanceenabled) |
| データベースの初期データ投入 | デフォルトの権限、チーム、ユーザー、ライセンス、ライセンスグループ、パッケージリポジトリ、設定プロパティを投入します。べき等です。ビルド識別子が変わっていない場合、以降の起動ではスキップされます。 | [`dt.init-task.database-seeding.enabled`](properties.md#dtinit-taskdatabase-seedingenabled) |
| Dex エンジンのデータベースのマイグレーション | [永続実行エンジン](dex-engine.md)のスキーマのマイグレーションを実行します。 | [`dt.init-task.dex-engine-database-migration.enabled`](properties.md#dtinit-taskdex-engine-database-migrationenabled) |

タスクごとの有効化プロパティは、[`dt.init-tasks.enabled`](properties.md#dtinit-tasksenabled) が `true` の場合にのみ有効になります。

## データソース {#data-source}

デフォルトでは、初期化タスクは `default` [データソース](datasources.md)を使います。[`dt.init-tasks.datasource.name`](properties.md#dtinit-tasksdatasourcename) でこれを上書きすると、別のコネクションプールを経由させることができます。

最もよくある理由は、`transaction` モードの PgBouncer によるコネクションプーリングの集約です。この構成では、初期化タスクはプーラーを経由せずに PostgreSQL に直接接続する必要があります。デフォルトのデータソースは PgBouncer を経由して接続し、初期化用データソースは PostgreSQL に直接接続するため、セッションレベルのアドバイザリーロックを引き続き使用できます。例については、[コネクションプーリングの集約](../../guides/administration/configuring-database.md#centralised-connection-pooling)を参照してください。

初期化用データソースが初期化タスク専用の場合は、[`dt.init-tasks.datasource.close-after-completion`](properties.md#dtinit-tasksdatasourceclose-after-completion) を `true` に設定してください。タスクが完了すると API サーバーはコネクションプールを閉じ、その接続を解放します。

## 初期化専用コンテナー {#init-only-containers}

[`dt.init-tasks.exit-after-completion`](properties.md#dtinit-tasksexit-after-completion) を `true` に設定すると、初期化タスクが成功した時点で、メインサーバーを起動せずに JVM がステータス `0` で終了します。これにより、短時間だけ動作するコンテナーが初期化タスクを実行して終了し、その後に長時間稼働する API サーバーコンテナーが起動する、専用の初期化コンテナーのパターンを実現できます。

このパターンでは、長時間稼働するコンテナーで [`dt.init-tasks.enabled`](properties.md#dtinit-tasksenabled) を `false` に設定し、起動時に初期化タスクをスキップします。

## 設定 {#configuration}

* [`dt.init-tasks.enabled`](properties.md#dtinit-tasksenabled)
* [`dt.init-tasks.datasource.name`](properties.md#dtinit-tasksdatasourcename)
* [`dt.init-tasks.datasource.close-after-completion`](properties.md#dtinit-tasksdatasourceclose-after-completion)
* [`dt.init-tasks.exit-after-completion`](properties.md#dtinit-tasksexit-after-completion)
* [`dt.init-task.database-migration.enabled`](properties.md#dtinit-taskdatabase-migrationenabled)
* [`dt.init-task.database-partition-maintenance.enabled`](properties.md#dtinit-taskdatabase-partition-maintenanceenabled)
* [`dt.init-task.database-seeding.enabled`](properties.md#dtinit-taskdatabase-seedingenabled)
* [`dt.init-task.dex-engine-database-migration.enabled`](properties.md#dtinit-taskdex-engine-database-migrationenabled)

[advisory lock]: https://www.postgresql.org/docs/current/explicit-locking.html#ADVISORY-LOCKS
[table partitions]: https://www.postgresql.org/docs/current/ddl-partitioning.html
