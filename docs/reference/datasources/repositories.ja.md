# パッケージリポジトリ

Dependency-Track は、公開および非公開のパッケージリポジトリと連携してコンポーネントのメタデータを取得します。この連携は主に古くなったコンポーネントの検出に使われます。Dependency-Track はレジストリにコンポーネントの最新の利用可能なバージョンを照会し、SBOM 内のバージョンと比較します。

## サポートされているエコシステム {#supported-ecosystems}

以下のエコシステムが標準でサポートされており、それぞれにデフォルトのリポジトリがあらかじめ設定されています。

| エコシステム | デフォルトのリポジトリ |
|:----------|:------------------|
| Cargo (Rust) | [crates.io](https://crates.io) |
| Composer (PHP) | [Packagist](https://packagist.org) |
| Gem (Ruby) | [RubyGems](https://rubygems.org) |
| GitHub (Actions) | [github.com](https://github.com) |
| Go Modules | [proxy.golang.org](https://proxy.golang.org) |
| Hex (Erlang/Elixir) | [Hex.pm](https://hex.pm) |
| Maven (Java) | [Maven Central](https://central.sonatype.com) |
| npm (Node.js) | [npmjs.com](https://www.npmjs.com) |
| NuGet (.NET) | [nuget.org](https://www.nuget.org) |
| PyPI (Python) | [pypi.org](https://pypi.org) |
| CPAN (Perl) | [CPAN](https://www.cpan.org) |

**Administration → Repositories** で、任意のエコシステムに追加のリポジトリを設定できます。

## 設定 {#configuration}

リポジトリの設定は **Administration → Repositories** で管理します。各リポジトリのエントリーには次のプロパティがあります。

| プロパティ | 説明 |
|:---------|:------------|
| Enabled | 分析の際にこのリポジトリを照会するかどうか。無効なリポジトリはスキップされます。 |
| Internal | 内部(非公開)のレジストリかどうか。内部リポジトリは、内部としてマークされたコンポーネントに*のみ*使われます。内部ではないリポジトリは、内部ではないコンポーネントにのみ使われます。 |
| URL | リポジトリのベース URL。 |
| Authentication | 任意の認証情報(下記を参照)。 |

## 認証 {#authentication}

サポートされている認証方式は 3 つあります。

| 方式 | 設定 |
|:-------|:-------------|
| None | 認証情報は不要です(公開リポジトリのデフォルト)。 |
| Basic | ユーザー名とパスワードを入力します。 |
| Bearer token | ユーザー名を空欄のままにし、パスワードのフィールドにトークンを入力します。 |

GitHub の場合は、GitHub のユーザー名と、少なくとも公開読み取りアクセス権を持つ[個人用アクセストークン](https://github.com/settings/tokens)を使用します。

Azure Artifacts や JFrog Artifactory などの非公開リポジトリの場合は、適切なサービスアカウントの認証情報を使用します。

## Dependency-Track によるリポジトリの使い方 {#how-dependency-track-uses-repositories}

Dependency-Track は、各コンポーネントの Package URL(PURL)を使ってそのコンポーネントが属するエコシステムを判断し、一致するリポジトリに最新の公開バージョンを照会します。コンポーネントのバージョンが最新より古い場合は、古くなったものとしてフラグが付けられます。

!!! note
    リポジトリへの照会は、バージョンの鮮度チェックにのみ使われます。脆弱性分析のパイプラインの一部ではありません。脆弱性データは、[内部アナライザー](../analyzers.md)と外部アナライザーとの連携から取得されます。

## 内部コンポーネントとリポジトリ {#internal-components-and-repositories}

[内部](internal-components.md)としてマークされたコンポーネントは、同じく内部としてマークされたリポジトリとのみ照合されます。これにより、内部パッケージの座標が外部のレジストリ API に漏れることを防ぎます。
