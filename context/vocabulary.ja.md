# 日本語訳語集

日本語ページ(`*.ja.md`)で使う訳語と表記のルールです。用語の定義は [vocabulary.md](vocabulary.md) を参照してください。ここに載っていない用語を新たに訳した場合は、この表に追加してください。

## 表記のルール

- です・ます調で書きます。チュートリアルの "we" は訳さず、主語を省略します。
- 全角の句読点(、。)を使います。括弧とコロンは半角(`()`、`:`)を使い、括弧の前後に空白は入れません。
- 日本語と半角英数字の間には半角空白を入れます。ただし、句読点、括弧、リンクの角括弧の直前・直後には入れません。
- 数字は半角で書きます。数量の単位は「1 つ」「5 秒」のように数字の後に空白を入れます。
- カタカナ語の語末の長音は原則として付けます(サーバー、ユーザー、コンテナー、エディター、エントリー、インベントリー)。ただし慣用に従い、リポジトリ、ライブラリ、カテゴリは長音を付けません。
- UI ラベル(太字・斜体)は英語 UI の表記のまま残します。
- 列挙値(分析状態、深刻度、違反の状態、通知レベルなど)は英語のまま、UI やコードと同じ表記で書きます。
- 略語(BOM、SBOM、VEX、VDR、CVE、CVSS、EPSS、PURL、CPE、CEL、API、CI/CD など)と製品名・仕様名(CycloneDX、Hyades など)は訳しません。
- 未翻訳ページへのリンクテキストは、リンク先の英語タイトルのまま残します。

## 中核となるドメインモデル

| 英語 | 訳語 | 備考 |
|------|------|------|
| project | プロジェクト | |
| component | コンポーネント | コンポーネントの種類(*library* など)は英語のまま |
| service | サービス | |
| portfolio | ポートフォリオ | |
| finding | 検出結果 | 「所見」「発見」は使わない |

## 脆弱性と分析

| 英語 | 訳語 | 備考 |
|------|------|------|
| vulnerability | 脆弱性 | |
| vulnerability analysis | 脆弱性分析 | 自動の照合処理。手動のトリアージとは区別する |
| analyzer | アナライザー | |
| data source | データソース | 「フィード」「データベース」は使わない |
| mirroring | ミラーリング | |
| alias | エイリアス | |
| analysis state | 分析状態 | 値は英語のまま(*Not Affected* など) |
| justification | 根拠 | 値は英語のまま |
| suppression | 抑制 | 動詞は「抑制する」 |
| impact analysis | 影響分析 | |
| triage | トリアージ | |
| audit trail | 監査証跡 | |

## スコアリング

| 英語 | 訳語 | 備考 |
|------|------|------|
| severity | 深刻度 | 「重大度」は使わない。値は英語のまま(*Critical* など) |
| risk score | リスクスコア | |
| inherited risk | 継承されたリスク | |
| OWASP risk rating | OWASP リスク評価 | |

## 部品表(BOM)

| 英語 | 訳語 | 備考 |
|------|------|------|
| BOM (Bill of Materials) | BOM | 初出時は「部品表(BOM)」 |
| SBOM | SBOM | |
| BOM processing | BOM の処理 | |
| BOM upload | BOM のアップロード | |

## ポリシーエンジン

| 英語 | 訳語 | 備考 |
|------|------|------|
| policy | ポリシー | |
| policy condition | ポリシー条件 | 文脈が明らかなら「条件」 |
| policy violation | ポリシー違反 | 文脈が明らかなら「違反」 |
| violation state | 違反の状態 | 値は英語のまま(`INFO`、`WARN`、`FAIL`) |
| component policy | コンポーネントポリシー | |
| vulnerability policy | 脆弱性ポリシー | |
| license group | ライセンスグループ | |
| allow-list | 許可リスト | |
| condition expression | 条件式 | |

## 通知

| 英語 | 訳語 | 備考 |
|------|------|------|
| notification | 通知 | |
| notification scope | 通知スコープ | 値は英語のまま(*System*、*Portfolio*) |
| notification group | 通知グループ | 値は英語のまま(`BOM_PROCESSED` など) |
| notification level | 通知レベル | 値は英語のまま |
| alert | アラート | 「通知ルール」は使わない |
| publisher | パブリッシャー | |
| notification template | 通知テンプレート | |
| fire (an alert) | (アラートが)発火する | |

## アクセス制御

| 英語 | 訳語 | 備考 |
|------|------|------|
| team | チーム | |
| permission | 権限 | 値は英語のまま(`VIEW_PORTFOLIO` など) |
| API key | API キー | |
| team API key | チーム API キー | |
| managed user | 管理対象ユーザー | |
| service account | サービスアカウント | |
| portfolio access control | ポートフォリオのアクセス制御 | |
| identity provider | ID プロバイダー | |
| workload identity federation | ワークロード ID フェデレーション | |
| managed secret | 管理対象シークレット | |

## アーキテクチャ(v5)

| 英語 | 訳語 | 備考 |
|------|------|------|
| API server | API サーバー | コード中の `apiserver` は変更しない |
| frontend | フロントエンド | 「UI」「Web インターフェース」は使わない |
| durable execution engine | 永続実行エンジン | |
| workflow | ワークフロー | |
| activity | アクティビティ | |

## 連携

| 英語 | 訳語 | 備考 |
|------|------|------|
| repository | パッケージリポジトリ | Git リポジトリと区別する。文脈が明らかなら「リポジトリ」 |
| component currency | コンポーネントの鮮度 | |
| internal component | 内部コンポーネント | |
| private vulnerability | 非公開の脆弱性 | |

## ドキュメントの構成

| 英語 | 訳語 | 備考 |
|------|------|------|
| Tutorials | チュートリアル | |
| Guides | ガイド | |
| Concepts | コンセプト | |
| Reference | リファレンス | |
| What we need | 必要なもの | |
| What's next | 次のステップ | |
| What we just did | このチュートリアルで行ったこと | |
| Expected output | 想定される出力 | |
