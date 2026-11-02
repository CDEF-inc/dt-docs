# CEL 式

Dependency-Track は [Common Expression Language] (CEL) を 3 つの場所で使用します。

* **ポリシー条件**: コンポーネントまたは脆弱性を対象に評価され、ポリシー違反と分析を決定します。[条件式](policies/condition-expressions.md)を参照してください。
* **通知フィルター**: 通知のサブジェクトを対象に評価され、どの通知を送信するかを制御します。[フィルター式](notifications/filter-expressions.md)を参照してください。
* **ワークロード ID のバインディング条件**: 検証済みのプラットフォームトークンのクレームを対象に評価され、ワークロードがサービスアカウントとして動作してよいかどうかを判断します。5.2.0 以降で利用できます。[ワークロード ID](workload-identity.md#condition-environment)を参照してください。

これらのコンテキストはこのページで説明する構文を共有しますが、公開する**変数、型、カスタム関数は異なります**。ポリシー向けに説明しているカスタム関数(`depends_on`、`spdx_expr_allows` など)は、通知フィルターやバインディング条件では使用できず、変数もまったく異なります。利用できる入力と関数については、各コンテキストのページを参照してください。

## 構文 {#syntax}

CEL の構文は、Java や JavaScript などの他の [C 系言語][C-style languages]に似ています。ただし、CEL は[チューリング完全][Turing-complete]ではありません。そのため、`if` 文やループ(`for`、`while`)のような構文はサポート*していません*。

ループがない代わりに、CEL には `all`、`exists`、`exists_one`、`map`、`filter` などの[マクロ][macros]があります。詳しくは[マクロ][macros]のドキュメントを参照してください。

CEL の構文は、公式の[言語定義][language definition]で詳しく説明されています。

## 標準ライブラリ {#standard-library}

どちらのコンテキストでも、CEL 仕様の[標準定義][standard definitions]と [CEL 文字列拡張][CEL strings extension]を利用できます。CEL 文字列拡張は、`charAt`、`indexOf`、`join`、`lowerAscii`、`replace`、`split`、`substring`、`trim`、`upperAscii` などの関数を追加します。

ポリシーのコンテキストは、追加のカスタム関数(`depends_on`、`spdx_expr_allows` など)を登録します。[条件式](policies/condition-expressions.md#function-reference)を参照してください。通知フィルターとワークロード ID のバインディング条件は、カスタム関数を登録しません。

## オプションフィールドのチェック {#optional-field-checking}

CEL には `null` の概念がありません。設定されていないフィールドにアクセスすると、そのデフォルト値(たとえば、文字列なら `""`、数値なら `0`、真偽値なら `false`)が返されるため、誤った一致につながる可能性があります。フィールドにアクセスする前に、`has()` マクロを使ってフィールドが存在するかどうかを確認してください。

```js linenums="1"
has(obj.field) && obj.field == "value"
```

`has()` マクロは 3 つのコンテキストすべてで使用できます。正確なルート変数(`component`、`subject`、`claims` など)は、各コンテキストのリファレンスページで説明しています。

[C-style languages]: https://en.wikipedia.org/wiki/List_of_C-family_programming_languages
[CEL strings extension]: https://github.com/google/cel-spec/blob/master/doc/extensions/strings.md
[Common Expression Language]: https://cel.dev/
[Turing-complete]: https://en.wikipedia.org/wiki/Turing_completeness
[language definition]: https://github.com/google/cel-spec/blob/v0.13.0/doc/langdef.md#language-definition
[macros]: https://github.com/google/cel-spec/blob/v0.13.0/doc/langdef.md#macros
[standard definitions]: https://github.com/google/cel-spec/blob/v0.13.0/doc/langdef.md#list-of-standard-definitions
