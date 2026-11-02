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
| collection project | コレクションプロジェクト |  |
| hierarchy / parent / child | 階層 / 親 / 子 |  |
| tag | タグ |  |
| latest version | 最新バージョン | 「最新としてマークする」 |
| retire (a version) | 廃止する |  |
| component inventory | コンポーネントインベントリー |  |

## 脆弱性と分析

| 英語 | 訳語 | 備考 |
|------|------|------|
| vulnerability | 脆弱性 | |
| vulnerability analysis | 脆弱性分析 | 自動の照合処理。手動のトリアージとは区別する |
| analyzer | アナライザー | |
| data source | データソース | 「フィード」「データベース」は使わない。英語が feed と書いている箇所は「フィード」 |
| mirroring | ミラーリング | |
| alias | エイリアス | |
| analysis state | 分析状態 | 値は英語のまま(*Not Affected* など) |
| justification | 根拠 | 値は英語のまま |
| suppression | 抑制 | 動詞は「抑制する」 |
| impact analysis | 影響分析 | |
| triage | トリアージ | |
| audit trail | 監査証跡 | |
| decision (triage, VEX) | 判断 |  |
| statement (VEX) | ステートメント |  |

## スコアリング

| 英語 | 訳語 | 備考 |
|------|------|------|
| severity | 深刻度 | 「重大度」は使わない。値は英語のまま(*Critical* など) |
| risk score | リスクスコア | |
| inherited risk | 継承されたリスク | |
| OWASP risk rating | OWASP リスク評価 | |
| rating (CVSS, vulnerability) | レーティング | 「評価」は evaluate に使う |
| rating override | レーティングの上書き |  |

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
| policy evaluation | ポリシー評価 |  |
| operator (policy) | 演算子 | UI ラベルとしては英語のまま |
| subject (condition) | サブジェクト |  |
| bundle (vulnerability policy) | バンドル |  |

## 通知

| 英語 | 訳語 | 備考 |
|------|------|------|
| notification | 通知 | |
| notification scope | 通知スコープ | 値は英語のまま(*System*、*Portfolio*) |
| notification group | 通知グループ | 値は英語のまま(`BOM_PROCESSED` など) |
| notification level | 通知レベル | 値は英語のまま |
| alert | アラート | 「通知ルール」は使わない。英語が DB や API の notification rule を指す場合のみ「通知ルール」 |
| publisher | パブリッシャー | |
| notification template | 通知テンプレート | |
| fire (an alert) | (アラートが)発火する | |
| trigger | トリガー | 値は英語のまま(*Event*、*Schedule*) |
| subscribe | サブスクライブする |  |
| destination | 送信先 |  |
| filter expression | フィルター式 |  |
| digest | ダイジェスト |  |

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
| secret | シークレット |  |
| credentials | 認証情報 |  |
| access token | アクセストークン |  |
| identity provider (IdP) | ID プロバイダー(IdP) |  |
| issuer / audience / trust domain | 英語のまま | OIDC・ワークロード ID のプロトコル用語 |
| claim | クレーム |  |
| redirect URI | リダイレクト URI |  |
| user provisioning | ユーザーのプロビジョニング |  |
| team synchronization | チームの同期 |  |
| distinguished name (DN) | 識別名(DN) |  |
| certificate authority (CA) | 認証局(CA) | internal CA は「社内 CA」 |
| truststore | トラストストア |  |
| envelope encryption | エンベロープ暗号化 |  |
| data encryption key (DEK) / key encryption key (KEK) | データ暗号化鍵(DEK) / 鍵暗号化鍵(KEK) | 「キー」ではなく「鍵」 |
| keyset | キーセット |  |
| key rotation | 鍵のローテーション |  |

## アーキテクチャ(v5)

| 英語 | 訳語 | 備考 |
|------|------|------|
| API server | API サーバー | コード中の `apiserver` は変更しない |
| frontend | フロントエンド | 「UI」「Web インターフェース」は使わない |
| durable execution engine | 永続実行エンジン | |
| workflow | ワークフロー | |
| activity | アクティビティ | |
| workflow run / workflow instance | ワークフロー実行 / ワークフローインスタンス |  |
| replay | リプレイ |  |
| deterministic | 決定的 |  |
| side effect | 副作用 |  |
| idempotent | べき等 | 「冪等」は使わない |
| transactional outbox | トランザクショナルアウトボックス |  |
| leader election / lease | リーダー選出 / リース |  |
| concurrency control / concurrency key | 同時実行制御 / 同時実行キー |  |
| coordination | 協調 | 「連携」は integrations に使う |
| extension point / extension | 拡張ポイント / 拡張 |  |
| plugin | プラグイン |  |
| retry / retry policy | 再試行 / 再試行ポリシー |  |
| exponential backoff | 指数バックオフ |  |
| init tasks | 初期化タスク |  |
| management server | 管理サーバー |  |
| health probe / startup probe | ヘルスプローブ / 起動プローブ |  |
| scrape (metrics) | スクレイプ |  |
| observability | オブザーバビリティ |  |
| connection pool / pooling | コネクションプール / コネクションプーリング | 「接続プール」は使わない |
| task queue | タスクキュー |  |
| throughput / latency | スループット / レイテンシー |  |
| backpressure | バックプレッシャー |  |
| rolling upgrade | ローリングアップグレード |  |
| schema migration | スキーマのマイグレーション |  |
| materialized view | マテリアライズドビュー |  |
| air-gapped | エアギャップ環境 |  |
| soft-delete | 論理削除 |  |

## 連携

| 英語 | 訳語 | 備考 |
|------|------|------|
| repository | パッケージリポジトリ | Git リポジトリと区別する。文脈が明らかなら「リポジトリ」 |
| component currency | コンポーネントの鮮度 | |
| internal component | 内部コンポーネント | |
| private vulnerability | 非公開の脆弱性 | |
| GitHub Advisories | GitHub アドバイザリー | 製品名として並べる場合は GitHub Advisories |
| KEV catalog | KEV カタログ |  |
| migrator (v4-migrator) | 移行ツール |  |
| cutover | 切り替え |  |
| staging schema | ステージングスキーマ |  |
| preflight | 事前チェック |  |
| deduplication | 重複排除 |  |
| upstream | 上流 | 「アップストリーム」は使わない |
| advisory | アドバイザリー |  |
| registry | レジストリ |  |
| provenance | 来歴情報 |  |
| attribution (finding) | 帰属情報 |  |
| integrity verification | 完全性検証 |  |
| extract / transform / load | 抽出 / 変換 / ロード | サブコマンド名は英語のまま |

## 一般的な用語

| 英語 | 訳語 | 備考 |
|------|------|------|
| clone | クローン、クローンする | |
| retention | 保持 | |
| sync | 同期 | |
| resolve | 解決する | |
| suppress (a notification) | 送信しない | 「抑制」は脆弱性の suppression に限る |
| supplier | サプライヤー | |
| third party | 第三者 | 製品・システムを指す場合は「サードパーティ」 |
| toggle on / off | オンにする / オフにする | |

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
| Prerequisites | 前提条件 |  |
| Further reading | 関連項目 | See also と同じ |
| References | 参考文献 |  |
| See also | 関連項目 |  |
