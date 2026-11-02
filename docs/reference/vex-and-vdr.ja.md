# VEX と VDR ドキュメント

Dependency-Track は、プロジェクトの検出結果を CycloneDX の VEX または VDR としてエクスポートし、CycloneDX の VEX ドキュメントをインポートして既存の検出結果に分析の判断を適用します。これらのドキュメントの背景にあるモデルについては、[VEX について](../concepts/vex.md)を参照してください。Dependency-Track が生成する、分析を含まない CycloneDX ドキュメントについては、[ファイル形式](file-formats.md#cyclonedx)を参照してください。

## エクスポート {#export}

| | VEX | VDR |
|:---|:---|:---|
| エンドポイント | `GET /api/v1/vex/cyclonedx/project/{uuid}` | `GET /api/v1/bom/cyclonedx/project/{uuid}?variant=vdr` |
| `components` | 検出結果のあるものだけ | 検出結果のあるものだけ |
| コンポーネントの詳細 | 識別用のフィールドだけ | すべて |
| `services` | なし | あり |
| `dependencies` | なし | あり |
| `vulnerabilities` | あり | あり |
| `analysis` | あり | あり |
| シリアライズ形式 | JSON | JSON、または `format=XML` を指定した場合は XML |

どちらのエンドポイントも、出力の CycloneDX 仕様のバージョンを選択する `version` クエリーパラメーターと、ドキュメントを添付ファイルとして返す `download` クエリーパラメーターを受け付けます。

VEX のエンドポイントには、`VIEW_VULNERABILITY`、`VULNERABILITY_ANALYSIS`、`VULNERABILITY_ANALYSIS_READ` のいずれかの[権限](permissions.md)が必要です。VDR のバリアントには、これら 3 つのいずれかと `VIEW_PORTFOLIO` が必要です。

## エクスポートの内容 {#export-contents}

### 含まれる検出結果 {#findings-included}

どちらのエクスポートにも、抑制された検出結果が含まれます。どのアナライザーも報告しなくなった非アクティブな検出結果は除外されます。

### コンポーネントのエントリー {#component-entries}

VEX では、各コンポーネントを識別できる程度にだけ記述します。`components` 内のエントリーには `type`、`group`、`name`、`version`、`purl`、`cpe`、`swid`、`hashes` が含まれ、それ以外のフィールドは含まれません。VEX の仕様では、ハッシュも含めてこれらをそれぞれ識別方法の 1 つとして扱います。

VEX では、コンポーネントを識別するのではなく記述するためのフィールド(`description`、`copyright`、`scope`、`author`、`supplier`、`properties`、`licenses`、`externalReferences`、`evidence`)を省略します。VDR にはこれらが含まれます。

### 脆弱性のエントリー {#vulnerability-entries}

Dependency-Track は、`vulnerabilities` 内のエントリーを次のように生成します。

1. 検出結果を脆弱性と分析でグループ化します。分析は、状態、根拠、対応、詳細で比較します。
2. グループごとに `vulnerabilities` のエントリーを 1 つ出力します。
3. エントリーの `affects` ノードに、グループ内のコンポーネントの参照を並べ替えて重複排除したものを設定します。
4. エントリーに `analysis` ノードを追加します。

### 識別子 {#identifiers}

| 要素 | 値 |
|:---|:---|
| `metadata.component.bom-ref` | プロジェクトの UUID |
| `components[].bom-ref` | コンポーネントの UUID |
| `vulnerabilities[].affects[].ref` | 同じドキュメント内で解決できるコンポーネントの UUID |

`vulnerabilities` 内のエントリーには `bom-ref` は含まれず、エクスポートでは [BOM-Link](https://cyclonedx.org/capabilities/bomlink/) を使用しません。

これらの UUID は Dependency-Track の識別子です。同じプロジェクトのエクスポート間では変わりませんが、プロジェクトにアップロードされたどの BOM の `bom-ref` 値とも対応しません。

### 分析の対応付け {#analysis-mapping}

| Dependency-Track | CycloneDX |
|:---|:---|
| 分析状態 | `analysis.state` |
| 根拠 | `analysis.justification` |
| ベンダーの対応 | `analysis.responses`(要素が 1 つの配列) |
| 詳細 | `analysis.detail` |
| 抑制 | 出力しない |

## インポート {#import}

VEX のアップロードを受け付けるエンドポイントは 2 つあります。`POST /api/v1/vex` はマルチパートフォームを受け取ります。`PUT /api/v1/vex` は、Base64 でエンコードしたドキュメントを `vex` フィールドに含む JSON ボディーを受け取り、その長さは 20,000,000 文字までです。どちらも対象のプロジェクトを UUID、または名前とバージョンで特定し、どちらにも `VULNERABILITY_ANALYSIS` または `VULNERABILITY_ANALYSIS_UPDATE` の[権限](permissions.md)が必要です。

Dependency-Track は、ドキュメントを CycloneDX のスキーマに照らして検証します。スキーマに違反している場合は、RFC 9457 形式の問題の詳細を含む `400` レスポンスを返します。

インポートは、既存の検出結果に分析の判断を適用します。コンポーネント、脆弱性、検出結果は作成しません。

### スキップの条件 {#skip-conditions}

ドキュメントに `vulnerabilities` が含まれない場合、または対象のプロジェクトに脆弱性がない場合、Dependency-Track はアップロード全体をスキップします。

次のいずれかに該当する場合、Dependency-Track は `vulnerabilities` 内の個々のエントリーをスキップします。

| 条件 | 結果 |
|:---|:---|
| `id` が空である | エントリーをスキップし、警告をログに記録する |
| `affects` がないか、空である | エントリーをスキップする |
| エントリーに `analysis` ノードも `method: OWASP` のレーティングもない | エントリーをスキップする |
| エントリーの脆弱性を解決できない | エントリーをスキップし、警告をログに記録する |

### 脆弱性の解決 {#vulnerability-resolution}

エントリーのソースは、フィルターではなくヒントとして働きます。

1. `source.name` が Dependency-Track の把握している脆弱性のソースを指している場合は、そのソースと `id` を持つ脆弱性を探します。一致するものがあれば、解決はそこで終わります。
2. そうでない場合、または最初の手順で何も見つからなかった場合は、`id` だけで脆弱性を特定する必要があります。一致するものがちょうど 1 つであれば解決します。一致するものが複数ある場合は ID だけでは脆弱性を特定できないことを意味し、Dependency-Track は競合するソースを示す警告を出してエントリーをスキップします。一致するものがない場合はプロジェクトが影響を受けないことを意味し、Dependency-Track は警告を出してエントリーをスキップします。

把握している脆弱性のソースは `NVD`、`GITHUB`、`OSSINDEX`、`VULNDB`、`INTERNAL`、`OSV`、`SNYK`、`CX`、`JVN` です。

ソースが判断に使われるのは、ID が同じ脆弱性どうしを区別する場合だけです。Dependency-Track は `CVE-2020-1234` を NVD と OSV の両方から保持することがあり、その場合、影響を受けるコンポーネントにはソースごとに 1 つずつ検出結果が生成されます。いずれかのソースを指定したエントリーはその脆弱性だけに解決され、もう一方のソースに属する検出結果は元の分析を保持します。どちらのソースも指定していないエントリーは何にも解決されません。

### 参照の解決 {#reference-resolution}

インポーターは、メタデータのコンポーネントと、ネストしたコンポーネントを含む `components` 内のすべてのエントリーを `bom-ref` でインデックス化します。`affects[].ref` の各値は次のように解決されます。

| 参照の解決先 | スコープ | 適用先 |
|:---|:---|:---|
| `components` 内のエントリー | コンポーネント単位 | そのエントリーの識別情報に一致するプロジェクト内のすべてのコンポーネント |
| メタデータのコンポーネント | プロジェクト単位 | その脆弱性の影響を受けるプロジェクト内のすべてのコンポーネント |
| 該当なし、かつ参照が BOM-Link である | プロジェクト単位 | その脆弱性の影響を受けるプロジェクト内のすべてのコンポーネント |
| 上記以外で該当なし | 解決不能 | なし。Dependency-Track はその参照を示す警告をログに記録する |

### コンポーネントの識別情報の照合 {#component-identity-matching}

`affects[].ref` から解決されたコンポーネントのエントリーは、次のいずれかが成り立つ場合に、対象のプロジェクト内のコンポーネントに一致します。

* PURL が正規形で一致する。
* PURL の座標が一致する。つまり、修飾子とサブパスを除いて比較した PURL が一致する。
* CPE が一致する。
* SWID タグ ID が一致する。
* グループ、名前、バージョンがすべて一致する。

照合の対象は対象のプロジェクトだけで、複数のコンポーネントが一致することもあります。一致したすべてのコンポーネントに分析が適用されます。

### 適用されるフィールド {#applied-fields}

| ドキュメント内の値 | 検出結果での適用先 |
|:---|:---|
| `analysis.state` | 分析状態 |
| `analysis.justification` | 根拠 |
| `analysis.responses` | ベンダーの対応。最後のエントリーが優先される |
| `analysis.detail` | 分析の詳細 |
| `method: OWASP` のレーティング | OWASP リスク評価のベクターとスコア |

`resolved_with_pedigree` など、Dependency-Track がモデル化していない CycloneDX の状態は、分析状態 *Not Set* として取り込まれます。

分析状態 *False Positive*、*Not Affected*、*Resolved* をインポートすると、検出結果も抑制されます。それ以外の状態では抑制は変わりません。

適用された判断ごとに、検出結果の監査履歴に、コメント者を `CycloneDX VEX` とするエントリーが追加されます。
