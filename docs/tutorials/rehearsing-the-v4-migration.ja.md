# v4 から v5 への移行をリハーサルする

このチュートリアルでは、既存の v4 デプロイを読み取り専用のソースとして使い、使い捨ての v5 スタックに対して v4 から v5 への移行をリハーサルします。最後には、実際のデータが投入され、本番環境から安全に切り離された、動作する v5 インスタンスができあがります。

実際の切り替え手順は [v4 から v5 への移行ガイド](../guides/administration/migrating-from-v4.md)にあります。このチュートリアルでは同じワークフローをたどり、本番の実行前に接続性、データ固有の問題、情報が失われる変換を洗い出します。

!!! warning "リハーサル中は v4 への書き込みを止める"

    移行ツールは v4 に書き込みませんが、ソースのロックも取得しません。抽出中に v4 への書き込みが同時に行われると抽出結果に不整合が生じ、互いに参照し合う行がサンドボックス内で食い違った状態になることがあります。リハーサルでは、再現性の高い順に次の 3 つの選択肢があります。

    1. **抽出中は v4 の API サーバーを停止する**。本番の切り替えと同じ方法です。
    2. **稼働中のインスタンスではなく、v4 データベースのスナップショットまたは復元したコピーに対して移行ツールを実行する**。
    3. **不整合な結果を受け入れる**。接続性や情報が失われる変換の挙動を洗い出すには役立ちますが、行数や参照整合性は信頼できません。

## 必要なもの

- [Docker](https://docs.docker.com/get-docker/) と [Compose v2](https://docs.docker.com/compose/install/)。
- バージョン **4.14.2 以降**の v4 インスタンスのデータベースに接続できること。データベースは次のいずれかです。
    - **PostgreSQL**
    - **Microsoft SQL Server**
- その v4 データベースの JDBC URL、ユーザー名、パスワード。

!!! note

    v4 がホスト上で動作している場合は、v4 の JDBC URL で `localhost` の代わりに `host.docker.internal` を使います。移行ツールはコンテナー内で動作するため、ホストの `localhost` には接続できません。

## Compose ファイルをダウンロードする

v5 の移行先には、クイックスタートの Compose ファイルを再利用します。

```shell
curl -O https://raw.githubusercontent.com/DependencyTrack/docs/main/docs/tutorials/docker-compose.quickstart.yml
```

??? note "Compose ファイルの内容"
    ```yaml linenums="1"
    --8<-- "docs/tutorials/docker-compose.quickstart.yml"
    ```

!!! warning "v4 と同じホストで実行する場合"

    この Compose ファイルは Compose プロジェクト名 `Dependency-Track` を宣言しており、Docker はこれを `dependency-track` に正規化します。同じホストで v4 スタックも Docker Compose で実行していて、そのプロジェクト名が同じ値に正規化される場合、このチュートリアルのコマンドは v4 プロジェクトを対象にしてしまい、v4 のサービスを停止または削除します。その場合は、先に進む前に、ダウンロードした Compose ファイルの先頭にある `name:` フィールドを `dtrack-v5-sandbox` などの一意な値に変更します。あわせて、移行ツールのエイリアスのネットワーク名も `--network=dtrack-v5-sandbox_default` のように一致させます。

## Postgres だけを起動する

データベースサービスだけを起動します。

```shell
docker compose -f docker-compose.quickstart.yml up -d postgres
```

`apiserver` はまだ起動**しません**。v5 の apiserver は初回起動時に、移行ツールが v4 から投入する必要のあるテーブルに初期データを入れるため、移行前に起動すると移行先が壊れます。

コンテナーが healthy になるまで待ちます。

```shell
docker compose -f docker-compose.quickstart.yml ps postgres
```

出力は次のようになります。

```text linenums="1"
NAME                       IMAGE                STATUS                   PORTS
dependency-track-postgres-1   postgres:18-alpine   Up 12 seconds (healthy)  5432/tcp
```

## 移行ツールのエイリアスを定義する

移行ツールはコンテナーイメージとして提供されています。コンテナーを Compose のネットワークに接続し、`postgres:5432` で Postgres に接続できるようにするシェルエイリアスを定義します。`<version>` は、移行先の v5 リリースに対応する移行ツールのイメージタグに置き換えます。

```shell linenums="1"
alias v4-migrator='docker run --rm -it --network=dependency-track_default ghcr.io/dependencytrack/v4-migrator:<version>'
```

以降、このチュートリアルでは `v4-migrator <subcommand>` を使います。

!!! note ":material-powershell: PowerShell を使う場合"

    PowerShell には引数を転送するシェルエイリアスがないため、代わりに関数を定義します。

    ```powershell linenums="1"
    function v4-migrator { docker run --rm -it --network=dependency-track_default ghcr.io/dependencytrack/v4-migrator:<version> @args }
    ```

    以降の `v4-migrator` コマンドは、bash と zsh の構文である `\` による行継続を使って複数行にまたがっています。PowerShell では、行末の `\` をそれぞれバッククォート(`` ` ``)に置き換えるか、各コマンドを 1 行にまとめて貼り付けます。

