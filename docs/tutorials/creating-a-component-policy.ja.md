# コンポーネントポリシーを作成する

このチュートリアルでは、少数の寛容なライセンスからなる許可リスト以外のライセンスを持つコンポーネントが含まれるプロジェクトを不合格にする、[コンポーネントポリシー](../concepts/component-policies.md)を作成します。単純なライセンス ID だけでなく SPDX ライセンス式全体に対して照合できるように、[`spdx_expr_allows`](../reference/policies/condition-expressions.md#spdx_expr_allows) 関数を使った `Expression` 条件を使います。ポリシーを作成したら、適切なライセンスのコンポーネントと不適切なライセンスのコンポーネントを 1 つずつ意図的に含めた小さな CycloneDX BOM をアップロードし、プロジェクトに違反が表示されることを確認します。

最後には、ポートフォリオ全体に適用されるポリシーと、監査できる `FAIL` のライセンス違反が表示されたプロジェクトができあがります。

## 必要なもの

- [クイックスタート](quickstart.md)で起動した Dependency-Track スタック。
- `POLICY_MANAGEMENT` 権限と `BOM_UPLOAD` 権限を持つアカウント。

## プロジェクトを作成する

ポリシーは BOM のアップロード時に評価されるため、まずアップロード先のプロジェクトを作成します。**Projects > Create Project** を開き、名前を `policy-demo` にして保存します。

## ポリシーを作成する

**Policy Management > Policies** を開き、*Create Policy* を選択して次の値を入力します。

| フィールド      | 値                          |
|-----------------|-----------------------------|
| Name            | `Permissive licenses only`  |
| Operator        | `Any`                       |
| Violation state | `FAIL`                      |

状態は重要です。`FAIL` にすると、違反によって後続の CI/CD チェックが失敗します。その他の状態については [Violation states](../reference/policies/component-policies.md#violation-states) を参照してください。

![ポリシー作成モーダル](../assets/images/tutorials/creating-a-component-policy/create-policy-modal.png)

保存すると、新しいポリシーが一覧に表示されます。ポリシーを開いて条件を追加します。

## 条件を記述する

*Add Condition* を選択し、サブジェクトとして `Expression` を選びます。エディターが入力補完付きの CEL エディターに切り替わります。違反の種類として `License` を選び、次のように入力します。

```js
!spdx_expr_allows(component.license_expression, [
  "MIT",
  "Apache-2.0",
  "BSD-3-Clause",
  "ISC"
])
```

この式の動作は次のとおりです。[`spdx_expr_allows`](../reference/policies/condition-expressions.md#spdx_expr_allows) は、左側の SPDX 式が右側のライセンス*だけ*を使って満たせる場合に `true` を返します。これを否定しているので、コンポーネントのライセンスが列挙した 4 つの寛容なライセンスのいずれでも*ない*場合に条件が一致し、違反が発生します。

!!! note
    `license_expression` フィールドを持たないコンポーネントは、現状ではこのチェックで無条件に不合格になります。本番環境で使う場合は、[リファレンスの例](../reference/policies/condition-expressions.md#license-expression-allowlist)にある `has(...) ? ... : component.resolved_license.id` によるフォールバックを参照してください。ここでは `spdx_expr_allows` に焦点を当てるため省略します。

行の *Update* を選択して条件を保存します。

![ポリシーの条件](../assets/images/tutorials/creating-a-component-policy/policy-condition.png)

*Projects* と *Tags* のオプションは空のままにして、ポリシーがポートフォリオ全体に適用されるようにします。

## サンプル BOM をアップロードする

条件の両方の分岐を確認できる BOM が必要です。次の CycloneDX ファイルには、寛容なライセンスのコンポーネント(`mit-lib`、`MIT`)が 1 つと、許可リストにない追加ライセンスのフォントアセットを同梱するコンポーネント(`font-lib`、`MIT AND OFL-1.1`)が 1 つ含まれています。

```json linenums="1" title="policy-demo.cdx.json"
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "version": 1,
  "components": [
    {
      "type": "library",
      "name": "mit-lib",
      "version": "1.0.0",
      "purl": "pkg:generic/acme/mit-lib@1.0.0",
      "licenses": [{ "expression": "MIT" }]
    },
    {
      "type": "library",
      "name": "font-lib",
      "version": "2.0.0",
      "purl": "pkg:generic/acme/font-lib@2.0.0",
      "licenses": [{ "expression": "MIT AND OFL-1.1" }]
    }
  ]
}
```

`policy-demo` プロジェクトを開き、*Components* タブに切り替えて、*Upload BOM* からファイルをアップロードします。

![BOM アップロードモーダル](../assets/images/tutorials/creating-a-component-policy/bom-upload.png)

## 違反を確認する

分析が完了したら、プロジェクトの *Policy Violations* タブを開きます。次の 1 行が表示されます。

- **Component**: `font-lib 2.0.0`
- **Violation type**: `License`
- **State**: `FAIL`
- **Policy**: `Permissive licenses only`

MIT ライセンスのコンポーネントは表示されません。そのライセンスは許可リストにあるため式が `true` を返し、否定によって条件が偽になったからです。`MIT` は許可リストにありますが、`font-lib` は違反として検出されます。`AND` は*両側*が許可リストで満たせることを要求しますが、`OFL-1.1` は許可リストにないためです。

![ポリシー違反の一覧](../assets/images/tutorials/creating-a-component-policy/violations.png)

## 違反を監査する

違反のドロワーを開いて分析状態を設定し、判断内容を記録する短いコメントを追加します。メトリクスやゲートの判定でこの検出結果を無視したい場合は、*Suppressed* もオンにします。トリアージのワークフロー全体については [Triaging policy violations](../guides/user/triaging-policy-violations.md) を参照してください。

![ポリシー違反の監査](../assets/images/tutorials/creating-a-component-policy/violation-audit.png)

## このチュートリアルで行ったこと

CEL 式の条件を 1 つ持つ、ポートフォリオ全体に適用されるコンポーネントポリシーを作成しました。その条件が寛容でないライセンスを含む BOM に一致し、`FAIL` の違反を発生させ、その違反を監査できることを確認しました。

次のステップ:

- [Managing component policies](../guides/user/managing-component-policies.md): プロジェクトの割り当て、タグによる適用範囲の指定、ライセンスグループなど、エディターのその他の機能を説明します。
- [About component policies](../concepts/component-policies.md): モデルの詳細と、コンポーネントポリシーと脆弱性ポリシーの関係を説明します。
- [Condition expressions](../reference/policies/condition-expressions.md): 式による条件で使える CEL 変数、カスタム関数、実例をすべて掲載しています。
