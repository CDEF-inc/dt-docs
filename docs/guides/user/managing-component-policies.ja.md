# コンポーネントポリシーを管理する

コンポーネントポリシーは *Policy Management* > *Policies* で管理します。必要な権限は `POLICY_MANAGEMENT`、またはより細かい粒度の `POLICY_MANAGEMENT_CREATE`、`POLICY_MANAGEMENT_READ`、`POLICY_MANAGEMENT_UPDATE`、`POLICY_MANAGEMENT_DELETE` のいずれかです。ポリシーが発生させた違反のトリアージは別のタスクです。[ポリシー違反をトリアージする](triaging-policy-violations.md)を参照してください。

コンポーネントポリシーとは何か、どのように動作するかについては、[コンセプトのページ](../../concepts/component-policies.md)を参照してください。フィールドの定義と、サブジェクト・演算子・値の組み合わせの一覧については、[リファレンスのページ](../../reference/policies/component-policies.md)を参照してください。

![ポリシーの一覧](../../assets/images/guides/user/managing-component-policies/policy-list.png)

## ポリシーを作成する {#creating-a-policy}

1. *Policy Management > Policies* を開き、*Create Policy* をクリックします。
2. ポリシーに名前を付けます。
3. [演算子](../../reference/policies/component-policies.md#operator)(`Any` または `All`)を選びます。
4. [違反の状態](../../reference/policies/component-policies.md#violation-states)(`INFO`、`WARN`、`FAIL` のいずれか)を選びます。
5. *Create* をクリックします。新しいポリシーには、最初は条件がありません。

!!! note
    ポリシーを保存しても、その時点でポートフォリオの分析が再実行されるわけではありません。ロールアウトはプロジェクトの分析スケジュールに合わせて計画してください。[コンポーネントポリシーについて › ライフサイクル](../../concepts/component-policies.md#lifecycle)を参照してください。

![新しいコンポーネントポリシー](../../assets/images/guides/user/managing-component-policies/new-policy.png)

## 条件を追加する {#adding-conditions}

一覧からポリシーを開いて詳細ビューを展開し、条件を 1 つずつ追加します。

- *Subject* を選びます。選択できる演算子と値のエディターは、サブジェクトに応じて切り替わります。組み合わせの一覧は[サブジェクトのリファレンス](../../reference/policies/component-policies.md#condition-subjects)にあります。
- *Operator* を選び、*Value* を入力します。`COORDINATES` のエディターにはグループ、名前、バージョンの入力欄があり、`VERSION_DISTANCE` にはエポック、メジャー、マイナー、パッチのフィールドがあります。`COMPONENT_HASH` では、演算子のフィールドがハッシュアルゴリズムになります。
- `EXPRESSION` 条件では、入力補完付きのインライン CEL エディターが表示され、違反の種類を明示的に選ぶ必要があります。[条件式](../../reference/policies/condition-expressions.md)を参照してください。
- 行の *Update* をクリックして保存します。

![ポリシーの編集](../../assets/images/guides/user/managing-component-policies/edit-policy.png)

## プロジェクトに割り当てる {#assigning-to-projects}

新しいポリシーはポートフォリオ全体に適用されます。適用範囲を絞り込むには、次のようにします。

- *Projects* タブでプロジェクトを追加します。*Include children* をオンにすると、その子孫のプロジェクトも対象になります。
- *Tags* タブでタグを追加します。ポリシーは、それらのタグを 1 つ以上持つすべてのプロジェクトに適用されます。

適用範囲の厳密なルールについては、[コンポーネントポリシー › 割り当て](../../reference/policies/component-policies.md#assignment)を参照してください。

![プロジェクトに限定したポリシー](../../assets/images/guides/user/managing-component-policies/limit-policy-to-project.png)

## ライセンスグループを管理する {#managing-license-groups}

ライセンスグループは *Policy Management* > *License Groups* で管理します。Dependency-Track には組み込みのグループ(*Copyleft* や *Permissive* など)が付属しています。同じビューで、それらを拡張したり新しいグループを追加したりできます。ライセンスグループは `LICENSE_GROUP` 条件の値として使います。

![ライセンスグループ](../../assets/images/guides/user/managing-component-policies/license-groups.png)