ネットワーク名は Compose プロジェクト名(`Dependency-Track`)から作られ、Docker が小文字に正規化して `_default` を付加します。`docker network ls` で確認できます。

```shell
docker network ls
```

想定される出力:

```text linenums="1"
NETWORK ID     NAME                         DRIVER    SCOPE
2f9b1c4d5e6a   bridge                       bridge    local
8a7b6c5d4e3f   dependency-track_default     bridge    local
1a2b3c4d5e6f   host                         host      local
0f9e8d7c6b5a   none                         null      local
```

## v5 のスキーマを初期化する

空の移行先に v5 のスキーマを適用します。

```shell linenums="1"
v4-migrator bootstrap \
  --target-url 'jdbc:postgresql://postgres:5432/dtrack' \
  --target-user dtrack \
  --target-pass dtrack
```

想定される出力:

```text linenums="1"
Applying v5 Flyway schema up to 202605111028
...
Bootstrap complete. Flyway head = 202605111028. Run 'extract' or 'run' next.
```

これで移行先には v5 のスキーマが作成されますが、**`PERMISSION` テーブルを除いて**行はありません。

## 空の移行先を検証する

初期化したばかりの移行先に対して事前チェックを実行します。

```shell linenums="1"
v4-migrator verify \
  --target-url 'jdbc:postgresql://postgres:5432/dtrack' \
  --target-user dtrack \
  --target-pass dtrack
```

想定される出力:

```text linenums="1"
== v4-migrator verify ==

[Schema]
  OK    Flyway head = 202605111028

[Row counts]
  Table                       Source      Staging           v5    Note
  (no source configured)
  LICENSE                          -            0            0
  TEAM                             -            0            0
  ...

[Probes]
  Staging schema "dt_v4_migration" not present — run extract first.

[Constraints]
  13 CHECK constraint(s) hold across 55 loaded table(s)

== verify complete ==
```

Flyway head が異なる場合や、**`PERMISSION` テーブル以外で**行数が 0 でない場合は、以降のリハーサルは正しく動作しません。

## 移行をドライランする

何かを書き込む前に、移行ツールに実行計画を出力させます。ソースのフラグには v4 の接続情報を指定します。v4 のソースが PostgreSQL か Microsoft SQL Server かの違いは JDBC URL だけです。

!!! tip "パスワードの入力"

    以下のコマンドでは、`--source-pass` を引数なしで渡しています。この場合、移行ツールは対話的にパスワードの入力を求めるため、シークレットがシェルの履歴や `ps` の出力に残りません。インラインで指定する場合は、`--source-pass <v4-pass>` と記述します。

=== ":simple-postgresql: PostgreSQL の v4 ソース"

    ```shell linenums="1"
    v4-migrator run \
      --target-url 'jdbc:postgresql://postgres:5432/dtrack' --target-user dtrack --target-pass dtrack \
      --source-url 'jdbc:postgresql://<v4-host>:5432/<v4-db>' --source-user <v4-user> --source-pass \
      --metrics-retention-days 30 \
      --dry-run
    ```

=== ":material-microsoft: Microsoft SQL Server の v4 ソース"

    ```shell linenums="1"
    v4-migrator run \
      --target-url 'jdbc:postgresql://postgres:5432/dtrack' --target-user dtrack --target-pass dtrack \
      --source-url 'jdbc:sqlserver://<v4-host>:1433;databaseName=<v4-db>' --source-user <v4-user> --source-pass \
      --metrics-retention-days 30 \
      --dry-run
    ```

