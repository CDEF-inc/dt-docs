# データソース

データソースは、データベース接続を取得するための論理的なオブジェクトです。

## プロパティの形式 {#property-format}

データソースは、次の形式のプロパティで設定します。

```ini
dt.datasource.<name>.<property>=<value>
```

利用できるプロパティと、それに対応する環境変数については、[設定リファレンス][configuration reference]を参照してください。

!!! tip
    `<name>` を省略すると `default` とみなされます。そのため、`dt.datasource.url` と `dt.datasource.default.url` は同じものとして扱われます。

`default` データソースは*必須*です。REST API と、バックグラウンド処理の大部分を担います。

一部の機能では、データベースの接続情報の代わりに*データソース名*を指定でき、専用のコネクションプールを使えます。たとえば、[*database* シークレット管理プロバイダー](../../guides/administration/configuring-secret-management.md#database)では、[`dt.secret-management.database.datasource.name`](properties.md#dtsecret-managementdatabasedatasourcename) で指定します。

??? example "複数のデータソース"

    ```ini linenums="1"
    # Configure the default data source
    dt.datasource.url=jdbc:postgresql://localhost:5432/dtrack
    dt.datasource.username=dtrack
    dt.datasource.password=dtrack
    dt.datasource.pool.enabled=true
    dt.datasource.pool.max-size=20

    # Configure the secret management data source
    dt.datasource.secretmgt.url=jdbc:postgresql://localhost:5432/dtrack
    dt.datasource.secretmgt.username=secrets
    dt.datasource.secretmgt.password=secrets
    dt.datasource.secretmgt.pool.enabled=true
    dt.datasource.secretmgt.pool.max-size=5

    # Configure secret management to use separate data source
    dt.secret-management.provider=database
    dt.secret-management.database.datasource.name=secretmgt
    ```

!!! note
    データソースは初めて使われたときにインスタンス化されます。データソースはいくつでも設定できますが、機能から使われない限り作成されません。

## 権限 {#privileges}

`default` データソースに設定するユーザーには、Dependency-Track のスキーマに対して DDL を実行する権限が必要です。API サーバーは通常の運用中に DDL を発行します。

* 起動時に、`default` データソースを使うように設定された[初期化タスク](init-tasks.md)を実行するとき(スキーマのマイグレーション、拡張機能の作成、パーティションのセットアップ、初期データの投入)。
* 実行時に、[時系列メトリクスの保持](../../concepts/time-series-metrics.md#daily-partitions-and-bounded-retention)を管理するために[テーブルパーティション][table partitions]を作成・削除するとき。

!!! warning
    `default` データソースに権限のないユーザーを設定することはサポートされていません。`SELECT`、`INSERT`、`UPDATE`、`DELETE` に制限されたユーザーでは、起動に成功した後でも実行時にエラーが発生します。

ユーザーにデータベースの所有権を付与するか、データベース内の Dependency-Track スキーマの所有権を付与してください。

## コネクションプールのプロパティ {#connection-pool-properties}

次のプロパティで、データソースごとのローカルなコネクションプーリングを制御します。

* [`dt.datasource.<name>.pool.enabled`](properties.md#dtdatasourcepoolenabled)
* [`dt.datasource.<name>.url`](properties.md#dtdatasourceurl)
* [`dt.datasource.<name>.username`](properties.md#dtdatasourceusername)
* [`dt.datasource.<name>.password`](properties.md#dtdatasourcepassword)
* [`dt.datasource.<name>.password-file`](properties.md#dtdatasourcepassword-file)
* [`dt.datasource.<name>.pool.max-size`](properties.md#dtdatasourcepoolmax-size)
* [`dt.datasource.<name>.pool.min-idle`](properties.md#dtdatasourcepoolmin-idle)
* [`dt.datasource.<name>.pool.max-lifetime-ms`](properties.md#dtdatasourcepoolmax-lifetime-ms)
* [`dt.datasource.<name>.pool.idle-timeout-ms`](properties.md#dtdatasourcepoolidle-timeout-ms)

複数のインスタンスをデプロイする場合、すべてのプールの接続数の合計が PostgreSQL の [`max_connections`](https://postgresqlco.nf/doc/en/param/max_connections/) の上限(デフォルト: 100)を超えてはいけません。

PgBouncer によるコネクションプーリングの集約については、[データベース設定ガイド](../../guides/administration/configuring-database.md#centralised-connection-pooling)を参照してください。

[configuration reference]: database.md
[table partitions]: https://www.postgresql.org/docs/current/ddl-partitioning.html
