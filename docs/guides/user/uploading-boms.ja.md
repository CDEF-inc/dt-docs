# BOM をアップロードする

Dependency-Track は、アップロードされた BOM からプロジェクトのコンポーネントインベントリーを構築します。アップロードのたびに、そのプロジェクトの脆弱性分析とポリシー評価が始まります。単発のアップロードにはフロントエンドを使い、ビルドのたびにインベントリーを追従させるにはパイプラインからアップロードします。

アップロードには `BOM_UPLOAD` [権限](../../reference/permissions.md)が必要です。最初のアップロードでプロジェクトを作成する場合は、`PROJECT_CREATION_UPLOAD`、`PORTFOLIO_MANAGEMENT`、`PORTFOLIO_MANAGEMENT_CREATE` のいずれかも必要です。パイプラインでは、これらの権限を個人ではなく[サービスアカウント](../../concepts/access-control.md#service-accounts)に付与します。

Dependency-Track が受け付ける BOM の形式については、[File formats](../../reference/file-formats.md) を参照してください。

## フロントエンドからアップロードする {#upload-from-the-ui}

1. プロジェクトを開きます。
2. **Upload BOM** を選択します。
3. **Browse** を選択して BOM ファイルを選び、**Upload** を選択します。

<!-- vale Google.Headings = NO -->
## REST API でアップロードする {#upload-via-rest-api}
<!-- vale Google.Headings = YES -->

BOM をマルチパートリクエストとして `/api/v1/bom` に送信します。

=== "Bash"

    ```bash
    curl -sSf -X POST "https://dependency-track.example.com/api/v1/bom" \
      -H "X-Api-Key: ${DT_API_KEY}" \
      -F "projectName=my-app" \
      -F "projectVersion=1.2.3" \
      -F "autoCreate=true" \
      -F "bom=@bom.json"
    ```

=== "PowerShell"

    ```powershell
    Invoke-RestMethod -Method Post -Uri "https://dependency-track.example.com/api/v1/bom" `
      -Headers @{ "X-Api-Key" = $env:DT_API_KEY } `
      -Form @{
        projectName    = "my-app"
        projectVersion = "1.2.3"
        autoCreate     = "true"
        bom            = Get-Item "bom.json"
      }
    ```

対象のプロジェクトは、`project`(プロジェクトの UUID)で指定する**か**、`projectName` と `projectVersion` で指定します。`autoCreate=true` を指定すると、プロジェクトが存在しない場合に Dependency-Track がプロジェクトを作成します。プロジェクトを作成するときは、次の任意のフィールドも適用します。

* `parentUUID`、または `parentName` と `parentVersion`: プロジェクトを[階層](organizing-projects.md)内に配置します。
* `projectTags`: カンマ区切りのタグのリストです。
* `isLatest=true`: そのバージョンを[最新](managing-project-versions.md#mark-a-version-as-latest)としてマークします。

`isActive` は、プロジェクトのアクティブ状態を変更する場合にのみ送信します。このフィールドは既存のプロジェクトにも適用されます。

大きな BOM で帯域幅を節約するには、`gzip` または `zstd` でファイルを圧縮し、その種類を宣言します。curl では、たとえば `-F "bom=@bom.json.gz;type=application/gzip"` を使います。`zstd` の場合は `application/zstd` を使います。

スキーマ検証に失敗した BOM には `400 Bad Request` が返されます。すべてのフィールドとレスポンスについては、[REST API v1 リファレンス](../../reference/api/v1.md)の `UploadBom` 操作を参照してください。

保存された API キーを使わずに認証するには、[ワークロード ID フェデレーションを設定する](../administration/configuring-workload-identity-federation.md#exchange-the-token-in-the-workload)の説明に従ってプラットフォームのトークンをセッションと交換し、`X-Api-Key` の代わりに `Authorization: Bearer ${ACCESS_TOKEN}` を送信します。

## 処理の完了を待つ {#wait-for-processing-to-finish}

アップロードは、Dependency-Track が BOM を保存した時点ですぐに返ります。処理はバックグラウンドで続きます。レスポンスには、処理を追跡するためのトークンが含まれます。

```json
{
  "token": "6a8d3bd2-3f7d-4b9c-9a54-7c1f0e1c2b4e",
  "projectUuid": "dadec8ad-7053-4e8c-8044-7b6ef698e08d"
}
```

後続のステップで結果が必要な場合(たとえば、ポリシー違反でビルドを失敗させる場合)は、処理が終わるまで `/api/v1/event/token/{token}` をポーリングします。

```json
{
  "processing": true,
  "status": "RUNNING"
}
```

`status` は `PENDING`、`RUNNING`、`COMPLETED`、`FAILED` のいずれかです。トークンは BOM のインポートと、それに続く脆弱性分析とポリシー評価を対象とするため、`COMPLETED` は、プロジェクトの検出結果とポリシー違反にアップロードした BOM が反映されていることを意味します。Dependency-Track が認識していないトークンの場合、レスポンスには `"processing": false` が含まれ、`status` は含まれません。

=== "Bash"

    ```bash
    TOKEN=$(curl -sSf -X POST "https://dependency-track.example.com/api/v1/bom" \
      -H "X-Api-Key: ${DT_API_KEY}" \
      -F "projectName=my-app" \
      -F "projectVersion=1.2.3" \
      -F "autoCreate=true" \
      -F "bom=@bom.json" \
      | jq -r .token)

    while true; do
      STATUS=$(curl -sSf -H "X-Api-Key: ${DT_API_KEY}" \
        "https://dependency-track.example.com/api/v1/event/token/${TOKEN}" \
        | jq -r '.status // "UNKNOWN"')
      case "${STATUS}" in
        COMPLETED) break ;;
        FAILED | UNKNOWN) echo "BOM processing ended with status ${STATUS}" >&2; exit 1 ;;
      esac
      sleep 5
    done
    ```

=== "PowerShell"

    ```powershell
    $headers = @{ "X-Api-Key" = $env:DT_API_KEY }
    $upload = Invoke-RestMethod -Method Post -Uri "https://dependency-track.example.com/api/v1/bom" `
      -Headers $headers `
      -Form @{
        projectName    = "my-app"
        projectVersion = "1.2.3"
        autoCreate     = "true"
        bom            = Get-Item "bom.json"
      }

    while ($true) {
      $status = (Invoke-RestMethod -Headers $headers `
        -Uri "https://dependency-track.example.com/api/v1/event/token/$($upload.token)").status ?? "UNKNOWN"
      if ($status -eq "COMPLETED") { break }
      if ($status -in "FAILED", "UNKNOWN") { throw "BOM processing ended with status $status" }
      Start-Sleep -Seconds 5
    }
    ```

ループの実行時間は、CI システムのジョブのタイムアウトで制限します。

<!-- vale Google.Headings = NO -->
## GitHub Actions からアップロードする {#upload-from-github-actions}
<!-- vale Google.Headings = YES -->

[`gh-upload-sbom`](https://github.com/DependencyTrack/gh-upload-sbom) アクションは、アップロードのリクエストをラップします。

```yaml
- name: Upload BOM
  id: upload
  uses: DependencyTrack/gh-upload-sbom@v4
  with:
    server-hostname: dependency-track.example.com
    api-key: ${{ secrets.DEPENDENCYTRACK_APIKEY }}
    project-name: my-app
    project-version: ${{ github.ref_name }}
    bom-filename: bom.json
    auto-create: true
```

API キーのシークレットを使わずに認証するには、`api-key` を `workload-identity-provider`、`service-account`、`oidc-audience` に置き換え、ジョブに `id-token: write` を付与します。アクションの [workload identity federation](https://github.com/DependencyTrack/gh-upload-sbom#workload-identity-federation) セクションと、Dependency-Track 側の設定については [GitHub Actions](../administration/configuring-workload-identity-federation.md#github-actions) を参照してください。

このアクションは処理の完了を待ちません。アップロードのトークンを `steps.upload.outputs.token` として公開するため、後続のステップで `TOKEN` にその出力を設定し、[処理の完了を待つ](#wait-for-processing-to-finish)のポーリングループを実行できます。

<!-- vale Google.Headings = NO -->
## Jenkins からアップロードする {#upload-from-jenkins}
<!-- vale Google.Headings = YES -->

[Dependency-Track Jenkins プラグイン](https://plugins.jenkins.io/dependency-track/)は、ビルドステップとして BOM をアップロードします。設定方法はプラグインのドキュメントを参照してください。その他の CI システムでは、[REST API でアップロードする](#upload-via-rest-api)で示したように REST API を呼び出します。
