# ポリシー違反をトリアージする

レビュー担当者は、プロジェクトの *Policy Violations* タブからポリシー違反をトリアージします。違反を表示するには `VIEW_POLICY_VIOLATION` 権限が、分析状態の設定、コメントの追加、抑制を行うには `POLICY_VIOLATION_ANALYSIS` 権限が必要です。どちらの権限でも、ポリシーの作成や編集はできません。ポリシーの作成と編集については[コンポーネントポリシーを管理する](managing-component-policies.md)で説明しています。

違反とは何か、違反の分析状態が何を意味するかについては、[About component policies](../../concepts/component-policies.md#what-a-violation-means) を参照してください。

## プロジェクトの違反を確認する {#reviewing-violations-on-a-project}

プロジェクトを開き、*Policy Violations* タブに切り替えます。各行には、コンポーネント、違反した条件、違反の種類(License、Operational、Security のいずれか)、ポリシーから継承した違反の[状態](../../reference/policies/component-policies.md#violation-states)(`INFO`、`WARN`、`FAIL` のいずれか)が表示されます。状態はポリシーから決まるもので、違反ごとに編集することはできません。

![プロジェクトビューの Policy Violations タブ](../../assets/images/guides/user/triaging-policy-violations/project-violations.png)

## 分析を記録する {#recording-an-analysis}

違反を開くと、監査ドロワーが表示されます。

- *分析状態*を `APPROVED`、`REJECTED`、`NOT_SET` のいずれかに設定します。Dependency-Track はこれらの値に固定の意味を割り当てていません。チームが一般的に採用する取り決めについては、[Analysis states](../../concepts/component-policies.md#what-a-violation-means) を参照してください。
- 判断の理由を記録するコメントを追加します。各コメントにはタイムスタンプと作成者が記録され、状態の変更とあわせて監査証跡になります。
- 必要に応じて *Suppressed* をオンにします。抑制すると、違反がプロジェクトのメトリクス、バッジ、CI/CD ゲートから除外されます。抑制は運用上の手段であり、分析状態にはその背後にある理由を記録します。

![プロジェクトのポリシー違反の監査](../../assets/images/guides/user/triaging-policy-violations/project-violations-audit.png)

監査証跡は再評価をまたいで保持されます。今後の分析で同じコンポーネントに対して違反が再び発生した場合(たとえば、問題のコンポーネントが新しい BOM で再び現れた場合)、抑制は引き継がれ、監査証跡のコメントによって経緯を確認できます。
