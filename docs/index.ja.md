---
title: ホーム
hide:
- navigation
---

# Dependency-Track

Dependency-Track は、組織がソフトウェアサプライチェーンのリスクを特定し、低減するためのインテリジェントなコンポーネント分析プラットフォームです。

部品表(BOM)の概念を中心に設計されており、ポートフォリオ内のすべてのプロジェクトのすべてのバージョンにわたってコンポーネントの使用状況を追跡し、既知の脆弱性、ポリシー違反、ライセンスリスクを発生時点で明らかにします。API ファーストの設計のため、CI/CD パイプラインに自然に組み込めます。

!!! info "ドキュメントのバージョン"
    このドキュメントは Dependency-Track v5 を対象としています。v4 については [v4 のドキュメント](../../4.x/)を参照してください。

## 機能 {#features}

### 脆弱性の発見と優先順位付け {#find-and-rank-vulnerabilities}

- **継続的な監視**: Dependency-Track はポートフォリオを定期的に再分析するため、新たに公開された[脆弱性](concepts/vulnerability-findings.md)を、BOM を再アップロードしなくても検出できます。
- **複数のデータソース**: NVD、GitHub Advisories、OSV などの[ミラーリングされたデータソース](concepts/about-vulnerability-data-sources.md)と、Sonatype OSS Index、Snyk、Trivy、VulnDB などの[アナライザー](reference/analyzers.md)を組み合わせて利用できます。
- **リスクベースの優先順位付け**: CVSS の深刻度、EPSS による悪用予測、CISA、ENISA、VulnCheck の[既知の悪用された脆弱性カタログ](concepts/about-kev-data-sources.md)に基づいて検出結果をランク付けします。
- **ダッシュボードと推移**: ポートフォリオ全体、各プロジェクト、各コンポーネントのリスクスコアを[時系列](concepts/time-series-metrics.md)で追跡できます。
- **非公開の脆弱性**: [組織内で発見した問題](guides/user/managing-private-vulnerabilities.md)を、公開されている脆弱性と並べて管理できます。

### ソフトウェアの構成を把握 {#know-whats-in-your-software}

- **BOM のインポート**: あらゆるエコシステムやビルドツールで作成した [CycloneDX](reference/file-formats.md) BOM を、サービスや依存関係グラフも含めてアップロードできます。
- **ポートフォリオのインベントリー**: バージョン、階層、タグを使って[プロジェクトを整理](guides/user/organizing-projects.md)できます。
- **ポートフォリオ全体の検索**: 特定のコンポーネントを使用しているプロジェクトや、特定の脆弱性の影響を受けるプロジェクトをすべて検索できます。
- **古いコンポーネントの検出**: Maven Central、npm、PyPI などの[パッケージリポジトリ](reference/datasources/repositories.md)で新しいバージョンを確認し、[コンポーネントの完全性を検証](concepts/component-integrity-verification.md)できます。

### ポリシーの適用 {#enforce-policies}

- **ライセンスコンプライアンス**: [コンポーネントポリシー](concepts/component-policies.md)とライセンスグループを使って、組織で許可していないライセンスのコンポーネントを検出できます。
- **セキュリティと運用のルール**: 深刻度の高い脆弱性、古いコンポーネント、使用禁止のパッケージを検出できます。
- **カスタム条件**: 組み込みの条件で対応できない場合は、CEL で[条件式](reference/policies/condition-expressions.md)を記述できます。
- **違反のレビュー**: [ポリシー違反をトリアージ](guides/user/triaging-policy-violations.md)し、理由を記録したうえで承認、却下、抑制できます。

### トリアージと判断の共有 {#triage-and-share-decisions}

- **監査証跡**: 検出結果ごとに分析状態、根拠、コメントを記録し、その履歴を保持します。
- **自動トリアージ**: [脆弱性ポリシー](concepts/vulnerability-policies.md)を使ってポートフォリオ全体に判断を適用できます。中央のバンドルから配布することもできます。
- **VEX と VDR**: 顧客やサプライヤーと [VEX ドキュメントを交換](guides/user/exchanging-vex-documents.md)し、脆弱性開示レポートをエクスポートできます。

### 連携と自動化 {#integrate-and-automate}

