# 通知を設定する

このチュートリアルでは、最初の[通知アラート](../concepts/notifications.md#alerts)を設定し、BOM をアップロードしたときにアラートが発火することを確認します。API サーバーの標準出力に通知を書き出す、組み込みの *Console* パブリッシャーを使います。そのため、メールサーバー、チャットのワークスペース、Webhook のエンドポイントがなくても、このチュートリアルだけで完結します。

## 必要なもの {#what-we-need}

- [クイックスタート](quickstart.md)で起動した Dependency-Track スタック。
- アップロードする BOM ファイル。有効な CycloneDX BOM であれば何でもかまいません。Dependency-Track 自体の [SBOM][dt-sbom] を使うと便利です。

## ログインする {#logging-in}

フロントエンド **<http://localhost:8081>** を開き、`admin` としてログインします。初回ログイン後に新しいパスワードを設定します。

![ログイン](../assets/images/tutorials/setting-up-notifications/login.png)

## プロジェクトを作成する {#creating-a-project}

`BOM_PROCESSED` 通知は特定のプロジェクトに対して発火するため、SBOM のアップロード先となるプロジェクトが必要です。

**Projects > Create Project** を開き、名前を `notifications-demo` にして保存します。

## アラートを作成する {#creating-the-alert}

**Administration > Notifications > Alerts** を開き、*Create Alert* を選択して次の値を入力します。

| フィールド   | 値                      |
|--------------|-------------------------|
| Name         | `Console BOM_PROCESSED` |
| Scope        | `Portfolio`             |
| Level        | `Informational`         |
| Publisher    | `Console`               |
| Trigger type | `Event`                 |

![アラート作成ダイアログ](../assets/images/tutorials/setting-up-notifications/create-alert.png)

保存したら、新しいアラートを開き、*Notification Groups* で `BOM_PROCESSED` グループを有効にします。*Limit To* は空のままにして、ポートフォリオ内のすべてのプロジェクトでアラートが発火するようにします。

Console パブリッシャーには追加の設定は不要です。常に API サーバーの標準出力に書き出します。

![アラートの設定](../assets/images/tutorials/setting-up-notifications/alert-config.png)

## API サーバーのログを監視する {#watching-the-api-server-logs}

別のターミナルで、API サーバーのコンテナーログを追跡します。

```shell
docker compose -f docker-compose.quickstart.yml logs --follow apiserver
```

このターミナルは表示したままにしておきます。通知はここに表示されます。

## 通知を発生させる {#triggering-a-notification}

フロントエンドに戻り、`notifications-demo` プロジェクトを開いて *Components* タブに切り替え、*Upload BOM* から SBOM をアップロードします。Dependency-Track は BOM をインポートして処理し、処理が完了すると `BOM_PROCESSED` 通知を発行します。

数秒以内に、ログを追跡しているターミナルに通知の出力が表示されます。

```text linenums="1"
--------------------------------------------------------------------------------
Notification
  -- timestamp: 2026-04-27T09:59:02.563Z
  -- level:     LEVEL_INFORMATIONAL
  -- scope:     SCOPE_PORTFOLIO
  -- group:     GROUP_BOM_PROCESSED
  -- title:     Bill of Materials Processed
  -- content:   A CycloneDX BOM was processed
```

これで、アラートが一連の流れを通して動作したことになります。プラットフォームでイベントが発生し、アラートがそれに一致し、パブリッシャーが内容をレンダリングし、送信先に配信されました。

## 次のステップ {#whats-next}

- [Configuring notification alerts](../guides/user/configuring-notifications.md): プロジェクトやタグによる制限を追加し、実際のパブリッシャーに切り替えます。
- [Notification publishers](../reference/notifications/publishers.md): メール、Slack、Webhook などの送信先を設定します。
- [Templating reference](../reference/notifications/templating.md): 通知の表示内容をカスタマイズします。
- [届かない通知をデバッグする](../guides/administration/debugging-notifications.md): 配信されないアラートの原因を調べます。

[dt-sbom]: https://github.com/DependencyTrack/dependency-track/releases
