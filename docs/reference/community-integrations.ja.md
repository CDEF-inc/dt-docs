# コミュニティによる連携

以下のツールと連携は、Dependency-Track の API ファーストの設計を基盤として、コミュニティによって作られたものです。これらは独立して保守されており、Dependency-Track プロジェクトによる公式のサポートはありません。

!!! note
    Dependency-Track の [REST API](api/v1.md) は、プラットフォームのすべての機能へのプログラムによるアクセスを提供します。そのため、ここに掲載されていないツールやワークフロー向けのカスタム連携も簡単に作れます。

## CI/CD とビルドシステムのプラグイン {#cicd-and-build-system-plugins}

これらのプラグインは、ビルドパイプラインの一部として、SBOM のアップロードと脆弱性ゲートの評価を自動化します。

| ツール | 連携 | リンク |
|:-----|:------------|:-----|
| Jenkins | Dependency-Track Jenkins Plugin | [jenkins.io](https://plugins.jenkins.io/dependency-track/) |
| GitHub | OWASP Dependency-Track Check GitHub Action | [GitHub Marketplace](https://github.com/marketplace/actions/owasp-dependency-track-check) |
| Azure DevOps | Azure DevOps Extension | [Visual Studio Marketplace](https://marketplace.visualstudio.com/) |
| Maven | `dependency-track-maven-plugin` | [GitHub](https://github.com/pmckeown/dependency-track-maven-plugin) |

## 開発者ポータル {#developer-portals}

| ツール | 連携 | リンク |
|:-----|:------------|:-----|
| Backstage | Dependency-Track Backstage Plugin (TRIMM) | [GitHub](https://github.com/TRIMM/plugin-dependencytrack) |

## クライアントライブラリ {#client-libraries}

このライブラリを使うと、独自のツールや自動化スクリプトから Dependency-Track API にプログラムでアクセスできます。

| 言語 | ライブラリ | リンク |
|:---------|:--------|:-----|
| Go | Dependency-Track Client | [GitHub](https://github.com/DependencyTrack/client-go) |

## セキュリティと脆弱性管理 {#security-and-vulnerability-management}

| ツール | 連携 | リンク |
|:-----|:------------|:-----|
| SecObserve | Dependency-Track との連携 | [GitHub](https://github.com/MaibornWolff/SecObserve) |
| SD Elements (Security Compass) | Dependency-Track との連携 | [securitycompass.com](https://securitycompass.com) |
| vens | インポート用に OWASP リスク評価を VEX に書き込む | [GitHub](https://github.com/venslabs/vens) |

## レポートと監査 {#reporting-and-auditing}

| ツール | 説明 | リンク |
|:-----|:------------|:-----|
| `dependency-track-exporter` | Prometheus メトリクスのエクスポーター(Jetstack) | [GitHub](https://github.com/jetstack/dependency-track-exporter) |

## その他のユーティリティ {#other-utilities}

| ツール | 説明 | リンク |
|:-----|:------------|:-----|
| dtapac | OPA による Dependency-Track 向けの Policy-as-code | [GitHub](https://github.com/nscuro/dtapac) |
| sbomify | SBOM の拡充と共有 | [sbomify.com](https://sbomify.com) |

---

*ここに掲載すべき連携をご存じでしたら、[ドキュメントのリポジトリ](https://github.com/DependencyTrack/docs)にプルリクエストを作成してください。*
