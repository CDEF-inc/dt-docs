# フィルター式

## はじめに {#introduction}

アラートにはフィルター式を含めることができ、通知の内容に基づいて、プラットフォームがどの通知を配信するかを制御できます。フィルター式は [CEL](../cel-expressions.md)(Common Expression Language)を使います。

フィルター式がない場合、アラートは、そのスコープ、グループ、レベル、およびプロジェクトやタグの制限を満たすすべての通知に一致します。フィルター式は条件をさらに追加します。プラットフォームは、式が `true` と評価された場合にのみ通知を配信します。

選択できるグループの一覧は[通知グループ](groups.md)を、プラットフォームがフィルターを適用する順序と評価の失敗を扱う方法については[アラートのフィルタリングのしくみ](../../concepts/notifications.md#how-alert-filtering-works)を参照してください。

![アラートエディターのフィルター式フィールド](../../assets/images/reference/notifications/filter-expressions/filter-expression-editor.png)

## 構文 {#syntax}

フィルター式は標準の [CEL の構文](../cel-expressions.md#syntax)を使います。CEL は[チューリング完全][Turing-complete]ではなく、`if` 文やループのような構文には対応していません。その代わりに、`all`、`exists`、`exists_one`、`map`、`filter` などの[マクロ][macros]が用意されています。

構文の詳しい説明については、公式の[言語定義][language definition]を参照してください。

## 評価コンテキスト {#evaluation-context}

式の評価コンテキストには、次の変数が含まれます。

| 変数        | 型                                                           | 説明                                                                                   |
|:------------|:-------------------------------------------------------------|:---------------------------------------------------------------------------------------|
| `level`     | [`Level`](schema.md#level)     | 整数の列挙値で表した通知レベル。名前付き定数を使います(後述)。      |
| `scope`     | [`Scope`](schema.md#scope)     | 整数の列挙値で表した通知スコープ。名前付き定数を使います(後述)。      |
| `group`     | [`Group`](schema.md#group)     | 整数の列挙値で表した通知グループ。名前付き定数を使います(後述)。      |
| `title`     | `string`                                                     | 通知のタイトル。                                                                |
| `content`   | `string`                                                     | 通知の内容。                                                              |
| `timestamp` | [`google.protobuf.Timestamp`][protobuf-ts-docs]              | 通知の作成日時。                                                        |
| `subject`   | dynamic                                                      | 通知のサブジェクト。通知グループに応じた型を持ちます(後述)。        |

### 列挙型の定数 {#enum-constants}

`level`、`scope`、`group` の各変数は整数値を保持します。これらを読みやすく比較するには、[通知スキーマ](schema.md#enums)の名前付き定数を使います。

```js
level == Level.LEVEL_INFORMATIONAL
```

```js
group == Group.GROUP_NEW_VULNERABILITY
```

```js
scope == Scope.SCOPE_PORTFOLIO
```

### サブジェクトの型 {#subject-types}

`subject` 変数は通知のサブジェクトを保持します。その型は通知グループによって異なります。グループとサブジェクトの対応については通知グループのリファレンスの[サブジェクト](groups.md#subjects)を、各サブジェクトのフィールドについては[通知スキーマのリファレンス](schema.md)を参照してください。

### 利用できる関数 {#available-functions}

通知フィルターでは、前述の表の変数と [CEL 標準ライブラリ](../cel-expressions.md#standard-library)を利用できます。このコンテキスト向けの独自関数はほかにありません。

## 検証 {#validation}

アラートを保存すると、そのフィルター式が検証されます。式に構文エラーがある場合や、存在しない型を参照している場合は保存が失敗し、レスポンスにエラーとその正確な位置(行と列)が示されます。

![無効なフィルター式に対する検証エラー](../../assets/images/reference/notifications/filter-expressions/filter-expression-editor-error.png)

フィルター式の長さの上限は 2048 文字です。

## 例 {#examples}

### 深刻度が Critical と High の脆弱性のみ {#only-critical-and-high-severity-vulnerabilities}

次の式は、脆弱性の深刻度が `CRITICAL` または `HIGH` の `NEW_VULNERABILITY` 通知に一致します。

```js linenums="1"
subject.vulnerability.severity in ["CRITICAL", "HIGH"]
```

### CVSS v3 スコアがしきい値を超える脆弱性 {#vulnerabilities-with-a-cvss-v3-score-over-a-threshold}

```js linenums="1"
subject.vulnerability.cvss_v3 >= 7.0
```

### 名前が特定のプレフィックスに一致するプロジェクトの通知 {#notifications-for-projects-matching-a-name-prefix}

次の式は、サブジェクトに名前が `acme-` で始まるプロジェクトを含む通知に一致します。

```js linenums="1"
subject.project.name.startsWith("acme-")
```

!!! tip
    単純なプロジェクト単位のフィルタリングであれば、代わりにアラートのプロジェクトとタグの制限を使うことを検討してください。フィルター式は、プロジェクトやタグの制限だけでは表現できない、内容に基づく条件に向いています。

### 特定の CWE を持つ脆弱性 {#vulnerabilities-with-a-specific-cwe}

次の式は、脆弱性の CWE に CWE-79(クロスサイトスクリプティング)が含まれる `NEW_VULNERABILITY` 通知に一致します。

```js linenums="1"
subject.vulnerability.cwes.exists(cwe, cwe.cwe_id == 79)
```

### 悪用が確認されている脆弱性 {#known-exploited-vulnerabilities}

次の式は、有効な [KEV データソース](../../concepts/about-kev-data-sources.md)が悪用を確認済みと報告している脆弱性の `NEW_VULNERABILITY` 通知に一致します。

```js linenums="1"
subject.vulnerability.is_kev
```

### 特定のポリシーへの違反 {#violations-of-a-specific-policy}

`POLICY_VIOLATION` 通知は、ポートフォリオ内のすべての[コンポーネントポリシー](../policies/component-policies.md)について発火します。次の式は、アラートの対象を名前で指定した 1 つのポリシーへの違反に絞り込みます。

```js linenums="1"
subject.policy_violation.condition.policy.name == "Known exploited vulnerabilities"
```

### 条件を組み合わせる {#combining-conditions}

次の式は、CVSSv3 の攻撃元区分がネットワークである `CRITICAL` 脆弱性の `NEW_VULNERABILITY` 通知に一致します。

```js linenums="1"
subject.vulnerability.severity == "CRITICAL"
  && subject.vulnerability.cvss_v3_vector.matches(".*/AV:N/.*")
```

### スケジュールされたアラート: Critical の脆弱性がある場合のみ {#scheduled-alerts-only-when-critical-vulnerabilities-exist}

脆弱性のサマリーを生成するスケジュールされたアラートでは、サブジェクトに深刻度ごとの脆弱性の件数をまとめた概要が含まれます。次の式は、報告期間に `CRITICAL` の脆弱性が 1 件以上含まれる場合にのみ一致します。

```js linenums="1"
"CRITICAL" in subject.overview.new_vulnerabilities_count_by_severity
```

### 任意フィールドの確認 {#optional-field-checking}

フィールドにアクセスする前に、`has()` マクロでフィールドの有無を確認します。その理由については、概説の[任意フィールドの確認](../cel-expressions.md#optional-field-checking)を参照してください。

```js linenums="1"
has(subject.vulnerability.cvss_v3_vector)
  && subject.vulnerability.cvss_v3_vector.matches(".*/AV:N/.*")
```

[Turing-complete]: https://en.wikipedia.org/wiki/Turing_completeness
[language definition]: https://github.com/google/cel-spec/blob/v0.13.0/doc/langdef.md#language-definition
[macros]: https://github.com/google/cel-spec/blob/v0.13.0/doc/langdef.md#macros
[protobuf-ts-docs]: https://protobuf.dev/reference/protobuf/google.protobuf/#timestamp
