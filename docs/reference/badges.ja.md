# バッジ

Dependency-Track は、プロジェクトの現在の脆弱性とポリシー違反のメトリクスを表示する SVG バッジを提供します。バッジを README ファイル、ダッシュボード、社内ドキュメントに埋め込むと、プロジェクトのセキュリティの状態をひと目で把握できます。

バッジの URL は、プロジェクトを UUID、`(name, version)`、または名前のみで参照します。名前のみの形式は、最新バージョンのフラグが付いたバージョンに解決されます。[バージョンを最新としてマークする](../guides/user/managing-project-versions.md#mark-a-version-as-latest)を参照してください。

## バッジの種類 {#badge-types}

### 脆弱なコンポーネント {#vulnerable-components}

プロジェクト内の脆弱なコンポーネントの深刻度別の内訳を表示します。バッジには存在する最も高い深刻度が表示され、有効な検出結果がない場合は *no vulns* と表示されます。

抑制された脆弱性は、バッジの件数から除外されます。

**プロジェクトの名前とバージョンで指定する場合:**

```text
https://dtrack.example.com/api/v1/badge/vulns/project/{name}/{version}
```

**プロジェクトの UUID で指定する場合:**

```text
https://dtrack.example.com/api/v1/badge/vulns/project/{uuid}
```

### ポリシー違反 {#policy-violations}

現在のポリシー違反の状態を表示します。有効な(抑制されていない)違反がある場合は *violations* と表示され、ない場合は *no violations* と表示されます。

**プロジェクトの名前とバージョンで指定する場合:**

```text
https://dtrack.example.com/api/v1/badge/violations/project/{name}/{version}
```

**プロジェクトの UUID で指定する場合:**

```text
https://dtrack.example.com/api/v1/badge/violations/project/{uuid}
```

## バッジを埋め込む {#embedding-badges}

=== "Markdown"

    ```markdown
    ![Vulnerabilities](https://dtrack.example.com/api/v1/badge/vulns/project/my-app/1.0.0)
    ![Policy Violations](https://dtrack.example.com/api/v1/badge/violations/project/my-app/1.0.0)
    ```

=== "HTML"

    ```html
    <img src="https://dtrack.example.com/api/v1/badge/vulns/project/my-app/1.0.0" alt="Vulnerabilities">
    <img src="https://dtrack.example.com/api/v1/badge/violations/project/my-app/1.0.0" alt="Policy Violations">
    ```
