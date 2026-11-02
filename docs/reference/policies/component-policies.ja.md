# コンポーネントポリシー

コンポーネントポリシーのフィールド単位のリファレンスです。背景については[コンポーネントポリシーについて](../../concepts/component-policies.md)を、手順については[コンポーネントポリシーを管理する](../../guides/user/managing-component-policies.md)を参照してください。

## 演算子 {#operator}

| 演算子 | 動作 |
|:---|:---|
| `ANY` | 少なくとも 1 つの条件がコンポーネントに一致した場合に違反を発生させます。デフォルトです。 |
| `ALL` | すべての条件がコンポーネントに一致した場合にだけ違反を発生させます。 |

## 違反の状態 {#violation-states}

ポリシーが発生させるすべての違反は、ポリシーの状態を引き継ぎます。この状態は、バッジ、プロジェクトのメトリクス、通知、CI/CD のゲートに使われます。

| 状態 | 一般的な用途 |
|:---|:---|
| `INFO` | 情報。プロジェクトの合否に影響を与えずに違反を表面化させます。 |
| `WARN` | 警告。メトリクスと通知に表示されます。 |
| `FAIL` | 失敗。プロジェクトのバッジと REST API が CI/CD のチェックをゲートするために使います。 |

## 条件のサブジェクト {#condition-subjects}

