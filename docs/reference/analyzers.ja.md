# 脆弱性アナライザー

Dependency-Track には、次の脆弱性アナライザーが付属しています。各アナライザーは、管理用の UI から個別に有効化して設定できます。

!!! info "エイリアスの同期"
    一部のアナライザーは*エイリアスの同期*をサポートしています。脆弱性のエイリアスは、データベース間で同等の識別子を対応付けます。たとえば、CVE 識別子と、それに対応する GitHub Security Advisory(GHSA)の識別子です。エイリアスの同期を有効にすると、Dependency-Track はこれらの識別子を関連付けられるようになり、ソースをまたいで各脆弱性の全体像をより完全に把握できます。

## 内部 {#internal}

Dependency-Track 自身の脆弱性データベースとコンポーネントを照合します。これには、NVD、GitHub アドバイザリー、OSV などのソースからミラーリングした脆弱性が含まれます。内部アナライザーはデフォルトで有効です。

ミラーリングした各ソースが何を提供するか、照合がどのように行われるかといった背景については、[脆弱性データソースについて](../concepts/about-vulnerability-data-sources.md)を参照してください。

CPE と PURL の両方による照合を使用します。

!!! note
    内部アナライザーは外部のサービスとは通信しません。ローカルのデータベースにだけクエリーを発行します。

### 設定 {#configuration}

| オプション | 有効時に必須 | 説明 |
|---|---|---|
| Enabled | - | アナライザーを有効にするかどうか |

![内部アナライザーの設定](../assets/images/reference/analyzers/analyzer-config_internal.png)

!!! tip "データソースの設定"
    このアナライザーは完全に読み取り専用で動作するため、専用の[データソース](./configuration/datasources.md)を使用できます。これにより、メインのデータベースの負荷を軽減できます。

    これは [`dt.vuln-analyzer.internal.datasource.name`](./configuration/properties.md#dtvuln-analyzerinternaldatasourcename) を使って設定できます。インフラストラクチャーに関する事項であるため、UI からは設定できません。

## OSS Index {#oss-index}

脆弱性インテリジェンスとして [Sonatype OSS Index][oss-index] と連携します。

PURL による照合を使用します。次のエコシステムをサポートしています。

* `cargo`
* `cocoapods`
* `composer`
* `conan`
* `conda`
* `cran`
* `gem`
* `golang`
* `maven`
* `npm`
* `nuget`
* `pypi`
* `rpm`
* `swift`

### 設定 {#configuration_1}

| オプション | 有効時に必須 | 説明 |
|---|---|---|
| Enabled | - | アナライザーを有効にするかどうか |
| Alias sync enabled | - | 脆弱性のエイリアスを同期するかどうか |
| API URL | はい | OSS Index API のベース URL(デフォルト: `https://ossindex.sonatype.org`) |
| Username | はい | OSS Index アカウントのユーザー名 |
| API token | はい | OSS Index の API トークン。[管理対象シークレット][managed secret]である必要があります。 |

![OSS Index アナライザーの設定](../assets/images/reference/analyzers/analyzer-config_oss-index.png)

## Snyk {#snyk}

[Snyk][snyk] の脆弱性データベースと連携します。

PURL による照合を使用します。次のエコシステムをサポートしています。

* `cargo`
* `cocoapods`
* `composer`
* `gem`
* `generic`
* `hex`
* `golang`
* `maven`
* `npm`
* `nuget`
* `pypi`
* `swift`

### 設定 {#configuration_2}

| オプション | 有効時に必須 | 説明 |
|---|---|---|
| Enabled | - | アナライザーを有効にするかどうか |
| Alias sync enabled | - | 脆弱性のエイリアスを同期するかどうか |
| API base URL | はい | Snyk REST API のベース URL(デフォルト: `https://api.snyk.io`) |
| Organisation ID | はい | Snyk の組織の識別子 |
| API token | はい | Snyk の API トークン。[管理対象シークレット][managed secret]である必要があります。 |

![Snyk アナライザーの設定](../assets/images/reference/analyzers/analyzer-config_snyk.png)

## Trivy {#trivy}

脆弱性スキャンのために [Trivy][trivy] サーバーのインスタンスと連携します。

PURL による照合を使用します。

!!! warning
    Trivy には、別途デプロイした Trivy サーバーが必要です。Dependency-Track は Trivy サーバーのプロセスを同梱も管理もしません。

### 設定 {#configuration_3}

| オプション | 有効時に必須 | 説明 |
|---|---|---|
| Enabled | - | アナライザーを有効にするかどうか |
| API URL | はい | Trivy サーバーの URL |
| API token | - | Trivy サーバーの認証トークン。Trivy サーバーを `--token` 付きで実行している場合にだけ必要です。[管理対象シークレット][managed secret]である必要があります。 |
| Ignore unfixed | - | 既知の修正がない脆弱性を除外するかどうか |
| Scan library | - | 言語やライブラリのパッケージをスキャンします(デフォルトで有効) |
| Scan OS | - | OS レベルのパッケージをスキャンします(デフォルトで無効) |

![Trivy アナライザーの設定](../assets/images/reference/analyzers/analyzer-config_trivy.png)

!!! note
    [`dt.outbound.allowed-destinations`](configuration/properties.md#dtoutboundallowed-destinations) で Trivy サーバーを許可する必要があります。API URL のホスト名をそのまま追加してください。たとえば `trivy`、サイドカーの場合は `localhost` です。範囲内のすべてのアドレスを許可する `loopback` や `private` よりも、こちらを優先してください。

## VulnDB {#vulndb}

商用の脆弱性インテリジェンスサービスである [Flashpoint VulnDB][vulndb] と連携します。

CPE による照合を使用します。

### 設定 {#configuration_4}

| オプション | 有効時に必須 | 説明 |
|---|---|---|
| Enabled | - | アナライザーを有効にするかどうか |
| Alias sync enabled | - | 脆弱性のエイリアスを同期するかどうか |
| API URL | はい | VulnDB の API URL(デフォルト: `https://vulndb.flashpoint.io`) |
| OAuth 2.0 client ID | はい | 認証に使う OAuth 2.0 のクライアント ID |
| OAuth 2.0 client secret | はい | 認証に使う OAuth 2.0 のクライアントシークレット。[管理対象シークレット][managed secret]である必要があります。 |

![VulnDB アナライザーの設定](../assets/images/reference/analyzers/analyzer-config_vulndb.png)

[managed secret]: ../guides/user/managing-secrets.md
[oss-index]: https://ossindex.sonatype.org/
[snyk]: https://snyk.io/
[trivy]: https://trivy.dev/
[vulndb]: https://flashpoint.io/resources/datasheets/vulndb/
