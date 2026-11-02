# 状況に応じて検出結果を評価する

このチュートリアルでは、1 つの脆弱性に対して 2 つのプロジェクトでそれぞれ異なる OWASP リスク評価を与え、各評価がそれぞれの検出結果に反映されることを確認します。

深刻度は脆弱性そのものに由来し、影響を受けるコンポーネントをどこで実行しているかについては何も示しません。VEX には分析の判断の代わりに [OWASP リスク評価](https://owasp.org/www-community/OWASP_Risk_Rating_Methodology)を含められるため、同じコンポーネントでも、あるデプロイでは危険で、別のデプロイでは無害であると表現できます。ここでは、インターネットに公開されたサービス用と、夜間バッチジョブ用の 2 つのドキュメントを作成します。

## 必要なもの {#what-we-need}

- [クイックスタート](quickstart.md)で起動した、バージョン 5.1.0 以降の Dependency-Track スタック。
- `PORTFOLIO_MANAGEMENT`、`BOM_UPLOAD`、`VULNERABILITY_MANAGEMENT`、`VULNERABILITY_ANALYSIS`、`VIEW_PORTFOLIO`、`VIEW_VULNERABILITY` の[権限](../reference/permissions.md)。`admin` アカウントはこの 6 つすべてを持っています。

その他のものはすべて途中で作成するため、脆弱性ミラーの同期を待つ必要はありません。

## 2 つのプロジェクトを作成する {#creating-the-two-projects}

**Projects** を開き、**Create Project** を選択して、バージョン `1.0.0` の `checkout-api` を作成します。同様に、同じくバージョン `1.0.0` の `nightly-report` を作成します。

どちらのプロジェクトにも同じコンポーネントを含め、記録するリスクだけを変えます。

## 両方のプロジェクトに同じ BOM をアップロードする {#uploading-the-same-bom-to-both-projects}

```json title="billing.cdx.json" linenums="1"
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "version": 1,
  "components": [
    {
      "bom-ref": "billing-lib@1.4.2",
      "type": "library",
      "group": "com.example",
      "name": "billing-lib",
      "version": "1.4.2",
      "purl": "pkg:maven/com.example/billing-lib@1.4.2"
    }
  ]
}
```

`checkout-api` を開き、**Components** タブに切り替え、**Upload BOM** を選択してファイルを選びます。`nightly-report` でも同じ操作を行います。これで、各プロジェクトにコンポーネントが 1 つあり、検出結果はない状態になります。

## コンポーネントに影響する脆弱性を作成する {#creating-a-vulnerability-that-affects-the-component}

評価の対象となる検出結果が必要です。このチュートリアルがどのインスタンスでも同じ結果になるように、脆弱性は自分で作成します。

**Vulnerabilities** を開き、**Create Vulnerability** を選択します。

| フィールド       | 値                                          |
|------------------|---------------------------------------------|
| Vulnerability ID | `INT-BILLING-0001`                          |
| Title            | `Incorrect pattern matching in billing-lib` |
| Severity         | `Medium`                                    |

**Affected Components** タブで **+** アイコンを選択し、次のように入力します。

| フィールド      | 値                                          |
|-----------------|---------------------------------------------|
| Identifier Type | `Package URL (PURL)`                        |
| Identifier      | `pkg:maven/com.example/billing-lib@1.4.2`   |
| Version Type    | `Exact`                                     |

バージョンは PURL に含まれます。Dependency-Track は解析できない PURL をエラーを報告せずに破棄するため、識別子は BOM の宣言と一致している必要があります。

保存したら、各プロジェクトに戻り、**Audit Vulnerabilities** タブで **Reanalyze** を選択します。数秒以内に、両方のプロジェクトに `INT-BILLING-0001` の検出結果が 1 件ずつ、深刻度 *Medium* で表示されます。検出結果がまだ表示されない場合は、タブを再読み込みします。

両方のプロジェクトの深刻度は同じです。これから作成する 2 つのドキュメントで、この深刻度に状況に応じた評価を加えます。

## 2 つの VEX ドキュメントを作成する {#writing-the-two-vex-documents}

各ドキュメントは脆弱性を指定し、製品全体を対象とします。そのため、`affects[].ref` には `metadata.component` の `bom-ref` を指定します。インポートで変更できる内容とできない内容については、[About VEX](../concepts/vex.md#what-an-import-changes) を参照してください。

```json title="vex-checkout-api.json" linenums="1"
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "version": 1,
  "metadata": {
    "component": {
      "bom-ref": "product",
      "type": "application",
      "name": "checkout-api",
      "version": "1.0.0"
    }
  },
  "vulnerabilities": [
    {
      "id": "INT-BILLING-0001",
      "source": { "name": "INTERNAL" },
      "ratings": [
        {
          "method": "OWASP",
          "vector": "OWASP/SL:9/M:9/O:9/S:9/ED:9/EE:9/A:9/ID:9/LC:7/LI:7/LAV:7/LAC:7/FD:7/RD:7/NC:7/PV:7",
          "score": 63.0
        }
      ],
      "affects": [{ "ref": "product" }]
    }
  ]
}
```

最初の 8 つの要素は攻撃の起こりやすさを、残りの 8 つは攻撃を受けた場合の影響を表します。スコアはそれぞれの平均を掛け合わせたもので、最大値は 81 です。`checkout-api` はインターネットからのトラフィックを受け付け、決済を処理するため、どちらの値も高くなります。

2 つ目のドキュメントで変わるのは評価だけです。製品名は対象のプロジェクトに合わせていますが、対象を決めるのは `metadata.component` ではなく、アップロード先です。

```json title="vex-nightly-report.json" linenums="1"
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "version": 1,
  "metadata": {
    "component": {
      "bom-ref": "product",
      "type": "application",
      "name": "nightly-report",
      "version": "1.0.0"
    }
  },
  "vulnerabilities": [
    {
      "id": "INT-BILLING-0001",
      "source": { "name": "INTERNAL" },
      "ratings": [
        {
          "method": "OWASP",
          "vector": "OWASP/SL:1/M:1/O:0/S:2/ED:1/EE:1/A:1/ID:1/LC:2/LI:1/LAV:1/LAC:1/FD:1/RD:1/NC:2/PV:3",
          "score": 1.5
        }
      ],
      "affects": [{ "ref": "product" }]
    }
  ]
}
```

どちらのドキュメントにも `analysis` オブジェクトは含まれていません。`method: OWASP` の評価だけで十分です。

## 各ドキュメントをプロジェクトに適用する {#applying-each-document-to-its-project}

`checkout-api` を開き、**Apply VEX** を選択し、`vex-checkout-api.json` を選んで **Upload** を選択します。`nightly-report` でも `vex-nightly-report.json` を使って同じ操作を行います。

## 結果を比較する {#comparing-the-results}

`checkout-api` で `INT-BILLING-0001` の検出結果を開いて展開します。**OWASP RR Vector** というフィールドに、送信したベクトルが表示されています。**Audit Trail** には両方の値が記録されています。

```text linenums="1"
OWASP Vector: (None) → OWASP/SL:9/M:9/O:9/S:9/ED:9/EE:9/A:9/ID:9/LC:7/LI:7/LAV:7/LAC:7/FD:7/RD:7/NC:7/PV:7
OWASP Score: (None) → 63.0
```

`nightly-report` の同じ検出結果には、もう一方のベクトルと `1.5` のスコアが記録されています。

1 つの脆弱性、1 つのコンポーネント、2 つのデプロイ、2 つの評価です。深刻度はどちらのプロジェクトでも *Medium* のままです。インポートした評価は深刻度を置き換えるのではなく、深刻度と並んで記録されます。

## 次のステップ {#whats-next}

- [Exchanging VEX documents](../guides/user/exchanging-vex-documents.md): 判断をエクスポートし、製品全体ではなく個々のコンポーネントを対象にします。
- [VEX and VDR documents](../reference/vex-and-vdr.md#import): インポート時に従うルールと、エントリーがスキップされる理由を説明します。
- [Community integrations](../reference/community-integrations.md): これらのドキュメントを生成するツールを紹介します。
