# HTTP プロキシを設定する

Dependency-Track の API サーバーは、[脆弱性データソース](configuring-vulnerability-sources.md)のミラーリング、パッケージリポジトリからのパッケージメタデータの取得、OIDC ディスカバリー、Webhook の配信、その他の連携先への接続のために、外向きの HTTP および HTTPS 呼び出しを行います。外向きのトラフィックが社内プロキシを経由しなければならない環境では、これらの呼び出しをプロキシ経由でルーティングするように API サーバーを設定します。

プロキシの設定は API サーバーにのみ適用されます。フロントエンドは、ユーザーのブラウザーに配信される静的なシングルページアプリケーションです。フロントエンドが送信しているように見えるリクエストは、実際にはブラウザー自体から送信されています。

!!! note
    API サーバーがサポートするのはプレーンな HTTP プロキシ(オプションで `Basic` 認証付き)だけです。HTTPS で接続するプロキシと SOCKS プロキシは動作しません。

## 設定の読み込み元 {#configuration-sources}

API サーバーは、次の 2 つの読み込み元からこの順序でプロキシ設定を読み込みます。

1. アプリケーションプロパティ(`dt.http.proxy.*`)。
2. 標準の `HTTPS_PROXY`、`HTTP_PROXY`、`NO_PROXY` 環境変数。

`dt.http.proxy.host` に値が設定されている場合はアプリケーションプロパティが優先され、API サーバーは環境変数を無視します。それ以外の場合、API サーバーは環境変数にフォールバックします。

## アプリケーションプロパティで設定する {#configuring-via-app-properties}

次のプロパティを設定します(プロパティ名と環境変数の対応については[アプリケーションの設定](../../reference/configuration/application.md#environment-variable-mapping)を参照してください)。

- [`dt.http.proxy.host`](../../reference/configuration/properties.md#dthttpproxyhost): プロキシのホスト名または IP アドレス。
- [`dt.http.proxy.port`](../../reference/configuration/properties.md#dthttpproxyport): プロキシのポート。`dt.http.proxy.host` に値を設定する場合は必須です。
- [`dt.http.proxy.auth.username`](../../reference/configuration/properties.md#dthttpproxyauthusername): 認証付きプロキシの場合に指定します(省略可能)。
- [`dt.http.proxy.auth.password`](../../reference/configuration/properties.md#dthttpproxyauthpassword): 認証付きプロキシの場合に指定します(省略可能)。
- [`dt.http.proxy.exclusions`](../../reference/configuration/properties.md#dthttpproxyexclusions): カンマ区切りの回避リスト。

例:

```properties linenums="1"
dt.http.proxy.host=proxy.example.com
dt.http.proxy.port=8080
dt.http.proxy.exclusions=localhost,127.0.0.1,example.com
```

## 標準の環境変数で設定する {#configuring-via-standard-environment-variables}

アプリケーションプロパティが設定されていない場合、API サーバーはまず `HTTPS_PROXY` を読み込み、なければ `HTTP_PROXY` にフォールバックします。変数名は大文字と小文字を区別せずに照合されるため、小文字の形式(`https_proxy`、`http_proxy`、`no_proxy`)も使えます。

各値は `http://[user[:password]@]host[:port]` の形式で指定します。API サーバーは認証情報を URL デコードするため、ユーザー名やパスワードに予約文字が含まれる場合はパーセントエンコーディングが必要です。

```text
HTTPS_PROXY=http://proxy.example.com:8080
NO_PROXY=localhost,127.0.0.1,example.com
```

API サーバーは、上流への HTTP 呼び出しと HTTPS 呼び出しの両方に同じプロキシを使います。それ以外のスキーム(`ldap://` など)の URI は、常にプロキシを経由しません。

## 回避リスト {#bypass-list}

`dt.http.proxy.exclusions` と `NO_PROXY` は、どちらもカンマ区切りのエントリーのリストを受け付けます。各エントリーはホスト名または IP アドレスのいずれかで、オプションで `:port` を付けられます。CIDR 範囲、IP アドレス範囲、先頭にドットを付ける表記、プロトコルスキームはサポートされていません。

照合のルールは次のとおりです。

- `*` だけのエントリーを指定すると、すべての送信先でプロキシが無効になります。
- 大文字と小文字を区別せずに比較します。
- エントリーは、リクエストのホストに完全一致する場合、またはそのサブドメインに一致する場合に一致します。たとえば、`example.com` は `example.com` と `api.example.com` の両方に一致します。
- エントリーにポートが含まれる場合(`host:port`)、ホストが一致(完全一致またはサブドメイン)し、かつポートが完全に一致する必要があります。
- プロキシを経由するのは `http` と `https` の URI だけです。それ以外のスキームは常にプロキシを経由しません。

たとえば、`dt.http.proxy.exclusions=example.com,localhost:5432` の場合は次のようになります。

- `https://api.example.com/` はプロキシを経由しません(サブドメインに一致)。
- `https://localhost:5432/` はプロキシを経由しません(ホストとポートが一致)。
- `https://localhost:5433/` はプロキシを経由します(ポートが不一致)。

## 送信先を制限する {#restricting-destinations}

プロキシを使う場合、[`dt.outbound.allowed-destinations`](../../reference/configuration/properties.md#dtoutboundallowed-destinations) ではホスト名へのリクエストを止められません。ホスト名を解決するのは API サーバーではなくプロキシであるため、API サーバーはそれらをすべて通過させます。API サーバーがアクセスしてはならない送信先は、プロキシ側でブロックするように設定してください。

このプロパティは、引き続き次のものに適用されます。

- ホスト名ではなく IP アドレスを使う URL。
- [回避リスト](#bypass-list)に含まれるホスト(API サーバーが直接接続するため)。

## 認証付きプロキシ {#authenticated-proxies}

`dt.http.proxy.auth.username` と `dt.http.proxy.auth.password` を設定します。[ファイルから値を読み込む](../../reference/configuration/application.md#loading-values-from-files)を使って、パスワードを平文で保持しないようにしてください。

一部の古い Microsoft のプロキシは、ドメイン名で修飾された `Basic` 認証情報を受け付けます。ユーザー名を `domain\username` の形式で指定します(`HTTPS_PROXY` では、バックスラッシュを `%5C` にパーセントエンコーディングします)。この場合も通信上は `Basic` 認証であり、NTLM *ではありません*。

## NTLM プロキシと Kerberos プロキシ {#ntlm-and-kerberos-proxies}

サポートされていません。上流で認証を行い、`Basic` 認証(または認証なし)のリスナーを公開する [cntlm] や [px] などのローカルブリッジを実行し、Dependency-Track の接続先をそのブリッジに向けてください。

## TLS を傍受するプロキシの証明書を信頼する {#trusting-an-intercepting-proxys-certificate}

プロキシが TLS 接続を終端して再発行する場合、API サーバーはプロキシの認証局を信頼する必要があります。[社内 CA の信頼を設定する](configuring-internal-ca.md)を参照してください。

[cntlm]: https://cntlm.sourceforge.net/
[px]: https://github.com/genotrance/px