- **API ファースト**: UI で行えるすべての作業を、[v1](reference/api/v1.md) と [v2](reference/api/v2.md) の REST API で自動化できます。
- **CI/CD**: 1 回の API 呼び出しで、どのパイプラインからでも [SBOM をアップロード](guides/user/uploading-boms.md)できます。初回アップロード時に、Dependency-Track がプロジェクトとバージョンを作成します。
- **通知**: リアルタイムのアラートや定期的なサマリーを[Slack、Microsoft Teams、Mattermost、Webex、メール、Jira、Webhook、Kafka](reference/notifications/publishers.md) に送信できます。
- **脆弱性管理プラットフォーム**: 検出結果を DefectDojo、Fortify SSC、Kenna Security に転送できます。
- **バッジ**: 管理者がバッジへのアクセスを有効にすると、[脆弱性とポリシーのバッジ](reference/badges.md)を README ファイルや社内ページに埋め込めます。
- **コミュニティによる連携**: Jenkins、GitHub Actions、Azure DevOps、Maven、Backstage などに対応した[プラグインとツール](reference/community-integrations.md)があります。

### アクセス制御 {#control-access}

- **ID プロバイダー**: [OIDC](guides/administration/configuring-oidc.md) または[LDAP](guides/administration/configuring-ldap.md) でサインインでき、チームの同期も設定できます。
- **チームと権限**: チームにきめ細かな権限を付与し、[ポートフォリオのアクセス制御](concepts/access-control.md)で各チームが参照できるプロジェクトを制限できます。
- **マシン ID**: パイプライン、スキャナー、スクリプトに専用の[サービスアカウント](concepts/access-control.md#service-accounts)を割り当て、個人のアカウントとは別に権限を管理できます。
- **キーレス認証**: [ワークロード ID フェデレーション](concepts/workload-identity-federation.md)により、GitHub Actions、GitLab CI、Kubernetes、SPIFFE のワークロードが各プラットフォームの短期間有効なトークンでサインインできます。API キーを保管したりローテーションしたりする必要はありません。
- **シークレットの一元管理**: [管理対象シークレット](guides/user/managing-secrets.md)を使って、連携用の認証情報を暗号化して 1 か所に保管できます。

### デプロイと運用 {#deploy-and-operate}

- **オープンソースかつセルフホスト**: Apache 2.0 ライセンスの下で無償で利用でき、自社のインフラストラクチャで稼働します。
- **最小限のインフラストラクチャ**: [コンテナイメージ](reference/container-images.md)を実行するだけで動作し、外部サービスとして必要なのは PostgreSQL のみです。
- **水平スケーリング**: ポートフォリオの拡大に応じて[インスタンスを追加](guides/administration/scaling.md)できます。たとえば [Kubernetes 上](guides/administration/deploying-to-kubernetes.md)で、ヘルスチェックと Prometheus メトリクスを利用して運用できます。
- **制限されたネットワーク**: [HTTP プロキシ](guides/administration/configuring-http-proxy.md)の背後や、[社内の認証局](guides/administration/configuring-internal-ca.md)を使う環境でも稼働します。
- **ローカライズされたインターフェース**: Web インターフェースは 15 言語に対応しています。

## はじめに {#getting-started}

[クイックスタートのチュートリアル](tutorials/quickstart.md)で、数分で Dependency-Track をローカルで起動できます。

ナビゲーションタブからドキュメントを参照してください。

- [チュートリアル](tutorials/index.md): 一般的なワークフローを順を追って説明します。
- [ガイド](guides/index.md): 特定の目的を達成するための手順を説明します。
- [コンセプト](concepts/index.md): Dependency-Track の仕組みに関する背景情報を説明します。
- [リファレンス](reference/index.md): API、設定、内部構造の技術的な説明です。

## 主要な概念 {#key-concepts}

- [プロジェクト](concepts/projects.md): Dependency-Track が追跡対象のソフトウェアをどのようにモデル化するか。
- [脆弱性の検出結果](concepts/vulnerability-findings.md): 既知の脆弱性がどのように検出され、トリアージされるか。
- [コンポーネントポリシー](concepts/component-policies.md): ポートフォリオで許容される内容をルールとして定義する方法。
- [アクセス制御](concepts/access-control.md): チーム、権限、プロジェクト階層。

## v4 から移行する場合 {#coming-from-v4}

変更点とその理由については [About changes in v5](concepts/changes-in-v5.md) を、1 回限りのデータ移行手順については [v4 から v5 に移行する](guides/administration/migrating-from-v4.md) を参照してください。

## コミュニティ {#community}

Dependency-Track は、コントリビューターのコミュニティによって維持されているオープンソースプロジェクトです。[毎月のコミュニティミーティング](https://github.com/DependencyTrack/community#community-meetings)に参加して、プロジェクトの最新情報を聞いたり、質問したり、他のユーザーやメンテナーと交流したりできます。
