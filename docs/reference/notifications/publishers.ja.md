# パブリッシャー

## 送信先を制限する {#restricting-destinations}

Dependency-Track は、[`dt.outbound.allowed-destinations`](../configuration/properties.md#dtoutboundallowed-destinations) で許可されたパブリッシャーの送信先にのみ接続します。

!!! note "5.2.0 での変更"
    5.2.0 より前は、メールパブリッシャーと Kafka パブリッシャーは独自のプロパティを使っていました。ローカル接続を許可するには、次のように設定します。

    * `dt.notification-publisher.email.allow-local-connections=true`
    * `dt.notification-publisher.kafka.allow-local-connections=true`

    [v5.2.0 へのアップグレード](../../guides/upgrading/v5.2.0.md)を参照してください。

## コンソール {#console}

通知を標準出力に書き出すことで発行します。

このパブリッシャーはテスト用途を想定しています。設定オプションはありません。

<!-- vale Google.WordList = NO -->
## メール {#email}
<!-- vale Google.WordList = YES -->

通知をメールとして発行します。このパブリッシャーは [SMTP] と [SMTPS] のプロトコルに対応しています。

### グローバル設定 {#global-config}

グローバル設定では、Dependency-Track がメールサーバーに接続する方法を定義します。

![メールパブリッシャーのグローバル設定](../../assets/images/reference/notifications/publishers/email-publisher-global-config.png)

### アラート設定 {#email-alert-config}

アラート設定では、メール通知の受信者と、任意の件名プレフィックスを定義します。

![メールパブリッシャーのアラート設定](../../assets/images/reference/notifications/publishers/email-publisher-alert-config.png)

受信者のアドレスを明示的に列挙するほかに、1 つ以上のチームを受信者として指定することもできます。チームを指定すると、パブリッシャーはそのチームのすべてのメンバーにメールを配信します。

明示的な受信者アドレスとチームは組み合わせて指定できますが、*少なくとも一方*を設定する必要があります。

## Jira {#jira}

Atlassian Jira インスタンスに課題を作成することで通知を発行します。

<!-- vale Vale.Terms = NO -->
### グローバル設定 {#jira-global-config}
<!-- vale Vale.Terms = YES -->

グローバル設定では、Dependency-Track が Jira サーバーに接続する方法を定義します。

![Jira パブリッシャーのグローバル設定](../../assets/images/reference/notifications/publishers/jira-publisher-global-config.png)

課題を作成するとき、Dependency-Track は `{API URL}/rest/api/2/issue` に `POST` リクエストを送信します。

Jira のホスティング形態と認証の構成に応じて、各フィールドを次のように設定します。

<!-- vale Google.WordList = NO -->
* **Jira Data Center または Jira Server:** **API URL** に Jira インスタンスのベース URL(例: `https://jira.example.com`)を設定します。**Username** を指定し、**Password or Token** にパスワードまたはパーソナルアクセストークンのいずれかを指定します。
* **Jira Cloud(Basic 認証):** **API URL** にサイトの URL(例: `https://example.atlassian.net`)を設定します。**Username** にアカウントのメールアドレスを、**Password or Token** に [Atlassian API トークン](https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/)を設定します。
* **Jira Cloud(スコープ付き OAuth 2.0 または API ゲートウェイのトークン):** **API URL** に `https://api.atlassian.com/ex/jira/{cloudId}`(末尾のスラッシュなし)を設定します。`{cloudId}` は Atlassian Cloud のサイト ID です。**Username** は空のままにし、**Password or Token** にアクセストークンを入力します。**Username** が空の場合、Dependency-Track は Basic 認証の代わりに `Bearer` 認可トークンを送信します。トークンに `write:jira-work` スコープ(または細分化された `write:issue:jira` スコープ)が付与されていることを確認してください。
<!-- vale Google.WordList = YES -->

<!-- vale Vale.Terms = NO -->
### アラート設定 {#jira-alert-config}
<!-- vale Vale.Terms = YES -->

アラート設定では、作成する課題のプロパティを定義します。

![Jira パブリッシャーのアラート設定](../../assets/images/reference/notifications/publishers/jira-publisher-alert-config.png)

!!! note
    このパブリッシャーでは、チームを受信者として選択しても効果はありません。

## Kafka {#kafka}

Apache Kafka クラスターにレコードを送出することで通知を発行します。

### グローバル設定 {#kafka-global-config}

グローバル設定では、Dependency-Track が Kafka クラスターに接続する方法を定義します。

![Kafka パブリッシャーのグローバル設定](../../assets/images/reference/notifications/publishers/kafka-publisher-global-config.png)

!!! note "TLS を設定する"
    TLS を有効にする場合は、Kafka ブローカーが使う証明書に署名した認証局(CA)の証明書を指定する**必要があります**。この証明書は [PEM] 形式で、暗号化されていない、つまりパスワードで保護されて**いない**ものである**必要があります**。

!!! note "mTLS を設定する"
    [相互 TLS][mutual TLS] を有効にする場合は、[PEM] 形式のクライアント証明書と鍵を指定する**必要があります**。どちらも暗号化されていない**必要があります**。クライアント鍵は[管理対象シークレット](../../guides/user/managing-secrets.md)である**必要があります**。

!!! note "プロデューサーのデフォルト設定"
    Dependency-Track は、基盤となる Kafka プロデューサーにデフォルトで次の[設定](https://kafka.apache.org/41/configuration/producer-configs/)を適用します。

      * [`compression.type`](https://kafka.apache.org/41/configuration/producer-configs/#producerconfigs_compression.type): `snappy`
      * [`enable.idempotence`](https://kafka.apache.org/41/configuration/producer-configs/#producerconfigs_enable.idempotence): `true`

<!-- vale Google.Latin = NO -->
### アラート設定 {#kafka-alert-config}
<!-- vale Google.Latin = YES -->

アラート設定では、パブリッシャーが送出する Kafka レコードの送信先と形式を定義します。

![Kafka パブリッシャーのアラート設定](../../assets/images/reference/notifications/publishers/kafka-publisher-alert-config.png)

!!! note
    このパブリッシャーでは、チームを受信者として選択しても効果はありません。

!!! tip "Protobuf"
    可能な限り、通知は Protobuf 形式で発行してください。Dependency-Track は Protobuf スキーマの変更を後方互換に保っています。これは、Kafka のような永続的なログが通知を保持する場合に重要です。`.proto` ファイルをダウンロードしてクライアントコードを生成するには、[Notification schema](schema.md) のリファレンスを参照してください。

!!! warning "テンプレート"
    Kafka パブリッシャーは Protobuf を想定しているため、デフォルトのテンプレートが付属していません。別のペイロード形式を使いたい場合は、先にカスタムテンプレートを設定してください。

!!! tip "レコードキー"
    通知のサブジェクトがプロジェクトの場合(`BOM_CONSUMED`、`NEW_VULNERABILITY` などのグループ)、Kafka レコードのキーにはプロジェクトの UUID が入ります。通知のサブジェクトがプロジェクト*でない*場合、キーは `null` です。

## Mattermost {#mattermost}

通知を Mattermost のメッセージとして発行します。

<!-- vale Vale.Terms = NO -->
### アラート設定 {#mattermost-alert-config}
<!-- vale Vale.Terms = YES -->

アラート設定では、Mattermost メッセージの送信先を定義します。

送信先には [Incoming Webhook](https://docs.mattermost.com/integrations-guide/incoming-webhooks.html) の URL を指定します。

!!! note
    このパブリッシャーでは、チームを受信者として選択しても効果はありません。

<!-- vale Google.Headings = NO -->
## Microsoft Teams {#microsoft-teams}
<!-- vale Google.Headings = YES -->

通知を Microsoft Teams のメッセージとして発行します。

### アラート設定 {#teams-alert-config}

アラート設定では、Microsoft Teams メッセージの送信先を定義します。

送信先には [Incoming Webhook](https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook) の URL を指定します。

!!! note
    このパブリッシャーでは、チームを受信者として選択しても効果はありません。

## Slack {#slack}

通知を Slack のメッセージとして発行します。

### アラート設定 {#slack-alert-config}

アラート設定では、Microsoft Teams メッセージの送信先を定義します。

送信先には [Incoming Webhook](https://docs.slack.dev/messaging/sending-messages-using-incoming-webhooks/) の URL を指定します。

!!! note
    このパブリッシャーでは、チームを受信者として選択しても効果はありません。

## Webex {#webex}

通知を Cisco Webex のメッセージとして発行します。

<!-- vale Vale.Terms = NO -->
### アラート設定 {#webex-alert-config}
<!-- vale Vale.Terms = YES -->

アラート設定では、Microsoft Teams メッセージの送信先を定義します。

送信先には [Incoming Webhook](https://apphub.webex.com/applications/incoming-webhooks-cisco-systems-38054-23307-75252) の URL を指定します。

!!! note
    このパブリッシャーでは、チームを受信者として選択しても効果はありません。

## Webhook {#webhook}

通知を Webhook として発行します。

### アラート設定 {#webhook-alert-config}

アラート設定では、Webhook リクエストの送信先と、必要に応じてリクエストの認証方法と署名方法を定義します。

![Webhook パブリッシャーのアラート設定](../../assets/images/reference/notifications/publishers/webhook-publisher-alert-config.png)

!!! note
    このパブリッシャーでは、チームを受信者として選択しても効果はありません。

### 署名 {#signature}

!!! note "5.2.0 以降で利用可能"

    それより前のバージョンは、Webhook リクエストを署名なしで送信します。

アラート設定で署名用シークレットを指定すると、各リクエストに `X-Webhook-Signature` ヘッダーが付きます。署名用シークレットは[管理対象シークレット](../../guides/user/managing-secrets.md)である**必要があります**。

ヘッダーの値は、`sha256=` の後に、シークレットの UTF-8 バイト列を鍵としたリクエストボディの HMAC-SHA256 を小文字の 16 進数でエンコードしたものを続けた文字列です。パブリッシャーは、テンプレートをレンダリングする場合も Protobuf を発行する場合も、実際に送信するバイト列そのものに対してこの値を計算します。

リクエストを検証するには、パース前の生のリクエストボディに対して同じ HMAC を計算し、定数時間でヘッダーの値と比較します。

[PEM]: https://en.wikipedia.org/wiki/Privacy-Enhanced_Mail
[SMTP]: https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol
[SMTPS]: https://en.wikipedia.org/wiki/SMTPS
[mutual TLS]: https://en.wikipedia.org/wiki/Mutual_authentication#mTLS
