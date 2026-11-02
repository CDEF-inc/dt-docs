# データベースを設定する

このガイドでは、Dependency-Track 用の PostgreSQL データベースの選定、デプロイ、チューニングについて説明します。技術仕様(バージョン要件、必要な拡張機能、チューニングパラメーター)については、[データベースのリファレンス](../../reference/configuration/database.md)を参照してください。

## ホスティング方法を選ぶ {#choosing-a-hosting-solution}

利用できるリソース、個人の好み、組織のポリシーに応じて、マネージドとセルフホストのどちらかを選ぶ必要があります。

### マネージドサービス {#managed-solutions}

PostgreSQL の公式 Web サイトには、[よく知られた商用ホスティングプロバイダーの一覧][list of well-known commercial hosting providers]が掲載されています。

よく選ばれるサービスには次のものがあります。

* [Amazon RDS for PostgreSQL](https://aws.amazon.com/rds/postgresql/)
* [Aiven for PostgreSQL](https://aiven.io/postgresql)
* [Azure Database for PostgreSQL](https://azure.microsoft.com/en-us/products/postgresql/)
* [Google Cloud SQL for PostgreSQL](https://cloud.google.com/sql/docs/postgres/)

クラウドサービスに対するテストは積極的には行っていません。ただし、経験則として、「素の」PostgreSQL やその拡張(たとえば [Neon] や [Timescale])を提供するサービスであれば、Dependency-Track で問題なく動作するはずです。

大幅に改変された PostgreSQL をベースとするプラットフォームや、[CockroachDB] や [YugabyteDB] のような完全な再実装については、必ずしもそうとは限りません。こうしたサービスは、より高いスケーラビリティを実現するために一定のトレードオフを行っており、Dependency-Track が依存する機能に影響する可能性があります。

#### Google Cloud SQL {#google-cloud-sql}

[Cloud SQL ソケットファクトリー][cloud-sql-jdbc]を通じて接続するには(たとえば IAM データベース認証を使う場合)、ソケットファクトリーを API サーバーに追加します。コンテナーイメージにはソケットファクトリーは含まれていません。

1. [ソケットファクトリーの JAR を依存関係込みでビルドします][cloud-sql-build]。
2. それを `/opt/owasp/dependency-track/lib-external/` にマウントします。API サーバーはこのディレクトリ内のすべての JAR を読み込みます。
3. データソース URL をインスタンスに設定します。

```yaml linenums="1" title="docker-compose.yaml"
services:
  apiserver:
    image: dependencytrack/apiserver
    environment:
      DT_DATASOURCE_URL: "jdbc:postgresql:///dtrack?cloudSqlInstance=<INSTANCE_CONNECTION_NAME>&socketFactory=com.google.cloud.sql.postgres.SocketFactory"
    volumes:
      - "./postgres-socket-factory-jar-with-dependencies.jar:/opt/owasp/dependency-track/lib-external/postgres-socket-factory.jar:ro"
```

### セルフホスト {#self-hosting}

#### ベアメタル / Docker {#bare-metal-docker}

Docker でデプロイする場合は、公式の [`postgres`](https://hub.docker.com/_/postgres) イメージを使います。

!!! warning
    `latest` タグは**使わないでください**。知らないうちにメジャーバージョンのアップグレードが行われ、最終的にデータベースが壊れるおそれがあります。タグは少なくともメジャーバージョン(たとえば `16`)に固定し、できればマイナーバージョン(たとえば `16.2`)に固定します。アップグレードの手順については、[アップグレード](#upgrades)を参照してください。

ベアメタルでデプロイする場合は、通常、ディストリビューションのパッケージリポジトリから PostgreSQL をインストールするのが最善です。たとえば、次を参照してください。

* [PostgreSQL instructions for Debian](https://wiki.debian.org/PostgreSql)
* [Install and configure PostgreSQL on Ubuntu](https://ubuntu.com/server/docs/databases-postgresql)
* [Using PostgreSQL with Red Hat Enterprise Linux](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html/configuring_and_using_database_servers/using-postgresql_configuring-and-using-database-servers)

Dependency-Track のインストールを最大限に活用するには、PostgreSQL をアプリケーションのコンテナーとは別のマシンで実行することをお勧めします。PostgreSQL が他のアプリケーションの影響を受けずに、マシン全体のリソースを使えるようにするためです。

小規模で重要度の低いデプロイでは、すべてを 1 台のマシンで実行してもまったく問題ありません。

**ストレージには高速なディスクを使ってください**。理想は NVME で、少なくとも SSD を使います。ワーキングセット全体がメモリに収まらない限り、PostgreSQL はディスクへのランダムアクセスを行う必要があり、HDD ではシーク遅延のために低速になります。ローカルディスクは最も予測しやすいパフォーマンスを発揮します。ネットワーク接続ストレージも、保証された IOPS をプロビジョニングし、持続的な負荷でスループットを制限するティアを避ければ、十分に機能します。

#### アップグレード {#upgrades}

[公式のアップグレードガイド][official upgrading guide]に従ってください。実行している PostgreSQL のバージョンに対応するバージョンのドキュメントを選択してください。

!!! warning
    基盤となるデータストレージ形式に破壊的変更が含まれる可能性があるため、**メジャーバージョンのアップグレードには通常、バックアップと復元のサイクルが必要**であることに注意してください。マイナーバージョンのアップグレードは、通常はローリング方式で安全に実行できます。

#### Kubernetes {#kubernetes}

自分が何をしているのかを*本当に*理解しているのでない限り、Kubernetes 上で PostgreSQL を実行することは基本的に**お勧めしません**。[Postgres Operator] のような大掛かりな仕組みを扱うのは、気軽にできることではありません。

自分が何をしているのかを理解しているのであれば、こちらからの助言はまったく必要ないでしょう。

## 基本的なチューニング {#basic-tuning}

PostgreSQL のデフォルト設定は*きわめて*保守的であることに注意してください。この設定は、最小限のハードウェアでも PostgreSQL を使えるようにすることを目的としています。テストには最適ですが、本番環境ではパフォーマンスを大きく損なう可能性があります。特定の環境に合わせて調整しなければ、本来得られるパフォーマンスをほぼ確実に取りこぼすことになります。

幸いにもプロのデータベース管理者の協力を得られる場合は、助けを求めてください。組織のベストプラクティスを理解しており、Dependency-Track に合わせた調整を手引きしてくれるでしょう。

そうでない場合は、[PGTune] を心からお勧めします。システムに関する基本的な情報を少し与えるだけで、妥当なベースラインの設定を提示してくれます。*DB Type* オプションでは `Online transaction processing system` を選択します。

![PGTune の出力例](../../assets/images/guides/administration/configuring-database/pgtune-output.png)

`postgresql.conf` は通常、`/var/lib/postgresql/data/postgresql.conf` にあります。これらの設定のほとんどは、アプリケーションの再起動が必要です。

Docker Compose 環境では、代わりにコマンドラインフラグで目的の設定を適用することもできます。たとえば、次のようにします。

```yaml
services:
  postgres:
    image: postgres:17
    command: >-
        -c 'shared_buffers=2GB'
        -c 'effective_cache_size=6GB'
```

## 高度なチューニング {#advanced-tuning}

大規模なデプロイでは、基本的な設定だけではデータベースのパフォーマンスが低下する状況にいずれ直面することがあります。多くの場合、高度な設定を調整すればそうした問題を解決できます。ただし、どの設定を調整すべきかを見極めること自体が難題です。

このような状況に陥った場合は、データベースの監視を必ず設定してください。高度な設定オプションをやみくもに変更すると、効果よりも害のほうが大きくなる可能性があります。

以下に、大規模なデプロイでの観察に基づいて調整する意味があるオプションをいくつか示します。パラメーターの仕様については、[データベースのリファレンス](../../reference/configuration/database.md#tuning-parameters)を参照してください。

!!! note
    PostgreSQL の設定やチューニングについて、他の人の役に立ちそうなヒントがほかにもありますか? ぜひドキュメントに掲載したいので、PR を作成してください。

### `autovacuum_vacuum_scale_factor` {#autovacuum_vacuum_scale_factor}

デフォルト値では、更新の多い大きなテーブルで [autovacuum][Autovacuum] の開始が遅くなりすぎ、実行時間が長くなります。スケールファクターを小さくすると autovacuum がより頻繁に実行され、1 回あたりの実行にかかる時間が短くなります。

`COMPONENT` テーブルは、挿入、更新、削除がきわめて頻繁に行われます。そのため、PostgreSQL がクリーンアップする必要のあるデッドタプルが大量に発生します。autovacuum は [`ANALYZE`](https://www.postgresql.org/docs/current/sql-analyze.html) も実行するため、バキュームが遅いと、クエリープランナーが非効率な実行計画を選択する原因になります。

```sql
ALTER TABLE "COMPONENT" SET (AUTOVACUUM_VACUUM_SCALE_FACTOR = 0.02);
```

### `default_toast_compression` {#default_toast_compression}

`lz4` 圧縮は `pglz` より高速かつ効率的ですが、圧縮率はわずかに劣ります。

ストレージ容量よりも CPU 使用率がボトルネックになりやすい場合は、lz4 への切り替えを検討してください。

```sql
ALTER SYSTEM SET (DEFAULT_TOAST_COMPRESSION = 'lz4');
```

### `wal_compression` {#wal_compression}

WAL 圧縮を有効にすると、書き込みの多いシステムで I/O が大幅に減少します。CPU 使用率がわずかに増えるコストを払う価値は十分にあります。

インスタンスが大量の BOM を高頻度でインポートしている場合、WAL はすぐにいっぱいになり、I/O がボトルネックになります。これは、SSD や NVME ストレージではなく HDD を使っている場合に特に当てはまります。

```sql
ALTER SYSTEM SET (WAL_COMPRESSION = 'zstd');
```

### `jit` {#jit}

PostgreSQL のジャストインタイム(JIT)コンパイルは、実行時間が長く CPU に負荷のかかる分析クエリーを高速化できます。一方で、Dependency-Track のワークロードの大半を占める、短くレイテンシーに敏感なクエリーには悪影響を与える傾向があります。プランナーがクエリーのコストを過大に見積もると、マシンコードをコンパイルし、そのオーバーヘッドが節約できる時間を桁違いに上回ることがあります。

Dependency-Track は、JIT が明らかに有害であると判明した個々のクエリーについては、すでに JIT を無効にしています。JIT をグローバルに無効にすると、通常はより安定したパフォーマンスが得られます。この最適化は広く行われているため、PostgreSQL 19 ではデフォルトが `off` に変更されています。

```sql
ALTER SYSTEM SET jit = off;
```

## コネクションプーリングの集約 {#centralised-connection-pooling}

大規模なデプロイ(つまり、インスタンスが 5 つを超える場合)では、各インスタンスがそれぞれコネクションプールを維持することが望ましくない場合があります。その場合は、[PgBouncer] のような集約型のコネクションプールを使えます。

!!! warning
    集約型のコネクションプーラーを使う場合は、[`dt.datasource.<name>.pool.enabled=false`](../../reference/configuration/properties.md#dtdatasourcepoolenabled) を使って、すべてのデータソースでローカルのコネクションプーリングを無効にする**必要があります**。

### 制約 {#constraints}

先に進む前に、次の制約に注意してください。

* サポートされるプーリングモードは `session` と `transaction` だけです。`transaction` を推奨します。
* プーリングモード `transaction` を使う場合、[Init tasks](../../reference/configuration/init-tasks.md) はコネクションプーラーを経由せずにデータベースに直接接続する**必要があります**。Init tasks は、セッションレベルの PostgreSQL アドバイザリーロックを使ってインスタンス間で調整しますが、このロックは `transaction` プーリングモードではサポートされていません。PostgreSQL に直接接続する別のデータソースを経由させるか、専用のコンテナーで実行するか、その両方を設定してください。

### 例 {#example}

```yaml linenums="1"
services:
  postgres:
    image: postgres
    environment:
      POSTGRES_DB: "dtrack"
      POSTGRES_USER: "dtrack"
      POSTGRES_PASSWORD: "dtrack"

  pgbouncer:
    image: bitnami/pgbouncer
    environment:
      POSTGRESQL_HOST: "postgres"
      POSTGRESQL_PORT: "5432"
      POSTGRESQL_USERNAME: "dtrack"
      POSTGRESQL_PASSWORD: "dtrack"
      POSTGRESQL_DATABASE: "dtrack"
      PGBOUNCER_DATABASE: "dtrack"
      PGBOUNCER_PORT: "6432"
      PGBOUNCER_POOL_MODE: "transaction"
      PGBOUNCER_DEFAULT_POOL_SIZE: "30"

  apiserver:
    image: ghcr.io/dependencytrack/hyades-apiserver
    environment:
      # Configure the default data source:
      # - Points to PgBouncer, NOT Postgres directly.
      # - Pooling is DISABLED.
      DT_DATASOURCE_URL: "jdbc:postgresql://pgbouncer:6432/dtrack"
      DT_DATASOURCE_USERNAME: "dtrack"
      DT_DATASOURCE_PASSWORD: "dtrack"
      DT_DATASOURCE_POOL_ENABLED: "false"
      # Configure the data source for initialisation tasks:
      # - Points to Postgres directly, NOT PgBouncer.
      # - Pooling is DISABLED.
      DT_DATASOURCE_INIT_URL: "jdbc:postgresql://postgres:5432/dtrack"
      DT_DATASOURCE_INIT_USERNAME: "dtrack"
      DT_DATASOURCE_INIT_PASSWORD: "dtrack"
      DT_DATASOURCE_INIT_POOL_ENABLED: "false"
      # Configure initialisation tasks to use the above data source.
      DT_INIT_TASKS_DATASOURCE_NAME: "init"
```

[Autovacuum]: https://www.postgresql.org/docs/current/routine-vacuuming.html
[CockroachDB]: https://www.cockroachlabs.com/
[cloud-sql-build]: https://github.com/GoogleCloudPlatform/cloud-sql-jdbc-socket-factory#building-the-drivers
[cloud-sql-jdbc]: https://github.com/GoogleCloudPlatform/cloud-sql-jdbc-socket-factory/blob/main/docs/jdbc.md
[Neon]: https://neon.tech/
[PGTune]: https://pgtune.leopard.in.ua/
[PgBouncer]: https://www.pgbouncer.org/
[Postgres Operator]: https://github.com/zalando/postgres-operator
[Timescale]: https://www.timescale.com/
[YugabyteDB]: https://www.yugabyte.com/
[list of well-known commercial hosting providers]: https://www.postgresql.org/support/professional_hosting/
[official upgrading guide]: https://www.postgresql.org/docs/current/upgrading.html
