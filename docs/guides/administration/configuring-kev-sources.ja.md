# KEV データソースを設定する

!!! note
    KEV との連携には Dependency-Track **5.1 以降**が必要です。

CISA KEV、ENISA EU KEV、VulnCheck KEV は、Dependency-Track が内部データベースにミラーリングできる 3 つの KEV カタログです。有効にするデータソースを選び、フロントエンドで設定し、初回のミラーリングをトリガーすることで、次回のスケジュール実行を待たずに KEV のステータスが表示されるようになります。

各データソースが提供する内容と、ミラーリングしたアサーションが脆弱性に紐付けられるしくみについては、[About KEV data sources](../../concepts/about-kev-data-sources.md) を参照してください。

## 前提条件 {#prerequisites}

有効にする予定の各データソースについて、API サーバーから対応するホストへの送信 HTTPS アクセスを許可します。

| データソース | ホスト |
|:-------|:-----|
| CISA KEV | `www.cisa.gov`、または設定したミラーのホスト |
| ENISA EU KEV | `raw.githubusercontent.com` |
| VulnCheck KEV | `api.vulncheck.com`、および返されるダウンロード URL のストレージホスト |

VulnCheck KEV は 2 段階でカタログをダウンロードします。Dependency-Track は `api.vulncheck.com` に現在のバックアップを問い合わせ、レスポンスに含まれる署名付き URL からアーカイブを取得します。この URL は別のストレージホストを指しています。`api.vulncheck.com` だけを対象とする許可リストでは、ミラーリングの実行がダウンロードの段階で失敗します。

送信トラフィックがプロキシを経由する必要がある場合は、[HTTP プロキシを設定する](configuring-http-proxy.md)を参照してください。プロキシが TLS を傍受する場合は、[社内 CA の信頼を設定する](configuring-internal-ca.md)を参照してください。

VulnCheck KEV には API トークンが必要です。CISA KEV と ENISA EU KEV には認証情報は不要です。

## データソースを有効にする {#enabling-sources}

フロントエンドで **Administration > KEV Sources** を開きます。各データソースには個別の設定パネルがあります。

### CISA KEV {#cisa-kev}

1. **Administration > KEV Sources > CISA KEV** を開きます。
2. オフになっている場合は **Enabled** を選択します。Dependency-Track では、CISA KEV はデフォルトでオンになっています。
3. **Save** を選択します。フォームに未保存の変更がある間は **Mirror now** を使えません。
4. **Mirror now** を選択し、カタログをすぐにダウンロードします。

![CISA KEV の設定](../../assets/images/guides/administration/configuring-kev-sources/cisa.png)

!!! note "デフォルトのフィードホストは一部のネットワークをブロックする"
    デフォルトのフィード URL `https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json` は、一部の IP アドレス範囲やホスティングプロバイダーからのリクエストを拒否します。Hetzner でホストされているサーバーからこの現象が確認されています。ミラーリングの実行が接続エラーまたは HTTP エラーで失敗する場合は、**Feed URL** を次のいずれかのミラーに変更してください。

    - `https://raw.githubusercontent.com/cisagov/kev-data/main/known_exploited_vulnerabilities.json`: CISA 自身の GitHub ミラー
    - `https://raw.githubusercontent.com/aboutcode-org/aboutcode-mirror-kev/main/known_exploited_vulnerabilities.json`: AboutCode がホストするコミュニティミラー

CISA KEV のアサーションは、NVD の名前空間で解決された CVE ID によって脆弱性に紐付けられます。[How KEV matching works](../../concepts/about-kev-data-sources.md#how-kev-matching-works) を参照してください。

### ENISA EU KEV {#enisa-eu-kev}

1. **Administration > KEV Sources > ENISA EU KEV** を開きます。
2. オフになっている場合は **Enabled** を選択します。Dependency-Track では、ENISA EU KEV はデフォルトでオンになっています。
3. **Save** を選択します。フォームに未保存の変更がある間は **Mirror now** を使えません。
4. **Mirror now** を選択し、カタログをすぐにダウンロードします。

![ENISA EU KEV の設定](../../assets/images/guides/administration/configuring-kev-sources/enisa.png)

!!! note
    CVE ID を持たない ENISA EU KEV のエントリーは KEV アサーションを生成しないため、脆弱性を既知の悪用済みとしてマークすることはありません。

### VulnCheck KEV {#vulncheck-kev}

1. **Administration > KEV Sources > VulnCheck KEV** を開きます。
2. **Enabled** を選択し、VulnCheck KEV をオンにします。Dependency-Track では、デフォルトでオフになっています。
3. **API Token** にトークンを入力します。無料のコミュニティトークンは [VulnCheck の Web サイト](https://vulncheck.com/token/newtoken)で作成できます。Dependency-Track はトークンを平文ではなく、管理対象シークレットとして保存します。
4. **Save** を選択します。フォームに未保存の変更がある間は **Mirror now** を使えません。
5. **Mirror now** を選択し、カタログをすぐにダウンロードします。トークンが誤っているか期限切れの場合は、ミラーリングの実行の失敗として現れるため、実行の終了後にステータスを確認してください。

![VulnCheck KEV の設定](../../assets/images/guides/administration/configuring-kev-sources/vulncheck.png)

!!! tip
    VulnCheck KEV は CISA KEV が漏らしている脆弱性をカバーし、悪用をより早く報告することがよくあります。トレードオフについては [Picking sources](../../concepts/about-kev-data-sources.md#picking-sources) を参照してください。

## 初回のミラーリングをトリガーする {#triggering-an-initial-mirror}

データソースを初めて有効にした後は、次回のスケジュール実行を待たずに **Mirror now** を使ってください。設定パネルには、ミラーリングのステータス(pending、running、succeeded、failed)が相対的なタイムスタンプとともに表示されます。

## ミラーリングの実行をスケジュールする {#scheduling-mirror-runs}

1 つの cron プロパティがすべての KEV データソースを制御します。[`dt.task.kev-mirror.cron`](../../reference/configuration/properties.md#dttaskkev-mirrorcron) で、デフォルトは `0 2 * * *`(毎日 02:00 UTC)です。各実行では、オンになっているすべてのデータソースをミラーリングし、オフのデータソースはスキップします。新規デプロイでは起動直後にタスクが 1 回実行されるため、初回のミラーリングはスケジュールを待ちません。その後の再起動ではミラーリングはトリガーされません。

## KEV のステータスを確認する {#verifying-kev-status}

ミラーリングが完了したら、有効にしたカタログのいずれかに含まれていることがわかっている脆弱性(たとえば Log4Shell の `CVE-2021-44228`)を、ポートフォリオの Vulnerabilities 一覧、プロジェクトの Findings ビュー、または Vulnerability Audit ビューで開きます。**KEV** 列に照準アイコンが表示されることを確認し、そのアイコンを選択してアサーションの詳細を開きます。照合はコンポーネントの識別子ではなく、脆弱性のエイリアスに基づいて行われます。[How KEV matching works](../../concepts/about-kev-data-sources.md#how-kev-matching-works) を参照してください。

ミラーリング後も KEV 列が空のままの場合は、API サーバーのログでミラーリングのエラーを確認してください。

## 関連項目 {#see-also}

- [About KEV data sources](../../concepts/about-kev-data-sources.md)
- [脆弱性データソースを設定する](configuring-vulnerability-sources.md)
- [About vulnerability data sources](../../concepts/about-vulnerability-data-sources.md)
- [エアギャップ環境で運用する](running-air-gapped.md)
- [HTTP プロキシを設定する](configuring-http-proxy.md)
- [社内 CA の信頼を設定する](configuring-internal-ca.md)
