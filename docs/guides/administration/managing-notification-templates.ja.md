# 通知テンプレートを管理する

*通知テンプレート*は、[通知](../../concepts/notifications.md)を[パブリッシャー](../../reference/notifications/publishers.md)が配信するペイロードにレンダリングします。各テンプレートは、[Pebble](https://pebbletemplates.io/) のソース、MIME タイプ、そしてちょうど 1 つのパブリッシャーへのバインディングで構成されます。

組み込みのパブリッシャーにはそれぞれデフォルトのテンプレートが付属しています。システムはデフォルトのテンプレートを読み取り専用として扱います。アラートが配信するペイロードをカスタマイズするには、デフォルトのテンプレートをクローンし、クローンを編集します。

## 前提条件 {#prerequisites}

- `SYSTEM_CONFIGURATION` 権限。

## デフォルトのテンプレートをクローンする {#cloning-a-default-template}

**Administration > Notifications > Templates** を開きます。このページには、組み込みの各パブリッシャーのデフォルトのテンプレートが、デフォルトであることを示す印付きで一覧表示されます。出発点にするテンプレートを選択し、*Clone* をクリックします。クローンしたテンプレートは、元のテンプレートからパブリッシャーのバインディングとソースを引き継ぎ、編集可能なままになります。

![デフォルトのテンプレート](../../assets/images/guides/administration/managing-notification-templates/default-template.png)

## テンプレートを編集する {#editing-a-template}

ユーザーが作成したテンプレートを選択すると、その Pebble のソースと MIME タイプを編集できます。テンプレートで使える変数とフィルターは、[テンプレートのリファレンス](../../reference/notifications/templating.md)に記載されています。MIME タイプは、バインドされたパブリッシャーが想定するものと一致している必要があります。パブリッシャーごとのペイロードの要件については、[パブリッシャーのリファレンス](../../reference/notifications/publishers.md)を参照してください。

![カスタムテンプレート](../../assets/images/guides/administration/managing-notification-templates/custom-template.png)

## テンプレートを削除する {#deleting-a-template}

デフォルトのテンプレートは削除できません。ユーザーが作成したテンプレートは、テンプレートの一覧から削除できます。テンプレートを参照しているアラートが残っている場合、削除は失敗します。先にそれらのアラートを別のテンプレートに割り当て直すか、削除してください。

## 関連項目 {#see-also}

- [Notification publishers](../../reference/notifications/publishers.md)
- [Templating reference](../../reference/notifications/templating.md)
- [通知アラートを設定する](../user/configuring-notifications.md)
- [届かない通知をデバッグする](debugging-notifications.md)
