# ファイル形式

## CycloneDX {#cyclonedx}

Dependency-Track の主要なファイル形式は [CycloneDX](https://cyclonedx.org/) です。これは、セキュリティに重点を置いた軽量な部品表(BOM)の仕様です。Dependency-Track への SBOM の**アップロード**でサポートされている形式は CycloneDX だけです。

サポートされている CycloneDX のシリアライズ形式:

| 形式 | Content-Type |
|:-------|:-------------|
| JSON | `application/vnd.cyclonedx+json` |
| XML | `application/vnd.cyclonedx+xml` |

アップロードでは、CycloneDX BOM 仕様のすべてのバージョンがサポートされています。

Dependency-Track は、いくつかの形態の CycloneDX ドキュメントの**生成**も行います。

| ドキュメントの種類 | リクエスト方法 | 説明 |
|:-------------|:---------------|:------------|
| BOM | `GET /api/v1/bom/cyclonedx/project/{uuid}`、デフォルトのバリアント | プロジェクトの現在のコンポーネントインベントリーを、サービスと依存関係グラフとともに反映した、完全なソフトウェア部品表です。 |
| 脆弱性付き BOM | 同じエンドポイントで `variant=withVulnerabilities` を指定 | インベントリーに加えて、そのコンポーネントに影響する脆弱性を含みます。脆弱性ごとに 1 つのエントリーがあり、影響を受けるすべてのコンポーネントを列挙します。分析の判断は含みません。 |
| VDR | 同じエンドポイントで `variant=vdr` を指定 | プロジェクトのコンポーネントに関する完全な脆弱性データと、それらについて記録された分析の判断を含む Vulnerability Disclosure Report です。 |
| VEX | `GET /api/v1/vex/cyclonedx/project/{uuid}` | プロジェクトの検出結果に対する分析の判断(状態、根拠)を含む Vulnerability Exploitability Exchange ドキュメントです。 |

BOM エンドポイントには `VIEW_PORTFOLIO` [権限](permissions.md)が必要で、その `withVulnerabilities` と `vdr` のバリアントには、さらに `VIEW_VULNERABILITY`、`VULNERABILITY_ANALYSIS`、`VULNERABILITY_ANALYSIS_READ` のいずれかが必要です。VEX または VDR の内容と、VEX のアップロードが従うルールについては、[VEX と VDR ドキュメント](vex-and-vdr.md)を参照してください。

## Finding Packaging Format(FPF) {#finding-packaging-format-fpf}

Finding Packaging Format(FPF)は、検出結果をエクスポートするための Dependency-Track 独自の JSON 形式です。主に、REST API を直接利用できないプラットフォームとの連携に使われます。

### 構造 {#structure}

FPF ドキュメントには 4 つのトップレベルのフィールドがあります。

| フィールド | 説明 |
|:------|:------------|
| `version` | FPF 形式のバージョン。 |
| `meta` | ファイルを生成した Dependency-Track インスタンスに関する情報。 |
| `project` | プロジェクトのメタデータ(名前、バージョン、UUID)。 |
| `findings` | 検出結果のレコードの配列。各レコードはコンポーネントと脆弱性を結び付け、現在の分析状態を含みます。 |

各検出結果のレコードには、影響を受けるコンポーネントの座標、脆弱性の詳細(ID、ソース、深刻度、CVSS ベクトル、CWE)、現在の分析状態と根拠、そして(プロジェクト、コンポーネント、脆弱性)の 3 つ組を一意に識別するマトリックス識別子が含まれます。

### API エンドポイント {#api-endpoint}

```text
GET /api/v1/finding/project/{uuid}/export
```

`VIEW_VULNERABILITY` 権限が必要です。

### バージョン履歴 {#version-history}

| FPF のバージョン | Dependency-Track のバージョン | 変更点 |
|:------------|:------------------------|:--------|
| v1.0 | 初版 | 基本となる形式。 |
| v1.1 | v4.5 | 脆弱性ごとに複数の CWE をサポートするため、`cwes` 配列を追加。 |
| v1.2 | v4.8.0 | エイリアスから `allBySource` と内部の `id` フィールドを削除。 |
| v1.3 | v4.14.0 | 任意の CVSS ベクトル(`cvssV2Vector`、`cvssV3Vector`、`cvssV4Vector`)と OWASP Risk Rating のベクトルのフィールドを追加。 |