移行ツールでは `--metrics-retention-days` の指定が必須です。v5 は v4 にはない保持期間に基づいて時系列メトリクスを削除するため、移行ツールは明示的な指定を求めます。このチュートリアルを短時間で終えるために `30` を指定します。期間を長くするとロードフェーズがかなり長くなります。本番の実行ではこの値を見直してください。トレードオフについては[移行ガイド](../guides/administration/migrating-from-v4.md#4-extract-transform-load)を参照してください。

`--dry-run` を指定すると、どちらのデータベースにも何も書き込みません。移行ツールは実行計画を出力して終了します。

## 移行を実行する

`--dry-run` を外し、実際の抽出、変換、ロードを実行します。

=== ":simple-postgresql: PostgreSQL の v4 ソース"

    ```shell linenums="1"
    v4-migrator run \
      --target-url 'jdbc:postgresql://postgres:5432/dtrack' --target-user dtrack --target-pass dtrack \
      --source-url 'jdbc:postgresql://<v4-host>:5432/<v4-db>' --source-user <v4-user> --source-pass \
      --metrics-retention-days 30
    ```

=== ":material-microsoft: Microsoft SQL Server の v4 ソース"

    ```shell linenums="1"
    v4-migrator run \
      --target-url 'jdbc:postgresql://postgres:5432/dtrack' --target-user dtrack --target-pass dtrack \
      --source-url 'jdbc:sqlserver://<v4-host>:1433;databaseName=<v4-db>' --source-user <v4-user> --source-pass \
      --metrics-retention-days 30
    ```

所要時間は v4 のデータセットの規模によって異なります。移行ツールはテーブルごとの進捗と、時間のかかるテーブルについては 5 秒ごとのハートビートを出力し、各フェーズの完了時にも 1 行出力します。`run` は最後に、成功を示す `Migration completed` の行を出力します。

```text linenums="1"
MetricsRetention - Metrics retention set to 30 days (cutoff = 2026-04-15T11:38:10.636499285Z)
ExtractPhase - Extracting LICENSE
ExtractPhase -   -> 811 rows in 395 ms
...
ExtractPhase - Extract phase completed: 64 table(s), 5821044 row(s) in 184302 ms
TransformPhase - Transforming LICENSE
TransformPhase -   -> 811 rows in 60 ms
...
TransformPhase - Transform phase completed: 64 table(s), 5820102 row(s) in 96118 ms
LoadPhase - Pre-creating metrics partitions for 32 day(s) from 2026-04-15 to 2026-05-16
LoadPhase - Loading LICENSE into v5
LoadProgressReporter -   -> LICENSE: 811 rows in 56 ms (14482 rows/s)
...
LoadPhase - Loading VULNERABLESOFTWARE_VULNERABILITIES into v5
LoadProgressReporter -   .. VULNERABLESOFTWARE_VULNERABILITIES: still loading after 5s (expected 2740322 rows)
LoadProgressReporter -   .. VULNERABLESOFTWARE_VULNERABILITIES: still loading after 10s (expected 2740322 rows)
LoadProgressReporter -   .. VULNERABLESOFTWARE_VULNERABILITIES: still loading after 15s (expected 2740322 rows)
...
LoadPhase - Finalizing load: re-enabling triggers and resetting identity sequences
LoadPhase - Analyzing 64 loaded table(s)
LoadPhase - Refreshing PORTFOLIOMETRICS_GLOBAL materialized view
LoadPhase - Applying v5.7.0 cleanup deletes
LoadPhase - Load phase completed: 64 table(s), 5820097 row(s) in 211740 ms
RunCommand - Migration completed: extract + transform + load finished. Run 'verify' to review row counts and probes.
```

## 結果を検証する

もう一度 `verify` を実行します。今回はテーブルごとにソース、ステージング、v5 の行数が表示され、すべてのプローブの結果も表示されます。

```shell linenums="1"
v4-migrator verify \
  --target-url 'jdbc:postgresql://postgres:5432/dtrack' \
  --target-user dtrack \
  --target-pass dtrack
```

想定される出力:

```text linenums="1"
== v4-migrator verify ==

[Schema]
  OK    Flyway head = 202605111028

[Row counts]
  Table                          Source      Staging           v5    Note
  LICENSE                           811          811          811
  LICENSEGROUP                        4            4            4
  LICENSEGROUP_LICENSE              131          131          131
  TEAM                               47           42           42    expected: dedup by NAME (-5)
  PROJECTS_TAGS                   12480        12462        12462    reduction (-18), see migration guide
...

[Probes]
  No probe entries.

[Constraints]
  13 CHECK constraint(s) hold across 55 loaded table(s)

== verify complete ==
```

移行ツールが行の重複排除、削除、書き換えを行った箇所では、ソースと v5 の行数が異なります。これらの削減は移行ツールが意図的に行うものです。`Note` 列には、該当する変換や `[Probes]` セクションへの参照とともに各削減の理由が示されるため、すべての減少の原因を確認できます。移行ガイドの[情報が失われる変更とわかりにくい変更](../guides/administration/migrating-from-v4.md#lossy-and-non-obvious-changes)のセクションにすべてのケースがまとめられているので、確認した削減がそこに記載されたケースと一致することを確かめます。

## ステージングスキーマを削除する

verify の結果に問題がなければ、ステージングスキーマを削除します。

```shell linenums="1"
v4-migrator cleanup \
  --target-url 'jdbc:postgresql://postgres:5432/dtrack' \
  --target-user dtrack \
  --target-pass dtrack
```

## v5 スタックを起動する

移行したデータベースを使って、apiserver とフロントエンドを起動します。

```shell
docker compose -f docker-compose.quickstart.yml up -d apiserver frontend
```

apiserver の起動を見守ります。

```shell
docker compose -f docker-compose.quickstart.yml logs --follow apiserver
```

ログが落ち着いたら、フロントエンド **<http://localhost:8081>** を開いてログインします。

!!! warning "クイックスタートのデフォルトではなく v4 の認証情報を使う"

    移行したデータベースには v4 のユーザーアカウントが含まれているため、[クイックスタート](quickstart.md)の `admin` / `admin` の認証情報はここでは使えません。v4 で使っていたものと同じ認証情報でログインします。LDAP、OIDC、API キーによる認証も同様です。移行ガイドの[情報が失われる変更とわかりにくい変更](../guides/administration/migrating-from-v4.md#lossy-and-non-obvious-changes)のセクションには、名前の衝突時に移行ツールが適用するユーザー名の書き換え(`-CONFLICT-LDAP` や `-CONFLICT-OIDC` のサフィックスなど)が記載されています。

v4 のプロジェクト、コンポーネント、検出結果が表示されます。よく知っているプロジェクトをいくつか確認し、BOM、依存関係、脆弱性が正しく表示されていることを確かめます。

## このチュートリアルで行ったこと

v4 に一切手を加えずに、実際の v4 データセットをサンドボックスの v5 インスタンスに移行しました。このリハーサルにより、自分たちのデプロイについて次の 3 点を確認できました。

- **接続性**: コンテナーから JDBC で v4 に接続できること。
- **データの形**: 移行ツールの変換が、自分たちの v4 のデータに対して最後まで完了すること。
- **情報が失われる影響**: どのユーザー、チーム、プロジェクト、プロパティが、移行ツールによって重複排除、名前変更、削除されるか。

本番の切り替えにかかる時間、v4 をオフラインにしたときの影響、本番ガイドで扱う移行後の認証情報の再入力については、このリハーサルでは確認できません。これらは[移行ガイド](../guides/administration/migrating-from-v4.md)で確認します。

このリハーサルは何度でも安全に繰り返せます。v4 は一切変更されていないため、いつでもサンドボックスを破棄してやり直せます。

## 後片付け

リハーサルが終わったら、サンドボックスとそのボリュームを削除します。

```shell
docker compose -f docker-compose.quickstart.yml down -v
```

Compose ファイルは名前付きボリュームを使っているため、`-v` を指定するとサンドボックスがきれいに削除されます。

## 次のステップ

- [Migrating from v4 to v5](../guides/administration/migrating-from-v4.md): 本番の切り替え手順です。
- [Lossy and non-obvious changes](../guides/administration/migrating-from-v4.md#lossy-and-non-obvious-changes): 本番の実行前に必ず読んでください。
- [Running v4 and v5 in parallel](../guides/administration/running-v4-and-v5-in-parallel.md): 本番に切り替えずに、実際のトラフィックで v5 を試します。
