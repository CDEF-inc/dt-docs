# タスクスケジューラー

タスクスケジューラーは、脆弱性データソースのミラーリング、連携先へのアップロード、メトリクスの更新、メンテナンス処理などの定期的なバックグラウンド処理をトリガーします。多くのタスクは、ワークフローやその他の非同期処理を実行する[永続実行エンジン](dex-engine.md)に処理をキューイングします。

スケジューラーを有効にしたノードは、安全に共存できます。スケジューラーはデータベースを通じて実行を協調させるため、リーダー選出を必要とせずに、実行時刻になった各タスクはちょうど 1 つのノードで実行されます。

## 設定 {#configuration}

スケジューラーはノードごとにオフにできます。たとえば、特定のノードを Web トラフィックの処理専用にする場合に使います。`threads` 設定は、1 つのノードで同時に実行できるスケジュール済みタスクの数の上限を設定します。非同期処理の大半は[永続実行エンジン](dex-engine.md)が行うため、通常はこの設定を調整する必要はありません。

設定:

- [`dt.task-scheduler.enabled`](properties.md#dttask-schedulerenabled)
- [`dt.task-scheduler.threads`](properties.md#dttask-schedulerthreads)
- [`dt.task-scheduler.poll-interval-ms`](properties.md#dttask-schedulerpoll-interval-ms)
- [`dt.task-scheduler.shutdown-max-wait-ms`](properties.md#dttask-schedulershutdown-max-wait-ms)

## cron 式 {#cron-expressions}

各スケジュール済みタスクは、`dt.task.<name>.cron` プロパティからスケジュールを取得します。このプロパティには、5 つのフィールドからなる UNIX の cron 式を指定します。

```text
minute  hour  day-of-month  month  day-of-week
```

すべての式は **UTC** を使用します。

毎日 03:30 UTC に実行する例:

```ini
dt.task.nvd-vuln-data-source-mirror.cron=30 3 * * *
```

## スケジュール済みタスク {#scheduled-tasks}

スケジューラーには、次の定期タスクが組み込まれています。[^1] が付いたタスクは、スケジューラーが初めて登録した直後にも、最大 1 分のランダムな遅延の後に 1 回実行されます。

| タスク                              | プロパティ                                                                                                                | デフォルトの cron     | 目的                                                                                       |
|-----------------------------------|-------------------------------------------------------------------------------------------------------------------------|------------------|-----------------------------------------------------------------------------------------------|
| ポートフォリオのメトリクスの更新          | [`dt.task.portfolio-metrics-update.cron`](properties.md#dttaskportfolio-metrics-updatecron)                             | `10 * * * *`     | プロジェクトごとおよびポートフォリオの時系列メトリクスを更新します。                                      |
| 脆弱性メトリクスの更新      | [`dt.task.vuln-metrics-update.cron`](properties.md#dttaskvuln-metrics-updatecron)                                       | `0 */6 * * *`    | 脆弱性ダッシュボードで使われるカウンターを更新します。                                       |
| NVD のミラー[^1]                    | [`dt.task.nvd-vuln-data-source-mirror.cron`](properties.md#dttasknvd-vuln-data-source-mirrorcron)                       | `0 4 * * *`      | NIST National Vulnerability Database をミラーリングします。                                             |
| GitHub Advisories のミラー[^1]      | [`dt.task.github-advisory-vuln-data-source-mirror.cron`](properties.md#dttaskgithub-advisory-vuln-data-source-mirrorcron) | `0 2 * * *`    | GitHub Advisory Database をミラーリングします。                                                         |
| OSV のミラー[^1]                    | [`dt.task.osv-vuln-data-source-mirror.cron`](properties.md#dttaskosv-vuln-data-source-mirrorcron)                       | `0 3 * * *`      | OSV の脆弱性データベースをミラーリングします。                                                       |
| EPSS のミラー[^1]                   | [`dt.task.epss-mirror.cron`](properties.md#dttaskepss-mirrorcron)                                                       | `0 1 * * *`      | FIRST の EPSS スコアのフィードをミラーリングします。                                                           |
| 脆弱性データベースのメンテナンス | [`dt.task.vuln-database-maintenance.cron`](properties.md#dttaskvuln-database-maintenancecron)                          | `0 0 * * *`      | 孤立した脆弱性レコードを削除し、インデックスを整合させます。                                |
| 脆弱性ポリシーのバンドルの同期[^1] | [`dt.task.vuln-policy-bundle-sync.cron`](properties.md#dttaskvuln-policy-bundle-synccron)                            | `*/15 * * * *`   | 設定された脆弱性ポリシーのバンドルを取得します。`dt.vuln-policy-bundle.url` が空の場合は何もしません。 |
| パッケージメタデータの解決       | [`dt.task.package-metadata-resolution.cron`](properties.md#dttaskpackage-metadata-resolutioncron)                       | `0 1 * * *`      | ポートフォリオのコンポーネントについて、古いコンポーネントかどうかの状態を更新します。                                 |
| パッケージメタデータのメンテナンス      | [`dt.task.package-metadata-maintenance.cron`](properties.md#dttaskpackage-metadata-maintenancecron)                     | `0 */12 * * *`   | 古くなったパッケージメタデータのレコードや孤立したレコードを削除します。                                          |
| メトリクスのメンテナンス               | [`dt.task.metrics-maintenance.cron`](properties.md#dttaskmetrics-maintenancecron)                                       | `1 * * * *`      | 時系列メトリクスの履歴を圧縮します。                                                          |
| タグのメンテナンス                   | [`dt.task.tag-maintenance.cron`](properties.md#dttasktag-maintenancecron)                                               | `0 */12 * * *`   | 使われていないタグを削除します。                                                                          |
| プロジェクトのメンテナンス               | [`dt.task.project-maintenance.cron`](properties.md#dttaskproject-maintenancecron)                                       | `0 */4 * * *`    | プロジェクトの保持ルールとクリーンアップルールを適用します。                                                  |
| Fortify SSC へのアップロード                | [`dt.task.fortify-ssc-upload.cron`](properties.md#dttaskfortify-ssc-uploadcron)                                         | `0 2 * * *`      | 検出結果のレポートを Fortify SSC にアップロードします。                                                       |
| DefectDojo へのアップロード                 | [`dt.task.defect-dojo-upload.cron`](properties.md#dttaskdefect-dojo-uploadcron)                                         | `0 2 * * *`      | 検出結果のレポートを DefectDojo にアップロードします。                                                        |
| Kenna Security へのアップロード             | [`dt.task.kenna-security-upload.cron`](properties.md#dttaskkenna-security-uploadcron)                                   | `0 2 * * *`      | 検出結果のレポートを Kenna Security にアップロードします。                                                    |
| 期限切れセッションのクリーンアップ           | [`dt.task.expired-session-cleanup.cron`](properties.md#dttaskexpired-session-cleanupcron)                               | `0 * * * *`      | 期限切れのユーザーセッショントークンを削除します。                                                          |
| スケジュール通知の送信   | [`dt.task.scheduled-notification-dispatch.cron`](properties.md#dttaskscheduled-notification-dispatchcron)               | `* * * * *`      | 実行時刻になったスケジュール通知ルールをポーリングし、送信します。                               |
| テレメトリーの送信[^1]          | [`dt.task.telemetry-submission.cron`](properties.md#dttasktelemetry-submissioncron)                                     | `0 */1 * * *`    | 匿名の利用状況データを送信します。[テレメトリー](telemetry.md)を参照してください。                                  |

[^1]: スケジューラーがタスクを初めて登録したときに、最大 1 分のランダムな遅延の後に 1 回トリガーされ、その後は設定したスケジュールで実行されます。登録は、新規デプロイ時、またはアップグレードでそのタスクが追加されたときに行われます。その後の再起動では、追加の実行はトリガーされません。
