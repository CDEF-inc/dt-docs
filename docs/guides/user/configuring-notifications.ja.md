# 通知アラートを設定する

*アラート*は 1 つ以上の[通知グループ](../../reference/notifications/groups.md)をサブスクライブし、一致する通知を[パブリッシャー](../../reference/notifications/publishers.md)を通じて送信先に転送します。このガイドでは、アラートを作成する方法と、アラートをポートフォリオの一部に制限する方法を説明します。

## 前提条件 {#prerequisites}

- `SYSTEM_CONFIGURATION` 権限。
- 設定済みのパブリッシャーが 1 つ以上あること。組み込みのパブリッシャー(メール、Slack、Webhook など)は最初から利用できますが、ほとんどは SMTP サーバーや送信先 URL などのグローバル設定が必要です。[通知パブリッシャーのリファレンス](../../reference/notifications/publishers.md)を参照してください。

## アラートを作成する {#creating-an-alert}

**Administration → Notifications → Alerts** を開き、*Create Alert* をクリックします。次の項目を指定します。

- 一意の **name**。
- [スコープ](../../concepts/notifications.md#scopes): プラットフォームのイベントには `SYSTEM`、プロジェクトのイベントには `PORTFOLIO`。
- アラートが受け取る通知の[レベル](../../concepts/notifications.md#levels)。
- 一致する通知を配信する[パブリッシャー](../../concepts/notifications.md#publishers)。
- アラートの[トリガー](#choosing-a-trigger)。

アラートを保存したら、編集用に開いて残りの項目を設定します。

## トリガーを選択する {#choosing-a-trigger}

リアルタイムに配信するにはトリガーを *Event*(デフォルト)に、定期的なダイジェストを配信するには *Schedule* に設定します。両者の違いについては[トリガー](../../concepts/notifications.md#triggers)を参照してください。サマリーグループ(`NEW_VULNERABILITIES_SUMMARY`、`NEW_POLICY_VIOLATIONS_SUMMARY`)にはスケジュールトリガーが必要です。各グループのトリガーは[通知グループのリファレンス](../../reference/notifications/groups.md)に記載されています。

定期的なダイジェストを設定するには、トリガーを *Schedule* に設定し、後述の[スケジュール設定](#scheduling)を参照してください。その他の手順(グループの選択、送信先、スコープの制限、フィルター式)は、どちらのトリガーにも共通です。

## グループを選択する {#selecting-groups}

各アラートは、そのスコープ内の 1 つ以上の通知グループをサブスクライブします。選択できるグループの一覧には、アラートのスコープとトリガーの種類に対応するグループだけが表示されます。すべてのグループの一覧と、各グループが表す内容については、[Notification groups](../../reference/notifications/groups.md) を参照してください。

## 送信先を設定する {#setting-the-destination}

送信先の形式はパブリッシャーによって異なります。主なケースは次のとおりです。

| パブリッシャー | 送信先 |
| :--- | :--- |
| メール | 1 つ以上の受信者アドレス、1 つ以上のチーム、またはその両方の組み合わせ。[メールアラートの設定][email-alert]を参照してください。 |
| Slack、Microsoft Teams、Mattermost、Webex | 送信先のプラットフォームが発行する Incoming Webhook の URL。 |
| Jira | プロジェクトキーと課題タイプ。[Jira アラートの設定][jira-alert]を参照してください。 |
| Webhook | 通知のペイロードを受け付ける HTTP(S) エンドポイント。 |
| Kafka | トピック名とシリアル化形式。[Kafka アラートの設定][kafka-alert]を参照してください。 |

各パブリッシャーが公開するすべてのフィールドについては、[パブリッシャーのリファレンス](../../reference/notifications/publishers.md)を参照してください。

## プロジェクトに制限する {#limiting-to-projects}

デフォルトでは、`PORTFOLIO` スコープのアラートはポートフォリオ内のすべてのプロジェクトで発火します。制限するには、*Limit To* セクションを展開し、1 つ以上のプロジェクトを追加します。

!!! note
    スケジュールされたアラートでは、プロジェクトの一覧が空でないことが*必須*です。サマリーグループはポートフォリオ全体を対象に実行できません。ペイロードがほとんどの受信システムにとって大きすぎ、計算コストも高すぎるためです。プロジェクトを 1 つ以上指定しないと、アラートを保存できません。

選択したプロジェクトの子プロジェクトの通知も受け取るには、*Include active children of projects* を有効にします。プラットフォームはアクティブな子プロジェクトだけを含め、非アクティブな子プロジェクトはスキップします。

## タグで制限する {#limiting-to-tags}

アラートでは、指定したタグのいずれかが付いたプロジェクトに配信を制限することもできます。*Limit To* セクションにタグを追加します。

一覧に複数のタグが含まれる場合、プロジェクトはそのうち*少なくとも 1 つ*を持っていれば一致します。タグは **OR** の論理で組み合わされます。

*Limit to projects* と *Limit to tags* の両方を設定した場合、プロジェクトは*いずれか*の条件を満たせば一致します。2 つの制限も **OR** の論理で組み合わされます。

## スケジュール設定 {#scheduling}

トリガーが *Schedule* の場合、アラートはイベントごとではなく [cron] 式に従って配信します。

```text
* * * * *
| | | | |
| | | | day of the week (0-6, Sunday to Saturday)
| | | month of the year (1-12)
| | day of the month (1-31)
| hour of the day (0-23)
minute of the hour (0-59)
```

`*` は*任意の値*を意味します。たとえば、`0 8 * * *` は毎日 08:00 に、`0 8 * * 1` は毎週月曜日の 08:00 にトリガーされます。

次のデフォルトと制約があります。

- 新しく作成したアラートのデフォルトのスケジュールは*毎時*です。
- cron 式は **UTC** で解釈されます。`0 8 * * *` は、オペレーターのタイムゾーンにかかわらず UTC の 08:00 を意味します。[crontab guru] などのツールを使うと、式を簡単に作成できます。
- Dependency-Track は実行時刻に達したスケジュールを毎分確認し、順番に処理します。そのため、通知はスケジュールされた時刻から数分遅れて届くことがあります。
- 設定パネルには、最後に成功したトリガーのタイムスタンプと、次に予定されているトリガーのタイムスタンプが表示されます。

前回の正常な実行以降に新しい検出結果がない場合に通知を送信しないようにするには、*Skip if unchanged* を有効にします。これにより、新たに報告する内容がないことが多いスケジュールでのノイズを減らせます。

スケジュールされたサマリーは、ペイロードが大きくなることがあります。メールと Webhook のパブリッシャーは内容全体を確実に処理しますが、Slack や Microsoft Teams などのチャットプラットフォームのパブリッシャーは、メッセージごとのサイズ上限を超えるメッセージを拒否することがあります。大量のデータを扱うスケジュールでは、メール、Webhook、Kafka を使うことをお勧めします。

## フィルター式 {#filter-expressions}

一致する通知をより細かく制御するには(たとえば、CVSS のしきい値を超える脆弱性だけに絞り込むなど)、アラートにフィルター式を付与します。[Filter expressions](../../reference/notifications/filter-expressions.md) を参照してください。

## 関連項目 {#see-also}

- [Notification groups](../../reference/notifications/groups.md)
- [届かない通知をデバッグする](../administration/debugging-notifications.md)
- [Notification publishers](../../reference/notifications/publishers.md)

[cron]: https://en.wikipedia.org/wiki/Cron
[crontab guru]: https://crontab.guru/
[email-alert]: ../../reference/notifications/publishers.md#email-alert-config
[jira-alert]: ../../reference/notifications/publishers.md#jira-alert-config
[kafka-alert]: ../../reference/notifications/publishers.md#kafka-alert-config
