# 届かない通知をデバッグする

想定していた通知が届かないとユーザーから報告があった場合、原因はたいてい少数のカテゴリのいずれかに当てはまります。このガイドでは、原因を絞り込む方法を順を追って説明します。

## よくある原因 {#common-causes}

- **アラートの設定の誤り。** アラートのスコープ、レベル、グループの選択、プロジェクトによる制限、タグによる制限のいずれかによって、通知が除外されています。[通知アラートを設定する](../user/configuring-notifications.md)と照らし合わせて確認してください。
- **フィルター式が通知を拒否している。** アラートの CEL フィルターが false と評価されています。[フィルター式](../../reference/notifications/filter-expressions.md)の説明に従って式をテストしてください。
- **パブリッシャーの送信先に到達できない。** ネットワークの障害、ファイアウォール、プロキシの設定の誤り、Webhook URL の期限切れなどが原因です。
- **送信先が拒否されている。** [`dt.outbound.allowed-destinations`](../../reference/configuration/properties.md#dtoutboundallowed-destinations) が送信先を許可していません。5.2.0 より前のバージョンでは、メールと Kafka のパブリッシャーは代わりにそれぞれ独自の `allow-local-connections` プロパティを使っていました。
- **カスタムテンプレートの描画に失敗している。** 構文エラーや変数の欠落により、パブリッシャーが送信前に停止します。

## API サーバーのログを調べる {#inspecting-the-api-server-logs}

API サーバーは、配信の失敗を `WARN` または `ERROR` レベルでログに記録します。アラートの名前またはパブリッシャーのクラス名でログを検索してください。デフォルトでは、サーバーは成功した配信をログに*記録しません*。

特定のアラートで成功した配信をログに記録するには、アラートを開いて *Log successful publishes* を有効にします。すると、API サーバーはアラートが配信するたびに `INFO` のログ行を出力します。

!!! note
    通知の多いアラートでこれを有効にすると、ログの量が急増することがあります。一時的な診断として扱うか、配信の頻度が低いアラートに限定してください。

成功した送信のログ行には、一致したアラート、パブリッシャー、通知の概要(グループ、レベル、スコープ、サブジェクトの識別子)が含まれます。

```text
INFO ... Notification published successfully [notificationId=..., notificationRuleName=...]
```

失敗のログ行には、根本の例外が含まれます。よくあるパターンは次のとおりです。

- `UnknownHostException` / `ConnectException`: API サーバーから送信先ホストに到達できません。
- `SSLHandshakeException`: TLS の設定が一致していません(証明書の期限切れ、社内 CA が信頼されていない、プロトコルや暗号スイートの不一致)。
- `IOException: Server returned HTTP response code: 4xx`: 送信先がリクエストを拒否しました。レスポンスの本文を確認してください。
- `PebbleException`: カスタムテンプレートの描画に失敗しています。

## リクエストビンでエンドツーエンドに検証する {#end-to-end-verification-with-a-request-bin}

Webhook ベースのパブリッシャー(Webhook、Slack、Microsoft Teams、Mattermost、Webex、Jira)では、アラートの送信先をリクエストビンのサービスに向けて、API サーバーがそもそもリクエストを送信しているかどうかを確認します。

1. <https://pipedream.com/requestbin>(または同様のサービス)で非公開のリクエストビンを作成します。
2. アラートを編集し、送信先をビンの URL に置き換えます。
3. 該当するグループを選択していることを確認します。
4. 選択したグループのいずれかに一致するイベントをトリガーします。たとえば、アラートの対象となるプロジェクトに SBOM をアップロードすると、`BOM_PROCESSED` が発火します。
5. リクエストビンを監視します。リクエストが届けば API サーバーは送信しているので、元の送信先が原因です。

Webhook 以外のパブリッシャー(メール、Kafka)では、オペレーターが管理する送信先に置き換えます。たとえば、メールを捕捉する SMTP サーバー(MailHog など)や、直接確認できる Kafka トピックを使います。

## 最も手早いローカルでの確認: コンソールパブリッシャー {#quickest-local-check-the-console-publisher}

組み込みの Console パブリッシャーは、通知を API サーバーの標準出力に書き込みます。ローカルでのデバッグでは、ネットワークを完全に切り離して確認できます。

1. `dt.notification-publisher.console.enabled` が `true` であることを確認します。
2. Console パブリッシャーを使い、対象のグループを選択したアラートを作成します。
3. 一致するイベントをトリガーします。
4. API サーバーのコンテナーのログを確認します。

Console パブリッシャーは通知を出力するのに、別のパブリッシャーを使う並行のアラートが通知を出力しない場合、問題は 2 つ目のパブリッシャーの設定または送信先にあります。

## 関連項目 {#see-also}

- [パブリッシャー](../../reference/notifications/publishers.md)
- [フィルター式](../../reference/notifications/filter-expressions.md)
- [通知アラートを設定する](../user/configuring-notifications.md)
