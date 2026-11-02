# VEX ドキュメントを交換する

VEX をエクスポートすると、トリアージの判断を Dependency-Track インスタンスの外部の相手と共有できます。VEX をインポートすると、プロジェクトの検出結果に判断を一括で適用できます。どちらの操作も、プロジェクトの **Audit Vulnerabilities** タブから行います。

エクスポートには、`VIEW_VULNERABILITY`、`VULNERABILITY_ANALYSIS`、`VULNERABILITY_ANALYSIS_READ` のいずれかの[権限](../../reference/permissions.md)が必要です。インポートには、`VULNERABILITY_ANALYSIS` または `VULNERABILITY_ANALYSIS_UPDATE` が必要です。

VEX が何を表明するか、VDR とどう違うかについては、[VEX について](../../concepts/vex.md) を参照してください。

## 第三者向けに判断をエクスポートする {#export-decisions-for-a-third-party}

1. プロジェクトを開き、**Audit Vulnerabilities** タブに切り替えます。
2. 分析だけを含むドキュメントが必要な場合は **Export VEX** を、サービスと依存関係グラフも含むドキュメントが必要な場合は **Export VDR** を選択します。

ファイルは CycloneDX JSON としてダウンロードされます。エクスポートを自動化するには、[VEX and VDR documents](../../reference/vex-and-vdr.md#export) に記載されているエンドポイントを呼び出します。このページには、各ドキュメントに含まれる内容も記載されています。

送付する前に、受け取る側が何を求めているかを確認します。

* 相手がすでに保持している SBOM に対して解決されるドキュメントが必要な場合、Dependency-Track のエクスポートではそれを作成できません。単独のドキュメントとして送付するか、別のツールで相互リンクされたドキュメントを作成します。
* 判断に加えて製品の構成も必要な場合は、VDR を送付します。VEX にはサービスと依存関係グラフが含まれず、各コンポーネントについても識別に必要な程度の情報しか記述されません。
* 抑制された検出結果は、抑制の根拠となった分析とともに、どちらのドキュメントにも含まれます。ファイルを組織外に送付する前に、それらの分析を確認してください。

## VEX の判断を適用する {#apply-decisions-from-a-vex}

サプライヤーの評価を受け入れる場合、プロジェクトの新しいバージョンに判断を再適用する場合、チームが別の場所で記録した判断を適用する場合に使用します。

1. 対象のプロジェクトを開き、**Audit Vulnerabilities** タブに切り替えます。
2. **Apply VEX** を選択します。
3. CycloneDX VEX ファイルを選び、**Upload** を選択します。

Dependency-Track は、各判断をすでに存在する検出結果に適用します。コンポーネントはドキュメント内の識別子ではなく同一性で照合されるため、別のプロジェクトからエクスポートしたドキュメントもこのプロジェクトに適用できます。インポートで変更できる内容とできない内容については [VEX について](../../concepts/vex.md#what-an-import-changes) で、インポート時に従うルールについては [VEX and VDR documents](../../reference/vex-and-vdr.md#import) で説明しています。

結果は **Audit Vulnerabilities** タブで確認します。分析状態 *False Positive*、*Not Affected*、*Resolved* をインポートすると、対象の検出結果は抑制されるため、それらを表示するには **Show Suppressed** を切り替えます。判断が反映されなかった場合の理由は、[変更が反映されない場合](#if-nothing-changed)に記載しています。

## 反映される VEX を作成する {#author-a-vex-that-takes-effect}

手作業で作成する VEX は、名前を挙げる脆弱性と、指し示すコンポーネントの 2 か所でプロジェクトと一致している必要があります。以下の例は、次の BOM から作成したプロジェクトに適用するものです。

```json linenums="1"
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "version": 1,
  "metadata": {
    "component": {
      "bom-ref": "acme-app@1.0.0",
      "type": "application",
      "name": "acme-app",
      "version": "1.0.0"
    }
  },
  "components": [
    {
      "bom-ref": "jackson-databind@2.13.4",
      "type": "library",
      "group": "com.fasterxml.jackson.core",
      "name": "jackson-databind",
      "version": "2.13.4",
      "purl": "pkg:maven/com.fasterxml.jackson.core/jackson-databind@2.13.4"
    }
  ]
}
```

脆弱性分析によって、このコンポーネントに `CVE-2022-42003` の検出結果が生成されており、チームは脆弱なコードに到達できないと結論付けたとします。

### 1 つのコンポーネントを対象にする {#target-one-component}

```json linenums="1"
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "version": 1,
  "metadata": {
    "component": {
      "bom-ref": "product",
      "type": "application",
      "name": "acme-app",
      "version": "1.0.0"
    }
  },
  "components": [
    {
      "bom-ref": "affected-library",
      "type": "library",
      "group": "com.fasterxml.jackson.core",
      "name": "jackson-databind",
      "version": "2.13.4",
      "purl": "pkg:maven/com.fasterxml.jackson.core/jackson-databind@2.13.4"
    }
  ],
  "vulnerabilities": [
    {
      "id": "CVE-2022-42003",
      "source": { "name": "NVD" },
      "analysis": {
        "state": "not_affected",
        "justification": "code_not_reachable",
        "response": ["will_not_fix"],
        "detail": "The vulnerable deserialization path is unreachable from our entry points."
      },
      "affects": [{ "ref": "affected-library" }]
    }
  ]
}
```

このドキュメントをプロジェクトにアップロードすると、`jackson-databind` の検出結果が *Not Affected* に設定され、根拠、対応、詳細が記録され、検出結果が抑制されます。反映されたのは、次の 4 つの条件を満たしていたためです。

1. **アップロード先がプロジェクトを決めた。** ドキュメント内の `metadata.component` はプロジェクトを選択せず、プロジェクトを記述している必要もありません。意味を持つのは、ステートメントがそれを指し示す場合だけです。
2. **`affects[].ref` が同じドキュメント内のエントリーを指定している。** 値 `affected-library` はそのエントリーの `bom-ref` と一致しています。これらの名前はドキュメント内でのみ有効です。アップロードした BOM と一致している必要はなく、Dependency-Track はその BOM の名前を記録していません。
3. **指定されたエントリーが、同一性によってプロジェクト内のコンポーネントと一致する。** PURL が一致するため、エントリーはプロジェクトの `jackson-databind` に解決されます。CPE、SWID タグ ID、またはグループ、名前、バージョンの組み合わせでも同様に照合でき、いずれか 1 つが一致すれば十分です。バージョンは同一性の一部です。ドキュメント内の `2.13.5` は、`2.13.4` を含むプロジェクトでは何とも一致しません。
4. **`id` が、プロジェクトにすでに検出結果がある脆弱性を指定している。** `source` はヒントであり、フィルターではありません。Dependency-Track が認識しているソースを指定した場合、解決はそのソースから始まります。そうでない場合は、ID だけで脆弱性を特定できる必要があります。Dependency-Track がその ID を複数のソースから保持している場合は、ソースを指定してください。生成される検出結果のうち、どれに判断が適用されるかはその名前で決まります。インポートで検出結果が作成されることはないため、プロジェクトにない脆弱性に関するステートメントは Dependency-Track によって破棄されます。

### 1 つの判断を影響を受けるすべてのコンポーネントに適用する {#broadcast-one-decision-to-every-affected-component}

ドキュメントの残りの部分は変更せず、`affects[].ref` をコンポーネントのエントリーではなく、`metadata.component` の `bom-ref` に向けます。

```json linenums="1"
  "vulnerabilities": [
    {
      "id": "CVE-2022-42003",
      "source": { "name": "NVD" },
      "analysis": {
        "state": "false_positive",
        "detail": "Reported against a component we repackage under a different name."
      },
      "affects": [{ "ref": "product" }]
    }
  ]
```

プロジェクト内で `CVE-2022-42003` の影響を受けるすべてのコンポーネントに、ドキュメントに記載されていないコンポーネントも含めて、この判断が適用されます。ステートメントが製品全体に関するものである場合に使用します。

### 変更が反映されない場合 {#if-nothing-changed}

Dependency-Track は、エントリーをスキップした理由をログに記録します。解決できない脆弱性と解決できない参照は、API サーバーのログに警告として出力されます。分析のないエントリーはデバッグレベルで出力されます。まずログを確認し、次に以下の一覧を確認します。

* プロジェクトにその ID の検出結果がない。**Audit Vulnerabilities** タブで確認してください。
* その ID が Dependency-Track 内に複数のソースで存在し、エントリーが認識できるソースを指定していない。ソースを指定してください。
* エントリーに `analysis` オブジェクトがなく、`method: OWASP` の評価もない。インポーターはこのようなエントリーを破棄します。
* `affects` がない、空である、またはドキュメント内のどのエントリーも宣言していない `bom-ref` を指定している。
* コンポーネントのエントリーとプロジェクトのコンポーネントに、共通する識別情報がない。バージョンが異なる PURL や、グループ、名前、バージョンの一部だけでは何とも一致しません。

照合ルールとスキップ条件の全体については、[VEX and VDR documents](../../reference/vex-and-vdr.md#import) を参照してください。
