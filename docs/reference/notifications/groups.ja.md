# 通知グループ

*グループ*は、通知のサブジェクトを細かく分類したものです。すべてのグループは、`SYSTEM`(プラットフォームレベルのイベント)と `PORTFOLIO`(プロジェクト、コンポーネント、検出結果に関するイベント)の 2 つのスコープのいずれかに属します。また、すべてのグループは 1 つのトリガーの種類を持ちます。`Event` はシステムのイベントに応じてシステムが送出する随時の通知、`Schedule` は cron スケジュールで定期的に発火する通知です。

各グループのサブジェクトのスキーマについては、[通知スキーマのリファレンス](schema.md)で説明しています。

## システムスコープ {#system-scope}

### `ANALYZER` {#analyzer}

- **トリガー:** Event
- **レベル:** Any

外部の脆弱性インテリジェンスのソースとのやり取りの結果として生成されます。

### `CONFIGURATION` {#configuration}

- **トリガー:** Event
- **レベル:** Any

プラットフォームの設定変更や設定エラーの結果として生成されます。

### `DATASOURCE_MIRRORING` {#datasource_mirroring}

- **トリガー:** Event
- **レベル:** Any

NVD など、サポートされているデータソースのミラーリングを実行したときに生成されます。

### `FILE_SYSTEM` {#file_system}

- **トリガー:** Event
- **レベル:** Any

ファイルシステムの操作の結果として生成されます。通常はエラーが発生した場合にのみ生成されます。

### `INTEGRATION` {#integration}

- **トリガー:** Event
- **レベル:** Any

外部の連携とのやり取りの結果として生成されます。

### `REPOSITORY` {#repository}

- **トリガー:** Event
- **レベル:** Any

Maven Central、RubyGems、npm など、サポートされているパッケージリポジトリとのやり取りの結果として生成されます。

### `USER_CREATED` {#user_created}

- **トリガー:** Event
- **レベル:** Informational

ユーザーの作成の結果として生成されます。

### `USER_DELETED` {#user_deleted}

- **トリガー:** Event
- **レベル:** Informational

ユーザーの削除の結果として生成されます。

## ポートフォリオスコープ {#portfolio-scope}

### `BOM_CONSUMED` {#bom_consumed}

- **トリガー:** Event
- **レベル:** Informational

プラットフォームがサポートされている BOM を取り込み、識別したときに発火します。

### `BOM_PROCESSED` {#bom_processed}

- **トリガー:** Event
- **レベル:** Informational

プラットフォームがサポートされている BOM を取り込み、識別し、正常に処理した後に発火します。

### `BOM_PROCESSING_FAILED` {#bom_processing_failed}

- **トリガー:** Event
- **レベル:** Error

BOM のアップロード処理が失敗したときに発火します。

### `BOM_VALIDATION_FAILED` {#bom_validation_failed}

- **トリガー:** Event
- **レベル:** Error

無効な BOM がアップロードされたときに発火します。

### `NEW_VULNERABILITY` {#new_vulnerability}

- **トリガー:** Event
- **レベル:** Informational

プラットフォームが新しい脆弱性を検出したときに発火します。

### `NEW_VULNERABLE_DEPENDENCY` {#new_vulnerable_dependency}

- **トリガー:** Event
- **レベル:** Informational

脆弱なコンポーネントがプロジェクトの依存関係になったときに発火します。

### `POLICY_VIOLATION` {#policy_violation}

- **トリガー:** Event
- **レベル:** Informational

プラットフォームがポリシー違反を記録したときに発火します。

### `PROJECT_AUDIT_CHANGE` {#project_audit_change}

- **トリガー:** Event
- **レベル:** Informational

プロジェクトの検出結果の分析状態または抑制の状態が変わったときに発火します。

### `PROJECT_CREATED` {#project_created}

- **トリガー:** Event
- **レベル:** Informational

新しいプロジェクトが作成されたときに発火します。

### `VEX_CONSUMED` {#vex_consumed}

- **トリガー:** Event
- **レベル:** Informational

プラットフォームが VEX ドキュメントを取り込んだときに発火します。

### `VEX_PROCESSED` {#vex_processed}

- **トリガー:** Event
- **レベル:** Informational

プラットフォームが VEX ドキュメントを取り込み、正常に処理した後に発火します。

### `VULNERABILITY_RETRACTED` {#vulnerability_retracted}

- **トリガー:** Event
- **レベル:** Informational

以前の脆弱性の報告が取り消されたときに発火します。

### `NEW_VULNERABILITIES_SUMMARY` {#new_vulnerabilities_summary}

- **トリガー:** Schedule
- **レベル:** Informational

一連のプロジェクトで見つかった新しい脆弱性をまとめます。

### `NEW_POLICY_VIOLATIONS_SUMMARY` {#new_policy_violations_summary}

- **トリガー:** Schedule
- **レベル:** Informational

一連のプロジェクトで見つかった新しいポリシー違反をまとめます。

## サブジェクト {#subjects}

通知の型付きサブジェクトは、そのグループによって異なります。各サブジェクトのスキーマについては、[通知スキーマのリファレンス](schema.md)で説明しています。

| グループ                                                | サブジェクトの型                                                                                                                                        |
|:--------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------------------------------------------------|
| `BOM_CONSUMED`, `BOM_PROCESSED`                         | [BomConsumedOrProcessedSubject](schema.md#bomconsumedorprocessedsubject)                                                               |
| `BOM_PROCESSING_FAILED`                                 | [BomProcessingFailedSubject](schema.md#bomprocessingfailedsubject)                                                                     |
| `BOM_VALIDATION_FAILED`                                 | [BomValidationFailedSubject](schema.md#bomvalidationfailedsubject)                                                                     |
| `NEW_VULNERABILITY`                                     | [NewVulnerabilitySubject](schema.md#newvulnerabilitysubject)                                                                           |
| `NEW_VULNERABLE_DEPENDENCY`                             | [NewVulnerableDependencySubject](schema.md#newvulnerabledependencysubject)                                                             |
| `POLICY_VIOLATION`                                      | [PolicyViolationSubject](schema.md#policyviolationsubject)                                                                             |
| `PROJECT_AUDIT_CHANGE`                                  | [VulnerabilityAnalysisDecisionChangeSubject](schema.md#vulnerabilityanalysisdecisionchangesubject) または [PolicyViolationAnalysisDecisionChangeSubject](schema.md#policyviolationanalysisdecisionchangesubject) |
| `VEX_CONSUMED`, `VEX_PROCESSED`                         | [VexConsumedOrProcessedSubject](schema.md#vexconsumedorprocessedsubject)                                                               |
| `USER_CREATED`, `USER_DELETED`                          | [UserSubject](schema.md#usersubject)                                                                                                   |
| `NEW_VULNERABILITIES_SUMMARY`                           | [NewVulnerabilitiesSummarySubject](schema.md#newvulnerabilitiessummarysubject)                                                         |
| `NEW_POLICY_VIOLATIONS_SUMMARY`                         | [NewPolicyViolationsSummarySubject](schema.md#newpolicyviolationssummarysubject)                                                       |
