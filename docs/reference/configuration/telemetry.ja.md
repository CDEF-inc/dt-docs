# テレメトリー

Dependency-Track は、小さな匿名のデータを定期的に `https://metrics.dependencytrack.org` に送信します。このデータは、メンテナーが利用状況を把握し、バージョンサポートを計画し、どのデータベースシステムでテストを続けるかを決めるのに役立ちます。

送信されるデータには、IP アドレス、ホスト名、プロジェクトの内容など、特定の組織に結び付けられる情報は含まれません。

## 収集するデータ {#data-collected}

各送信は、4 つのフィールドを持つ 1 つの JSON オブジェクトです。

| フィールド   | 説明                                                                        |
|--------------|-----------------------------------------------------------------------------|
| `system_id`  | 初回起動時に生成されるランダムなクラスター識別子。再起動やノードの入れ替えをまたいでも変わりません。 |
| `dt_version` | Dependency-Track のリリースバージョン。                                     |
| `db_type`    | JDBC が報告するデータベース製品名(たとえば `PostgreSQL`)。                |
| `db_version` | JDBC が報告するデータベース製品のバージョン。                               |

`system_id` により、メンテナーは運用者を特定することなく、同じデプロイからの送信を時系列で関連付けられます。

## 送信スケジュール {#submission-schedule}

[タスクスケジューラー](task-scheduler.md)は、起動直後に最大 1 分のランダムな遅延を置いてテレメトリー送信タスクを 1 回実行し、その後は [`dt.task.telemetry-submission.cron`](properties.md#dttasktelemetry-submissioncron) で定義されたスケジュール(デフォルトは `0 */1 * * *`、1 時間ごと)で実行します。

タスク自体が送信の間隔を 24 時間に制限しています。そのため、cron 式が制御するのは、新しい送信が必要かどうかをタスクが確認する頻度であり、実際にデータを送信する頻度ではありません。

## オプトアウト {#opting-out}

次のいずれかの方法で、いつでもオプトアウトできます。

### 管理 UI {#administration-ui}

**Administration** > **Configuration** > **Telemetry** に移動し、送信をオフにします。

### 設定 API {#configuration-api}

```shell linenums="1"
curl -X POST \
  -H 'X-Api-Key: odt_...' \
  -H 'Content-Type: application/json' \
  -d '{
        "groupName": "telemetry",
        "propertyName": "submission.enabled",
        "propertyValue": "false"
      }' \
  https://dtrack.example.com/api/v1/configProperty
```

### 初回起動の前 {#before-first-startup}

初回起動でランタイム設定が作成される前にオプトアウトするには、[`dt.telemetry.submission.default-enabled`](properties.md#dttelemetrysubmissiondefault-enabled) を `false` に設定します。

```ini
dt.telemetry.submission.default-enabled=false
```

環境変数の場合:

```shell
DT_TELEMETRY_SUBMISSION_DEFAULT_ENABLED=false
```

このプロパティは、ランタイム設定の初期値を設定するだけです。設定がデータベースに作成された後は、UI や REST API による変更が初期値より優先されます。
