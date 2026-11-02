# KEV データソースについて

!!! note
    KEV との連携には Dependency-Track **5.1 以降**が必要です。

KEV データソースは、実際に悪用されていることが確認された脆弱性をまとめた上流のカタログです。通常の脆弱性データソースと KEV データソースは、異なるシグナルを送ります。NVD、GHSA、OSV は、脆弱性が存在することを伝え、その深刻度を評価します。KEV のアサーションは、悪用がすでに起きていることを伝えるもので、修正の優先度を決めるための強いシグナルになります。Dependency-Track は 3 つの KEV カタログをミラーリングできます。どれも必須ではなく、3 つすべてをオンにすることが正しい選択であることはまれです。

このページでは、各データソースが提供する内容と、ミラーリングしたアサーションが脆弱性に紐付けられるしくみを説明します。データソースを有効にする手順については、[KEV データソースを設定する](../guides/administration/configuring-kev-sources.md)を参照してください。

## ミラーリングされるデータソース {#mirrored-sources}

Dependency-Track は 3 つの KEV カタログを自身のデータベースにミラーリングできます。

- **[CISA KEV](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)** はデフォルトでオンになっており、CVE ID で脆弱性を識別します。
- **[ENISA EU KEV](https://euvd.enisa.europa.eu/)** はデフォルトでオンになっており、CVE ID で脆弱性を識別します。この機関が CVE ID なしで公開するエントリーからは、KEV のアサーションは生成されません。
- **[VulnCheck KEV](https://docs.vulncheck.com/community/vulncheck-kev/introduction)** はコミュニティのカタログです。デフォルトではオフで、無料のコミュニティ API トークンが必要です。CISA KEV が漏らしている脆弱性をカバーし、悪用をより早く記録することがよくあります。CVE ID なしで公開されるエントリーからは、KEV のアサーションは生成されません。

### データソースを選ぶ {#picking-sources}

- CISA KEV と ENISA EU KEV は無料で、政府機関がキュレーションしており、デフォルトでオンになっているため、外向きのネットワークアクセス以外の設定は不要です。まずはこれらから始めてください。
- VulnCheck KEV は API トークンが必要ですが、より広く、より速いカバレッジが得られます。政府機関のデータソースだけにとどめることよりも修正の速さが重要な場合にオンにしてください。

## Dependency-Track がデータを使うしくみ {#how-dependency-track-uses-the-data}

ミラーリングはバックグラウンドタスクです。Dependency-Track は、設定可能なスケジュールに従って、有効な各データソースから現在のカタログをダウンロードし、アサーションを自身のデータベースに書き込みます。新しいデプロイでは、起動後まもなくタスクが 1 回実行されるため、最初のミラーリングはスケジュールを待ちません。その後の再起動ではミラーリングは開始されません。

KEV のステータスは、BOM のアップロードや分析の実行を待ちません。Dependency-Track は脆弱性の CVE ID でステータスを確認するため、定期的なミラーリングの実行や、データソースを初めてオンにすることで、他に何もしなくても、すでに見つかっている脆弱性が既知の悪用された脆弱性としてマークされることがあります。

### データソースをオフにする {#turning-a-source-off}

データソースをオフにすると、そのデータソースからのそれ以降のミラーリングは停止しますが、Dependency-Track はすでに書き込んだアサーションを保持し、クリーンアップしません。そのデータソースが既知の悪用された脆弱性としてフラグを付けた脆弱性は、フラグが付いたままになります。

## KEV の照合のしくみ {#how-kev-matching-works}

Dependency-Track は、KEV カタログのエントリーを、コンポーネントの情報ではなく CVE ID によって脆弱性と照合します。ポートフォリオ内の脆弱性が、有効な KEV カタログのエントリーと同じ CVE ID を持つ場合、Dependency-Track はその脆弱性に既知の悪用された脆弱性としてフラグを付けます。

これは、同じ脆弱性を異なる方法で記述しているデータソースの間でも機能します。たとえば Log4Shell は、NVD では `CVE-2021-44228`、GHSA では `GHSA-jfh8-c2jp-5v3q` です。Dependency-Track はこれらが[同じ脆弱性](about-vulnerability-data-sources.md#aliases-across-sources)であることを追跡しているため、`CVE-2021-44228` に対する CISA KEV のアサーションによって、両方のレコードに既知の悪用された脆弱性としてフラグが付きます。

照合は CPE や PURL ではなく CVE ID で行われるため、KEV のステータスはコンポーネントが持つ識別子に依存しません。必要なのは、Dependency-Track が任意の[脆弱性データソース](about-vulnerability-data-sources.md)から脆弱性の CVE ID を把握していることだけです。

## KEV のステータスが表示される場所 {#where-kev-status-appears}

Dependency-Track は、ポートフォリオの Vulnerabilities 一覧、プロジェクトの Findings ビューと EPSS ビュー、Vulnerability Audit ビューに **KEV** 列を表示します。表示する検出結果を絞り込むためのフィルターも利用できます。

![KEV で絞り込んだプロジェクトの検出結果](../assets/images/concepts/about-kev-data-sources/project-findings-filter.png)

フラグが付いた脆弱性には照準アイコンが表示され、選択すると各データソースのアサーションを一覧表示するモーダルが開きます。表示される内容は、アサーションを行ったカタログ、既知のランサムウェアでの使用を報告しているかどうか、カタログがエントリーを追加した日付、必要な修正措置(ある場合)、説明です。

![KEV アサーションのダイアログ](../assets/images/concepts/about-kev-data-sources/kev-assertions.png)

コンポーネントポリシーの条件は KEV のステータスで照合でき、コンポーネントが既知の悪用された脆弱性を持つ場合に違反を発生させられます。[条件式の例](../reference/policies/condition-expressions.md#known-exploited-vulnerabilities)を参照してください。

通知は、脆弱性のサブジェクトに KEV のステータスを含めます。[フィルター式](../reference/notifications/filter-expressions.md)を使うとアラートを既知の悪用された脆弱性に限定でき、[通知テンプレート](../reference/notifications/templating.md)を使うとパブリッシャーが送信するメッセージにフラグを出力できます。
