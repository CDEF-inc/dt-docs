# エアギャップ環境で運用する

Dependency-Track はインターネットへの送信アクセスがない環境でも運用できますが、通常は公開エンドポイントにアクセスする連携のそれぞれに代替手段が必要です。このガイドでは、関連する考慮事項をまとめます。

!!! warning "未完成"
    このガイドは作成中です。現時点では、脆弱性データソースと脆弱性アナライザーを扱っています。その他のアプリケーション領域(通知、古いコンポーネントの検出に使うパッケージリポジトリのメタデータ)もデフォルトでは公開インターネットにアクセスします。これらは内容が書かれ次第、ここに記載します。エアギャップ環境のデプロイメントがこれらの領域のいずれかに依存している場合は、このガイドを完全なチェックリストではなく出発点として扱ってください。

ネットワークが送信トラフィックをプロキシ経由でのみルーティングしている場合は、完全なエアギャップ構成は不要かもしれません。まず [HTTP プロキシを設定する](configuring-http-proxy.md)と[社内 CA の信頼を設定する](configuring-internal-ca.md)を参照してください。

## 脆弱性データソース {#vulnerability-data-sources}

ミラーリングされる 3 つのデータソースの背景と有効にする方法については、[脆弱性データソースを設定する](configuring-vulnerability-sources.md)を参照してください。エアギャップ環境での対応方法は、データソースごとに異なります。

### NVD {#nvd}

[NVD JSON 2.0 フィードのレイアウト](https://nvd.nist.gov/vuln/data-feeds#divJson20Feeds)に一致するファイルを、社内の HTTP ファイルサーバーでホストします。Dependency-Track には `META` ファイルと `GZ` ファイルが必要です。`ZIP` ファイルは必要ありません。

NVD データソースのフィード URL を社内のミラーに向けてから、NVD の設定パネルの **Test** アクションを使って、ミラーに到達でき、想定どおりのレイアウトでファイルを提供していることを確認します。

### OSV {#osv}

[OSV のデータダンプ](https://google.github.io/osv.dev/data/#data-dumps)を社内の HTTP ファイルサーバーでホストします。Dependency-Track は、エコシステムごとの `all.zip` ファイルを想定しています。また、増分ミラーリングには `modified_id.csv` が必要です。増分ミラーリングをオフにすると、Dependency-Track は実行のたびにダンプ全体を再ダウンロードします。

OSV データソースのベース URL を社内のミラーに向けます。

### GitHub アドバイザリー {#github-advisories}

GitHub アドバイザリーの連携は、GitHub のページネーション付き GraphQL API を使います。静的な HTTP ミラーでは提供できません。HTTP フォワードプロキシ経由で転送すると動作する可能性がありますが、テストされていません。

厳格なエアギャップ環境では、GitHub アドバイザリーのデータソースをオフにしてください。代わりに、オープンソースのカバレッジには OSV を使います。OSV は他のキュレーターのアドバイザリーとともに GitHub アドバイザリーも取り込むため、OSV だけに頼っても GHSA で始まるレコードが失われることはありません。

## 脆弱性アナライザー {#vulnerability-analyzers}

[内部アナライザー](../../reference/analyzers.md#internal)はエアギャップ環境でも安全です。ローカルの脆弱性データベースにだけ問い合わせ、分析中に外部への通信を行わないため、上記の対応する[脆弱性データソース](#vulnerability-data-sources)を設定していれば動作します。

もう 1 つの実用的な選択肢は [Trivy](../../reference/analyzers.md#trivy) です。Trivy サーバー自体は、脆弱性データベースを事前に社内のストレージから読み込むことで、エアギャップ環境での運用をサポートしています。セットアップについては、[Trivy のエアギャップ環境ガイド](https://trivy.dev/docs/latest/guide/advanced/air-gap/)を参照してください。Dependency-Track は自分で運用する Trivy サーバーとだけ通信するため、API サーバーから Trivy サーバーに到達できれば、アナライザーは動作します。

[OSS Index](../../reference/analyzers.md#oss-index)、[Snyk](../../reference/analyzers.md#snyk)、[VulnDB](../../reference/analyzers.md#vulndb) の各アナライザーは、分析を実行するたびにベンダーがホストする API を呼び出すため、それらのエンドポイントへの送信接続が必要です。キャッシュプロキシ経由でルーティングすると動作する可能性がありますが、テストされていません。厳格なエアギャップ環境では、これらのアナライザーをオフにしてください。

## 関連項目 {#see-also}

- [脆弱性データソースを設定する](configuring-vulnerability-sources.md)
- [HTTP プロキシを設定する](configuring-http-proxy.md)
- [社内 CA の信頼を設定する](configuring-internal-ca.md)