各条件は `subject`、`operator`、`value` を持ちます。サブジェクトによって、[違反の種類](#violation-types)と適用できる演算子が決まります。

以下の `NUMERIC_*` は、`NUMERIC_GREATER_THAN`、`NUMERIC_LESS_THAN`、`NUMERIC_EQUAL`、`NUMERIC_NOT_EQUAL`、`NUMERIC_GREATER_THAN_OR_EQUAL`、`NUMERIC_LESSER_THAN_OR_EQUAL` を表します。

!!! note "非同期に取り込まれるデータ"
    [`AGE`](#age)、[`VERSION_DISTANCE`](#version_distance)、[`EPSS`](#epss) の条件、および同じデータを読み取る [`EXPRESSION`](#expression) の条件への入力は、BOM のアップロード後の最初の評価の時点ではまだ存在しない場合があります。[コンポーネントポリシーについて](../../concepts/component-policies.md#lifecycle)を参照してください。

### `AGE` {#age}

- **違反の種類:** 運用
- **演算子:** `NUMERIC_*`
- **値:** ISO 8601 の期間(たとえば `P30D`、`P1Y`)。

コンポーネントの公開日と比較します。

### `COMPONENT_HASH` {#component_hash}

- **違反の種類:** 運用
- **演算子:** アルゴリズムの選択(演算子のフィールドにハッシュアルゴリズムを指定します)
- **値:** JSON `{ "algorithm": "<alg>", "value": "<hash>" }`。

サポートしているアルゴリズム: `MD5`、`SHA-1`、`SHA-256`/`384`/`512`、`SHA3-256`/`384`/`512`、`BLAKE2b-256`/`384`/`512`、`BLAKE3`。

### `COORDINATES` {#coordinates}

- **違反の種類:** 運用
- **演算子:** `MATCHES`、`NO_MATCH`
- **値:** JSON `{ "group": "<re>", "name": "<re>", "version": "<re>" }`。

各フィールドは、コンポーネントの対応する座標に対する正規表現です。

### `CPE` {#cpe}

- **違反の種類:** セキュリティ
- **演算子:** `MATCHES`、`NO_MATCH`
- **値:** コンポーネントの CPE 文字列に対する正規表現。

### `CWE` {#cwe}

- **違反の種類:** セキュリティ
- **演算子:** `CONTAINS_ANY`、`CONTAINS_ALL`
- **値:** カンマ区切りの CWE ID(たとえば `CWE-79, CWE-89`)。

コンポーネントの脆弱性の CWE と照合します。

### `EPSS` {#epss}

- **違反の種類:** セキュリティ
- **演算子:** `NUMERIC_*`
- **値:** `0.0` から `1.0` までの数値。

コンポーネントの脆弱性のうち最も高い EPSS スコアと照合します。

### `EXPRESSION` {#expression}

- **違反の種類:** 条件で明示的に選択します(`LICENSE`、`OPERATIONAL`、`SECURITY` のいずれか)
- **演算子:** なし
- **値:** スコープ内のすべてのコンポーネントに対して評価される [CEL](../cel-expressions.md) 式。式が `true` と評価された場合に条件が一致します。

利用できる変数、カスタム関数([`spdx_expr_allows`](condition-expressions.md#spdx_expr_allows)、[`is_dependency_of`](condition-expressions.md#is_dependency_of)、[`matches_range`](condition-expressions.md#matches_range)、[`version_distance`](condition-expressions.md#version_distance) を含む)、実例については、[条件式](condition-expressions.md)を参照してください。

### `LICENSE` {#license}

- **違反の種類:** ライセンス
- **演算子:** `IS`、`IS_NOT`
- **値:** ライセンスの UUID、または解決済みのライセンスがないコンポーネントに一致させるためのリテラル `unresolved`。

### `LICENSE_GROUP` {#license_group}

- **違反の種類:** ライセンス
- **演算子:** `IS`、`IS_NOT`
- **値:** ライセンスグループの UUID。

### `PACKAGE_URL` {#package_url}

- **違反の種類:** 運用
- **演算子:** `MATCHES`、`NO_MATCH`
- **値:** コンポーネントのパッケージ URL(PURL)に対する正規表現。

### `SEVERITY` {#severity}

- **違反の種類:** セキュリティ
- **演算子:** `IS`、`IS_NOT`
- **値:** `CRITICAL`、`HIGH`、`MEDIUM`、`LOW`、`INFO`、`UNASSIGNED` のいずれか。

コンポーネントの脆弱性の深刻度と照合します。

### `SWID_TAGID` {#swid_tagid}

- **違反の種類:** 運用
- **演算子:** `MATCHES`、`NO_MATCH`
- **値:** コンポーネントの SWID タグ ID に対する正規表現。

### `VERSION` {#version}

- **違反の種類:** 運用
- **演算子:** `NUMERIC_*`
- **値:** バージョン文字列。エコシステムに応じたバージョンのセマンティクスで比較します。

### `VERSION_DISTANCE` {#version_distance}

- **違反の種類:** 運用
- **演算子:** `NUMERIC_*`
- **値:** JSON [`VersionDistance`](schema.md#versiondistance): `{ "epoch": n, "major": n, "minor": n, "patch": n }`。

### `VULNERABILITY_ID` {#vulnerability_id}

- **違反の種類:** セキュリティ
- **演算子:** `IS`、`IS_NOT`
- **値:** 脆弱性の識別子(たとえば `CVE-2021-44228`)。

## 違反の種類 {#violation-types}

条件のサブジェクトによって、条件が一致したときに記録される違反の種類が決まります。

| 種類 | サブジェクト |
|:---|:---|
| `LICENSE` | [`LICENSE`](#license)、[`LICENSE_GROUP`](#license_group) |
| `OPERATIONAL` | [`AGE`](#age)、[`COMPONENT_HASH`](#component_hash)、[`COORDINATES`](#coordinates)、[`PACKAGE_URL`](#package_url)、[`SWID_TAGID`](#swid_tagid)、[`VERSION`](#version)、[`VERSION_DISTANCE`](#version_distance) |
| `SECURITY` | [`CPE`](#cpe)、[`CWE`](#cwe)、[`EPSS`](#epss)、[`SEVERITY`](#severity)、[`VULNERABILITY_ID`](#vulnerability_id) |
| (明示) | [`EXPRESSION`](#expression)(条件自体が違反の種類を指定します)。 |

## 割り当て {#assignment}

次のいずれかが成り立つ場合、ポリシーはプロジェクトに適用されます。

- ポリシーにプロジェクトもタグも割り当てられていない。この場合、ポリシーはポートフォリオ全体に適用されます。
- プロジェクトがポリシーの `projects` リストに含まれている、または `includeChildren` が有効になっている、リスト内のプロジェクトの子孫である。
- プロジェクトに、ポリシーの `tags` に含まれるタグが付いている。

## 評価 {#evaluation}

プロジェクトの分析は、BOM のアップロード時、スケジュールされたポートフォリオ分析の実行中、および手動のトリガー時にポリシーを評価します。照合のモデルについては、[コンポーネントポリシーについて](../../concepts/component-policies.md#lifecycle)を参照してください。

## 権限 {#permissions}

関連する権限は、ポリシーの編集には `POLICY_MANAGEMENT`(およびより細かい `_CREATE`、`_READ`、`_UPDATE`、`_DELETE` のバリアント)、違反の閲覧には `VIEW_POLICY_VIOLATION`、違反のトリアージには `POLICY_VIOLATION_ANALYSIS` です。完全な一覧については、[権限のリファレンス](../permissions.md)を参照してください。
