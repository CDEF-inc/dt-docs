# バナーを設定する

Dependency-Track では、アプリケーション全体に表示するバナーを設定できます。バナーは、認証済みのすべてのユーザーに対してアプリケーションの上部に表示されます。このガイドでは、管理者がバナーを有効にし、スタイルを設定し、管理する方法を説明します。

## 概要 {#overview}

バナーは、計画メンテナンスの時間帯や重要なお知らせなど、システム全体に向けた短い告知を想定しています。バナーは認証済みのユーザーにだけ表示され、ログインページとパスワード変更ページには表示されません。

バナーはすべて、管理 UI の **Administration → Configuration → Banner**(ルート `/admin/configuration/banner`)から設定します。

!!! note
    バナーの設定にアクセスするには、`SYSTEM_CONFIGURATION` 権限が必要です。

## 設定項目 {#settings}

設定画面には次のコントロールがあります。

| 設定 | 説明 |
| --- | --- |
| **Activate banner** | バナー全体のオン/オフを切り替えます。無効にすると、バナーは表示されません。 |
| **Allow users to dismiss banner** | ユーザーがバナーを非表示にできるように、閉じる(×)ボタンを追加します。[バナーを閉じる](#dismissing-the-banner)を参照してください。 |
| **Message** | バナーのプレーンテキストの内容([デフォルトモード](#default-mode))。 |
| **Color scheme** | バナーのプリセットの色([デフォルトモード](#default-mode))。 |
| **Custom mode** | メッセージと配色の代わりに HTML エディターに切り替えます。 |
| **HTML content** | バナーとして描画される生の HTML([カスタムモード](#custom-mode))。 |

バナーの内容は、テキストと色を指定する[デフォルト](#default-mode)モードと、HTML を指定する[カスタム](#custom-mode)モードのいずれかで定義できます。

## モード {#modes}

### デフォルトモード {#default-mode}

デフォルトモードでは、プリセットの **Color schemes** のいずれかを使って、プレーンテキストの **Message** を表示します。ほとんどの告知には、このオプションをお勧めします。

次の配色を利用できます。

* `red`
* `orange`
* `green`
* `blue`
* `lilac`

デフォルトモードでバナーを設定するには、次の手順を実行します。

1. **Activate banner** を有効にします。
2. ユーザーがバナーを閉じられるようにする場合は、**Allow users to dismiss banner** を有効にします。
3. **Message** フィールドにバナーのテキストを入力します。
4. **Color scheme** を選択します。
5. **Custom mode** は無効のままにします。
6. **Update** を選択して保存します。

!!! note
    バナーが有効で **Message** フィールドが空の間は、**Update** ボタンは無効のままです。

次のスクリーンショットは、**Allow users to dismiss banner** を有効にして**デフォルトモード**で設定したバナーです。

![閉じる操作を有効にしてデフォルトモードで設定したバナー](../../assets/images/guides/administration/configuring-banner/default_banner_example.png)

### カスタムモード {#custom-mode}

カスタムモードでは、メッセージと配色の代わりに本格的な HTML エディターを使い、バナーのスタイル、レイアウト、リンクを完全に制御できます。プリセットの配色やプレーンテキストでは不十分な場合(リンクを埋め込む場合など)に、このモードを使います。

カスタムモードでバナーを設定するには、次の手順を実行します。

1. **Activate banner** を有効にします。
2. ユーザーがバナーを閉じられるようにする場合は、**Allow users to dismiss banner** を有効にします。
3. **Custom mode** を有効にします。これによりメッセージと色の設定がクリアされ、エディターにサンプルのテンプレートが入力されます。
4. エディターで **HTML content** を編集します。
5. **Update** を選択して保存します。

!!! note
    カスタムモードを有効にすると、**Message** フィールドと色の見本は無効になります。バナーが有効で **HTML content** が空の間は、**Update** ボタンは無効のままです。

??? example "HTML コンテンツの例"
    ```html linenums="1"
    <div style="background:#321FDB;color:#fff;padding:0.5rem 1rem;border-bottom:1px solid rgba(0,0,0,.2);font-size:1rem;line-height:1.5;text-align:center">
      <strong>Example:</strong> <span>Your HTML-Banner Text</span>
    </div>
    ```

次のスクリーンショットは、**Allow users to dismiss banner** を有効にして**カスタムモード**で設定したバナーです。

![閉じる操作を有効にしてカスタムモードで設定したバナー](../../assets/images/guides/administration/configuring-banner/custom_banner_example.png)

## バナーを閉じる {#dismissing-the-banner}

**Allow users to dismiss banner** オプションは、ユーザーが自分でバナーを非表示にできるかどうかを制御します。

有効にした場合は、次のようになります。

* バナーの右上隅に閉じる(×)ボタンが表示されます。
* ユーザーがバナーを閉じると、そのブラウザーセッションの間は非表示のままになります。
* 新しいログインセッションでは、バナーが再び表示されます。

無効にした場合は、閉じるボタンは表示されず、ユーザーはバナーを非表示にできません。
