# v5 の破壊的変更

このページでは、Dependency-Track v4 と v5 の間での REST API v1 の破壊的変更を列挙します。REST API v2 は v5 で新たに追加されたものであり、対象外です。

現在の [v1 の OpenAPI 仕様](v1.md)が信頼できる情報源です。[削除されたエンドポイント](#removed-endpoints)の表と横断的な変更のセクションで、ほとんどのクライアントが影響を受ける変更を扱います。リソースごとのセクションには、それ以外のすべての変更を参照用に記載しています。

## クライアントが最も壊れやすい変更 {#whats-most-likely-to-break-your-client}

簡易的なトリアージです。各項目は、詳細を記載したセクションにリンクしています。

- **クライアントが呼び出すエンドポイントが存在しなくなっている可能性があります。** [削除されたエンドポイント](#removed-endpoints)の表を確認してください。
- **一覧エンドポイントは、デフォルトで 100 件までに制限されるようになりました。** ページネーションは、チーム、検出結果、脆弱性ごとのプロジェクトの一覧に適用されます。[Team](#team-resource)、[Finding](#finding-resource)、[Vulnerability](#vulnerability-resource) のセクションを参照してください。
- **バッジエンドポイントの認証の約束事が変わりました。** v5 は認証されていないリクエストを受け付けるため、`401` は不正な認証情報を示さなくなりました。[Badge リソース](#badge-resource)を参照してください。
- **プロジェクトの関連付けを行うエンドポイントで、新たに `403` レスポンスが返されます。** ステータスコードを厳密に照合していると失敗します。[Policy](#policy-resource) と [Notification rule](#notification-rule-resource) を参照してください。
- 次のリソースで、**リクエストボディの形式と必須フィールドが変わりました**: [Repository](#repository-resource)、[Notification publisher](#notification-publisher-resource)、[Notification rule](#notification-rule-resource)、[Tag](#tag-resource)。

## 削除されたエンドポイント {#removed-endpoints}

v5 では、`/v1/search/*` と `/v1/integration/osv/*` のリソース全体に加え、以下の個別のエンドポイントが削除されています。

| メソッド | パス                                                 | 代替                                                                           |
|:-------|:-----------------------------------------------------|:--------------------------------------------------------------------------------------|
| GET    | `/v1/search`                                         | なし。v5 では Lucene ベースの検索インデックスが削除されました。v5 にはあいまい一致の機能はありません。 |
| GET    | `/v1/search/component`                               | なし。                                                                                 |
| GET    | `/v1/search/license`                                 | なし。                                                                                 |
| GET    | `/v1/search/project`                                 | なし。                                                                                 |
| POST   | `/v1/search/reindex`                                 | なし。検索インデックスを再構築する必要はなくなりました。                                    |
| GET    | `/v1/search/service`                                 | なし。                                                                                 |
| GET    | `/v1/search/vulnerability`                           | なし。                                                                                 |
| GET    | `/v1/search/vulnerablesoftware`                      | なし。                                                                                 |
| GET    | `/v1/integration/osv/ecosystem`                      | なし。                                                                                 |
| GET    | `/v1/integration/osv/ecosystem/inactive`             | なし。                                                                                 |
| POST   | `/v1/notification/publisher/restoreDefaultTemplates` | なし。                                                                                 |
| POST   | `/v1/notification/publisher/test/smtp`               | `POST /v2/extension-points/notification.publisher/extensions/email/test`              |
| POST   | `/v1/policy/{policyUuid}/tag/{tagName}`              | `POST /v1/tag/{name}/policy`                                                          |
| DELETE | `/v1/policy/{policyUuid}/tag/{tagName}`              | `DELETE /v1/tag/{name}/policy`                                                        |
| GET    | `/v1/tag/{policyUuid}`                               | `GET /v1/tag/policy/{uuid}`                                                           |

## 横断的な変更 {#cross-cutting-changes}

これらの変更は多くのエンドポイントに影響します。リソースごとのセクションで繰り返さないよう、ここで一度だけ記載します。

- **`propertyType` の列挙型から `ENCRYPTEDSTRING` がなくなりました。** `ConfigProperty.propertyType`、`ProjectProperty.propertyType`、`ComponentProperty.propertyType` に適用されます。
- **`Project.classifier` と `Project.collectionLogic` から `NONE` がなくなりました。** ネストされたものを含め、`Project` を返すすべてのエンドポイントに適用されます。
- **`ProjectMetrics.collectionLogic` と `collectionLogicChanged` が削除されました。** `ProjectMetrics` を返すすべてのエンドポイントに適用されます。
- **`Permission` の列挙型から `VIEW_BADGES` がなくなりました。** `GET /v1/permission` と、権限の値を持つすべてのフィールドに影響します。
- **`AffectedVersionAttribution`**(`Vulnerability.affectedComponents[]` にネスト)から `uuid` フィールドがなくなりました。
- すべての脆弱性のレスポンスから **`VulnerabilityAlias.uuid` が削除されました**。

### 追加的な権限の変更 {#additive-permission-changes}

v5 では、v4 の粗い粒度の権限に加えて、操作ごとの権限(たとえば `POLICY_MANAGEMENT_READ`、`SYSTEM_CONFIGURATION_UPDATE`、`VULNERABILITY_ANALYSIS_READ`)が導入されています。v4 の権限を持つ既存のトークンは引き続き動作するため、これらの追加によってクライアントが壊れることはありません。全一覧は[権限](../permissions.md)を参照してください。

## リソースごとの変更 {#per-resource-changes}

リソースのセクションはアルファベット順に並んでいます。各セクション内では、変更のグループごとに、その先頭にエンドポイントのパスを太字で示しています。

### Badge リソース {#badge-resource}

**4 つのバッジエンドポイントすべて(`/v1/badge/vulns/...`、`/v1/badge/violations/...`)**

- **認証が不要に**: v5 のバッジエンドポイントは、認証されていないリクエストを受け付けます。認証情報の欠落や誤りを `401` で検出していたクライアントは、このステータスを受け取らなくなります。バッジのサポートは引き続きデフォルトで無効になっており、管理者が認証なしのアクセスを明示的に有効にする必要があります。
- **ステータスコードの変更**: `401` は返されなくなりました。`403` は、認証情報が誤っていることではなく、管理者がバッジを無効にしたことを意味します。`403` を受け取った場合に、別の認証情報で再試行しないでください。

!!! note
    v4.12.0 でバッジへのアクセスに認証が導入されました。バッジは通常 `README` などのドキュメントに埋め込まれるため、標準の `Authorization` ヘッダーはそこでは使えません。これを補うため、`/v1/badge` エンドポイントは URL のクエリーパラメーターで API キーを受け付けていました。`VIEW_BADGES` 権限だけを持つ API キーであれば安全だという想定でした。実際には、この設計によって API キーがログや Referer ヘッダーに露出したため、v5 では廃止されました。

### BOM リソース {#bom-resource}

**`GET /v1/bom/cyclonedx/project/{uuid}`**

- **権限の厳格化**: v4 では、すべてのバリアントで `VIEW_PORTFOLIO` だけが必要でした。v5 では、`variant=withVulnerabilities` または `variant=vdr` の場合に、`VIEW_VULNERABILITY`、`VULNERABILITY_ANALYSIS`、`VULNERABILITY_ANALYSIS_READ` のいずれかも必要です。

### Calculator リソース {#calculator-resource}

**`GET /v1/calculator/cvss`**

- **レスポンスフィールドの省略**: v4 は、6 つのスコアフィールド(`baseScore`、`impactSubScore`、`exploitabilitySubScore`、`temporalScore`、`environmentalScore`、`modifiedImpactSubScore`)を、該当しない場合(`NaN`)でもすべてプリミティブ値として返していました。v5 は、指定されたベクトルに該当しないフィールドを省略します。クライアントは `NaN` を前提とせず、キーが存在しない場合に対処する必要があります。

### Component リソース {#component-resource}

**`GET /v1/component/project/{uuid}`、`PUT /v1/component/project/{uuid}`、`POST /v1/component`、`GET /v1/component/{uuid}`**

- **列挙値の削除**: `Component.classifier.NONE`。`null` またはフィールドが存在しないことが、v4 の `NONE` と同じ意味を持ちます。
- **削除されたフィールド**: ネストされた `RepositoryMetaComponent.published` -> `latestVersionPublishedAt`。
- **必須フィールドの約束事の緩和**: `RepositoryMetaComponent` は、`lastCheck`、`latestVersion`、`name`、`repositoryType` を必須として宣言しなくなりました。クライアントは、これらが存在することを前提にできなくなります。

### Component property リソース {#component-property-resource}

**`/v1/component/{uuid}/property` 配下のすべてのエンドポイント**

- **列挙値の削除**: `ComponentProperty.propertyType.ENCRYPTEDSTRING`。

### Config property リソース {#config-property-resource}

**`/v1/configProperty` 配下のすべてのエンドポイント**

- **列挙値の削除**: `ConfigProperty.propertyType.ENCRYPTEDSTRING`。

### Finding リソース {#finding-resource}

**`Finding` を返すすべてのエンドポイント**

- **`vulnerability.cwes` の形式の変更**: v4 は CWE の整数 ID の配列(たとえば `[80, 666]`)を返していました。v5 は、`cweId` と `name` フィールドを持つ CWE オブジェクトの配列(たとえば `[{"cweId": 80, "name": "..."}, ...]`)を返します。これらのエンドポイントが出力する SARIF にも同じ変更があります。v4 は `cwes` を元のリストを引用符で囲んだ文字列としてシリアライズしていましたが、v5 は `{cweId, name}` オブジェクトの正しい JSON 配列を出力します。

**`POST /v1/finding/project/{uuid}/analyze`**

- **権限の厳格化**: 必要な権限が `VIEW_VULNERABILITY` -> `VULNERABILITY_ANALYSIS` に変わりました。

**`GET /v1/finding/project/{uuid}`**

- **ページネーションが適用されるように**: v4 は `pageNumber`/`pageSize` を公開していましたが、内部の SQL がそれらを無視していたため、レスポンスには常に一致するすべての行が含まれていました。v5 はこれらのパラメーターを適用します。1 回のレスポンスで結果全体を受け取ることを前提としていた呼び出し側は、デフォルトで `pageSize=100` に達した時点で、警告なく結果が切り捨てられるようになります。

**`GET /v1/finding` と `GET /v1/finding/grouped`**

- **ページネーションが適用されるように**: `GET /v1/finding/project/{uuid}` と同じ変更です。v4 は `pageNumber` と `pageSize` を受け付けていましたが無視していました。v5 はこれらを適用します。

### Metrics リソース {#metrics-resource}

**`GET /v1/metrics/project/{uuid}/current`、`/since/{date}`、`/days/{days}`**

- **削除されたレスポンスフィールド**: `ProjectMetrics.collectionLogic`、`collectionLogicChanged`。

### Notification publisher リソース {#notification-publisher-resource}

v5 では、`POST /v1/notification/publisher/restoreDefaultTemplates` と `POST /v1/notification/publisher/test/smtp` が削除されています。[削除されたエンドポイントの表](#removed-endpoints)を参照してください。

**`PUT /v1/notification/publisher`**

- **リクエストボディのスキーマの変更**: v4 は完全な `NotificationPublisher` を受け付けていました。v5 は `CreateNotificationPublisherRequest` を使います。
- **名前が変わり必須になったフィールド**: `publisherClass` -> `extensionName`(必須)。`extensionName` は、`GET /v2/extension-points/notification.publisher/extensions` で一覧表示される名前を参照する必要があります。
- **削除されたリクエストフィールド**: `defaultPublisher` と `uuid` は受け付けられなくなりました(v4 ではどちらも使われていませんでした)。作成時に `templateMimeType` は必須ではなくなりました。

**`POST /v1/notification/publisher`**

- **リクエストボディのスキーマの変更**: v4 は完全な `NotificationPublisher` を受け付けていました。v5 は `UpdateNotificationPublisherRequest` を使います。
- **名前が変わり必須になったフィールド**: `publisherClass` -> `extensionName`(必須)。`extensionName` は、`GET /v2/extension-points/notification.publisher/extensions` で一覧表示される名前を参照する必要があります。

**`NotificationPublisher` のレスポンススキーマ**

- **名前が変わったフィールド**: `publisherClass` -> `extensionName`。

### Notification rule リソース {#notification-rule-resource}

**`PUT /v1/notification/rule`**

- **リクエストボディのスキーマの変更**: v4 は完全な `NotificationRule` を受け付けていました。v5 は `CreateNotificationRuleRequest` を使います。
- **名前が変わったフィールド**: `notificationLevel` -> `level`。
- **新たに必須になったリクエストフィールド**: `publisher`(UUID のラッパー)が必須になりました。
- **削除されたリクエストフィールド**: `triggerType` と `uuid` は受け付けられなくなりました(サーバーが割り当てます)。

**`POST /v1/notification/rule`**

- **リクエストボディのスキーマの変更**: v4 は完全な `NotificationRule` を受け付けていました。v5 は `UpdateNotificationRuleRequest` を使います。
- **名前が変わったフィールド**: `notificationLevel` -> `level`。
- **新たに必須になったリクエストフィールド**: `level` と `scope` が必須になりました。
- **削除されたリクエストフィールド**: `triggerType`、`projects`、`teams`、`tags`、`publisher`、`publisherConfig`、およびスケジュールのフィールドは、更新のボディに含まれなくなりました(専用のサブエンドポイントで管理します)。

**`NotificationRule` のレスポンススキーマ**

- **列挙値の削除**: `notifyOn.INDEXING_SERVICE`。

**`POST /v1/notification/rule/{ruleUuid}/project/{projectUuid}`、`DELETE /v1/notification/rule/{ruleUuid}/project/{projectUuid}`**

- **新しいレスポンスステータス**: `403 Forbidden`(プロジェクトへのアクセスが拒否された場合)。

### Permission リソース {#permission-resource}

**`GET /v1/permission`**

- **列挙値の削除**: `Permission.VIEW_BADGES`。

### Policy リソース {#policy-resource}

**`POST /v1/policy/{policyUuid}/project/{projectUuid}`、`DELETE /v1/policy/{policyUuid}/project/{projectUuid}`**

- **新しいレスポンスステータス**: `403 Forbidden`(プロジェクトへのアクセスが拒否された場合)。v4 のコードだけを厳密に照合するクライアントには、ドキュメントに記載されていないエラーとして見えます。

v5 では、`/v1/policy/{policyUuid}/tag/{tagName}` の `POST` と `DELETE` のバリアントが削除されています。[削除されたエンドポイント](#removed-endpoints)の表を参照してください。

### Project リソース {#project-resource}

**`PUT /v1/project`、`POST /v1/project`、`GET /v1/project/{uuid}`、`PATCH /v1/project/{uuid}`**

- **削除されたレスポンスフィールド**: インラインの配列 `Project.properties`。代わりに `GET /v1/project/{uuid}/property` でプロジェクトのプロパティを取得します。
- **列挙値の削除**: `Project.classifier.NONE`、`Project.collectionLogic.NONE`。`null` またはフィールドが存在しないことが、v4 の `NONE` と同じ意味を持ちます。

**`GET /v1/project`**

- **削除されたレスポンスフィールド**: インラインの配列 `Project.children`。代わりに `GET /v1/project/{uuid}/children` でプロジェクトの子を取得します。

**`POST /v1/project/batchDelete`**

- **削除されたレスポンス**: v4 は `ProjectOperationProblemDetails` を伴う `400` をドキュメントに記載していました。v5 がドキュメントに記載しているのは `204` と `401` だけです。

### Project property リソース {#project-property-resource}

**`/v1/project/{uuid}/property` 配下のすべてのエンドポイント**

- **列挙値の削除**: `ProjectProperty.propertyType.ENCRYPTEDSTRING`。

### Repository リソース {#repository-resource}

**`GET /v1/repository/latest`**

- **名前が変わったレスポンスフィールド**: `RepositoryMetaComponent.published` -> `latestVersionPublishedAt`。
- **必須フィールドの約束事の緩和**: v4 で必須だった `lastCheck`、`latestVersion`、`name`、`published`、`repositoryType` は、レスポンススキーマではすべて任意になりました。

**`PUT /v1/repository`、`POST /v1/repository`**

- **新たに必須になったリクエストフィールド**: `Repository.authenticationRequired`。

### Tag リソース {#tag-resource}

v5 では、`GET /v1/tag/{policyUuid}` が削除され、`GET /v1/tag/policy/{uuid}` に置き換えられています。[削除されたエンドポイントの表](#removed-endpoints)を参照してください。

### Team リソース {#team-resource}

**`GET /v1/team`**

- **ページネーションの導入**: v4 にはページネーションのパラメーターがありませんでした。v5 では、`pageNumber`、`pageSize`、`offset`、`limit`、`sortName`、`sortOrder` が追加され、デフォルトは `pageSize=100` です。単純な呼び出し側では、最初の 100 件を超えるチームが警告なく欠落します。

### Vulnerability リソース {#vulnerability-resource}

**`Vulnerability` を返すすべてのエンドポイント**

- **削除されたレスポンスフィールド**: `findingAttribution` と `normalizedCvssV2Vector` は代替なしで削除されました。`cwe`(単数形)は削除されたため、代わりに `cwes` 配列を使います(単一の CWE は要素が 1 つの配列として表されます)。
- ネストされた `VulnerabilityAlias.uuid` が削除されました。ネストされた `AffectedVersionAttribution.uuid` が削除されました。

**`GET /v1/vulnerability/source/{source}/vuln/{vuln}/projects`**

- **ページネーションの導入**: v4 は件数に上限のない一覧を返していました。v5 はデフォルトで `pageSize=100` に制限し、`pageNumber`、`pageSize`、`sortName`、`sortOrder` を公開します。単純な呼び出し側では、最初の 100 件を超えるプロジェクトが警告なく欠落します。
- **レスポンスの型の変更**: v4 は `Project[]`(完全なスキーマ)を返していました。v5 は `AffectedProject[]` を返します。これは `active`、`affectedComponentUuids`、`dependencyGraphAvailable`、`name`、`uuid`、`version` だけを含む軽量な DTO です。v5 では、それ以外の `Project` のフィールドはすべて含まれません。
- **ステータスコードの削除**: v4 は不明な脆弱性に対して `404` を返していました。v5 は空の一覧とともに `200` を返します。
