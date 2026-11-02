# ワークロード ID フェデレーションを設定する

!!! note "5.2.0 以降で利用可能"

    それより前のバージョンでは、自動化処理の認証にはチーム API キーしか使えません。

ワークロード ID フェデレーションを使うと、CI ジョブ、Kubernetes の Pod、その他のワークロードは、自身のプラットフォームが発行したトークンを Dependency-Track のセッションと交換できます。そのため、ワークロードは API キーを保存する必要がありません。その背後にあるモデルについては、[About workload identity federation](../../concepts/workload-identity-federation.md) を参照してください。

プロバイダーとバインディングを作成するには、`ACCESS_MANAGEMENT` 権限、またはそのきめ細かいバリアントが必要です。

## 始める前に {#before-you-start}

プラットフォームから次の情報を集めます。

* OpenID Connect プロバイダーの場合は **issuer**。SPIFFE の場合は代わりに **trust domain**。
* Dependency-Track が HTTPS で issuer のディスカバリードキュメントにアクセスできるかどうか。アクセスできない場合は、issuer の公開署名鍵を JSON Web Key Set として用意する必要があります。
* ワークロードが受け取るトークンの正確な `sub` クレーム。プラットフォームによって形式が変わるため、推測せずに試行実行の際に 1 つ出力して確認します。

この Dependency-Track インスタンスに固有の **audience** を選びます。たとえば、インスタンスの URL です。同じ audience を、すべてのプロバイダーと、ワークロードが行うすべてのトークンリクエストに指定します。

## サービスアカウントを作成する {#create-a-service-account}

**Administration > Access Management > Service Accounts** で、ワークロードが使うアカウントを作成し、ワークロードに必要な権限だけを付与します。たとえば、`BOM_UPLOAD` と `PROJECT_CREATION_UPLOAD` です。

アカウントを使い回さず、ワークロードごとに専用のアカウントを用意します。ユーザー名は監査レコードに記録され、アカウントを停止するとちょうど 1 つのワークロードだけを遮断できます。

このアカウントには API キーを作成しないでください。

## ワークロード ID プロバイダーを登録する {#register-a-workload-identity-provider}

**Administration > Access Management > Workload Identity Providers** に移動し、**Create** を選択します。

![プロバイダー作成のモーダル](../../assets/images/guides/administration/configuring-workload-identity-federation/create-provider.png)

フォームに入力します。

| フィールド | 入力する内容 |
|:---|:---|
| **Name** | `github-actions` のような短い名前。ワークロードはトークンを交換するときにこの名前を送信します。後から変更できません。 |
| **Type** | CI システム、クラウドプラットフォーム、Kubernetes の場合は **OpenID Connect**。SPIRE やその他の SPIFFE 実装の場合は **SPIFFE**。後から変更できません。 |
| **Issuer** | トークンの `iss` クレームの正確な値。SPIFFE の場合は、`example.org` のような trust domain そのもの。 |
| **Audience** | トークンの `aud` クレームに含まれている必要がある値。 |
| **Signing Keys** | 公開鍵の取得元。[鍵の取得元を選ぶ](#choose-a-key-source)を参照してください。 |
| **Session Lifetime** | このプロバイダーから発行されるセッションの有効期間(秒)。60 から 86400 の間で、デフォルトは 3600 です。 |

Dependency-Track は保存時に鍵を取得し、取得に失敗するとプロバイダーを登録しません。

2 つのワークロードのグループで異なるセッション有効期間や異なる audience が必要な場合は、同じ issuer を 2 回登録します。バインディング自体には有効期間がありません。

### 鍵の取得元を選ぶ {#choose-a-key-source}

**Discover from the issuer's OpenID Connect configuration** は OpenID Connect プロバイダーのデフォルトで、Dependency-Track が issuer にアクセスできる場合は常にこれが適切な選択です。issuer の[ディスカバリードキュメント](../../reference/workload-identity.md#key-fetching)から鍵セットを解決します。

**Fetch from a JWKS URL** はディスカバリーを省略します。SPIFFE のバンドルエンドポイントや、ディスカバリードキュメントにはアクセスできないが鍵セットにはアクセスできる issuer に使います。

**Provide a JWK Set** は鍵を Dependency-Track に保存し、何も取得しません。主にセルフマネージドの Kubernetes クラスターなど、Dependency-Track からまったくアクセスできない issuer に使います。インラインの鍵は更新されないため、issuer が鍵をローテーションするたびにプロバイダーを更新します。

取得する URL には `https` を使う必要があります。[outbound fetch constraints](../../reference/workload-identity.md#outbound-fetch-constraints) の範囲内であれば、社内ネットワーク内の issuer も使えます。

## サブジェクトをサービスアカウントにバインドする {#bind-a-subject-to-the-service-account}

**Administration > Access Management > Service Accounts** に戻り、サービスアカウントを展開して、**Workload Identity Bindings** の下にあるプラスアイコンを選択します。

![バインディング作成のモーダル](../../assets/images/guides/administration/configuring-workload-identity-federation/create-binding.png)

| フィールド | 入力する内容 |
|:---|:---|
| **Provider** | 登録したプロバイダー。 |
| **Subject** | 受け付ける `sub` クレームの正確な値、またはそのプレフィックス。[subject matching](../../reference/workload-identity.md#subject-matching) を参照してください。 |
| **Condition** | トークンのクレームに対する任意の [CEL](../../reference/cel-expressions.md) 式。クレームは `claims` マップとして使えます。 |

共有の issuer では、サブジェクトのプレフィックスに少なくとも自分の組織を含めます。[Subjects and conditions](../../concepts/workload-identity-federation.md#subjects-and-conditions) を参照してください。

1 つのサービスアカウントは複数のバインディングを持てます。Dependency-Track は [matching order](../../reference/workload-identity.md#matching-order) に従って、最初に一致したバインディングを使います。

アクセスを取り消すには、バインディングを削除します。すでに発行されたセッションは、有効期限が切れるまで有効なままです。それらのセッションも遮断するには、サービスアカウントを停止します。

## ワークロードでトークンを交換する {#exchange-the-token-in-the-workload}

ワークロードは、プラットフォームのトークンを [RFC 8693](https://www.rfc-editor.org/rfc/rfc8693) のトークン交換エンドポイントである `/api/v2/oauth/token` に POST します。このリクエスト自体には認証は不要です。

```bash
ACCESS_TOKEN=$(curl -sSf -X POST \
  "https://dependency-track.example.com/api/v2/oauth/token" \
  -d "grant_type=urn:ietf:params:oauth:grant-type:token-exchange" \
  -d "subject_token_type=urn:ietf:params:oauth:token-type:jwt" \
  -d "subject_token=${PLATFORM_TOKEN}" \
  -d "workload_identity_provider=github-actions" \
  -d "service_account=ci-pipeline" \
  | jq -r .access_token)
```

結果をベアラートークンとして使います。

```bash
curl -sSf -X POST "https://dependency-track.example.com/api/v1/bom" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -F "project=${PROJECT_UUID}" \
  -F "bom=@bom.json"
```

トークンの交換はジョブごとに 1 回行い、ジョブの残りではそのセッションを再利用します。セッションはプロバイダーのセッション有効期間だけ存続し、セッションを更新するエンドポイントはありません。すべてのパラメーターとエラーレスポンスについては、[REST API v2 リファレンス](../../reference/api/v2.md)で `OAuth` タグが付いた操作を参照してください。

## プラットフォーム別の例 {#platform-examples}

`https://dependency-track.example.com` はインスタンスの URL に、`acme-inc` は自分の組織に置き換えてください。

<!-- vale Google.Headings = NO -->
### GitHub Actions {#github-actions}
<!-- vale Google.Headings = YES -->

GitHub Actions は、GitHub.com のすべてのアカウントで共有される単一の issuer から OpenID Connect の ID トークンを発行します。そのため、サブジェクトのプレフィックスには自分の組織を含める必要があります。クレームとその現在の形式は、GitHub の [OIDC リファレンス](https://docs.github.com/en/actions/reference/security/oidc)に記載されています。

プロバイダー:

| フィールド | 値 |
|:---|:---|
| Name | `github-actions` |
| Type | OpenID Connect |
| Issuer | `https://token.actions.githubusercontent.com` |
| Audience | `https://dependency-track.example.com` |
| Signing Keys | Discover from the issuer's OpenID Connect configuration |

組織内のすべてのリポジトリを対象とするバインディング:

| フィールド | 値 |
|:---|:---|
| Subject | `repo:acme-inc/*` |
| Condition | (なし) |

!!! warning "2 種類のサブジェクト形式があります"

    2026-07-15 以降に作成されたリポジトリと、オプトインした古いリポジトリでは、数値 ID を含む[イミュータブルなサブジェクト](https://docs.github.com/en/actions/reference/security/oidc#immutable-subject-claims)を使います。たとえば `repo:acme-inc@123456/app@456789:ref:refs/heads/main` です。`repo:acme-inc/*` というプレフィックスはこれに一致しません。こうしたリポジトリには `repo:acme-inc@123456/*` を使い、組織内で両方の形式が使われている場合は 2 つ目のバインディングを追加します。

ジョブには `id-token: write` 権限が必要で、自分の audience 向けにトークンをリクエストします。

```yaml title=".github/workflows/upload-bom.yml"
jobs:
  upload-bom:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
    - name: Upload BOM
      env:
        DT_URL: https://dependency-track.example.com
      run: |
        PLATFORM_TOKEN=$(curl -sSf \
          -H "Authorization: bearer ${ACTIONS_ID_TOKEN_REQUEST_TOKEN}" \
          "${ACTIONS_ID_TOKEN_REQUEST_URL}&audience=${DT_URL}" | jq -r .value)
        # Exchange PLATFORM_TOKEN as shown above.
```

`ACTIONS_ID_TOKEN_REQUEST_URL` にはすでにクエリー文字列が含まれているため、audience の前に `&` を付けます。

BOM のアップロードには、[`gh-upload-sbom`](https://github.com/DependencyTrack/gh-upload-sbom#workload-identity-federation) アクションがトークンのリクエストと交換を代わりに行います。

### GitLab CI {#gitlab-ci}

GitLab CI は、GitLab インスタンスの URL を issuer として ID トークンを発行します。GitLab.com ではすべてのアカウントがその issuer を共有するため、サブジェクトのプレフィックスには自分のグループを含める必要があります。クレームとその現在の形式は、GitLab の [ID token authentication](https://docs.gitlab.com/ci/secrets/id_token_authentication/) ガイドに記載されています。

プロバイダー:

| フィールド | 値 |
|:---|:---|
| Name | `gitlab` |
| Type | OpenID Connect |
| Issuer | `https://gitlab.com`、またはインスタンスの URL |
| Audience | `https://dependency-track.example.com` |
| Signing Keys | Discover from the issuer's OpenID Connect configuration |

ジョブでは、トークンと必要な audience を宣言します。

```yaml title=".gitlab-ci.yml"
upload-bom:
  id_tokens:
    DT_TOKEN:
      aud: https://dependency-track.example.com
  script:
  - ./upload-bom.sh  # Exchanges $DT_TOKEN as shown in "Exchange the token in the workload".
```

#### 環境で照合するには条件が必要 {#matching-on-the-environment-requires-a-condition}

GitLab のサブジェクトは `project_path:{group}/{project}:ref_type:{type}:ref:{branch}` です。このサブジェクトが示すのはプロジェクトと Git の ref だけです。デプロイ環境は別のクレームに含まれるため、「本番環境にデプロイするジョブだけ」のようなルールは**サブジェクトではまったく表現できません**。条件として記述します。

| フィールド | 値 |
|:---|:---|
| Subject | `project_path:acme-inc/*` |
| Condition | `claims.environment == "production" && claims.environment_protected == "true"` |

!!! note

    GitLab は、ブール値に見えるクレーム `environment_protected` と `ref_protected` を文字列 `"true"` と `"false"` としてエンコードします。そのため、`claims.environment_protected == true` は決して一致しません。

`environment` クレームは、`environment:` を宣言したジョブにだけ含まれます。存在しないクレームを読む条件はエラーになり、条件がエラーになったバインディングは一致しません。そのため、このバインディングはデプロイ以外のすべてのジョブを拒否します。

### Kubernetes {#kubernetes}

Pod は[プロジェクションされたサービスアカウントトークン][k8s-sa]で認証します。サブジェクトは `system:serviceaccount:{namespace}:{name}` です。

`kubeadm` で構築したクラスターは、クラスター内部の issuer `https://kubernetes.default.svc.cluster.local` からトークンを発行します。この名前はクラスター内でしか解決できないため、Dependency-Track はこの issuer に対してディスカバリーを実行できません。代わりに鍵をインラインで保存します。

```shell
kubectl get --raw /openid/v1/jwks
```

プロバイダー:

| フィールド | 値 |
|:---|:---|
| Name | `k8s-prod` |
| Type | OpenID Connect |
| Issuer | クラスターの issuer(`iss` に表示されるとおりの値) |
| Audience | `https://dependency-track.example.com` |
| Signing Keys | Provide a JWK Set(上記のコマンドの出力を貼り付ける) |

多くのマネージドサービスのように、Dependency-Track がクラスターのディスカバリードキュメントにアクセスできる場合は、クラスターの issuer URL でディスカバリーを使い、手動での鍵セットの設定は省略します。

1 つのサービスアカウントを対象とするバインディング:

| フィールド | 値 |
|:---|:---|
| Subject | `system:serviceaccount:ci:bom-uploader` |

Pod は、プロジェクションされたボリュームを通じて、適切な audience のトークンを要求します。

```yaml
spec:
  serviceAccountName: bom-uploader
  containers:
  - name: upload-bom
    image: acme-inc/upload-bom:1.0.0
    volumeMounts:
    - name: dt-token
      mountPath: /var/run/secrets/dependency-track
      readOnly: true
  volumes:
  - name: dt-token
    projected:
      sources:
      - serviceAccountToken:
          audience: https://dependency-track.example.com
          expirationSeconds: 3600
          path: token
```

コンテナーは `/var/run/secrets/dependency-track/token` からトークンを読み取り、`subject_token` として送信します。kubelet がこのファイルを更新するため、交換のたびに直前にファイルを読み取ります。

### SPIFFE と SPIRE {#spiffe-and-spire}

SPIFFE のワークロードは [JWT-SVID][spiffe-jwt-svid] を提示します。JWT-SVID では `iss` クレームが省略されることがあり、その代わりにサブジェクトに trust domain が含まれます。これらは **SPIFFE** タイプで登録します。

プロバイダー:

| フィールド | 値 |
|:---|:---|
| Name | `spire` |
| Type | SPIFFE |
| Issuer | `example.org`(`spiffe://` を除いた trust domain そのもの) |
| Audience | `https://dependency-track.example.com` |
| Signing Keys | Fetch from a JWKS URL(trust domain のバンドルエンドポイントを指定する) |

使えるのは、公的に信頼された証明書を持つバンドルエンドポイントだけです。これは [SPIFFE federation][spiffe-federation] の `https_web` プロファイルに当たります。そのようなエンドポイントを持たない trust domain では、バンドルをエクスポートしてインラインで保存します。

```shell
spire-server bundle show -format spiffe
```

バインディング:

| フィールド | 値 |
|:---|:---|
| Subject | `spiffe://example.org/ci/*` |
| Condition | (なし) |

SPIFFE のプレフィックスは `/` で終わる必要があります。プロバイダーの trust domain を変更すると、そのプロバイダーのすべてのバインディングが一致しなくなるため、変更後にバインディングのサブジェクトを更新します。

ワークロードは、[SPIRE エージェント][spire-agent]から audience 向けの JWT-SVID を取得します。

```shell
spire-agent api fetch jwt -audience https://dependency-track.example.com
```

## 設定を検証する {#verify-the-setup}

ワークロードから一度交換を実行し、そのセッションが持つ ID を確認します。

```bash
curl -sSf "https://dependency-track.example.com/api/v1/user/self" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}"
```

レスポンスの `username` は、`svc:` のプレフィックスが付いたサービスアカウント名です。

バインディングの **Last used** タイムスタンプは交換が成功するたびに更新されます。どのバインディングが一致したかを確認するには、これが最も手早い方法です。

## トラブルシューティング {#troubleshooting}

交換エンドポイントは、何が失敗しても同じ `invalid_request` エラーを返すため、どのチェックで失敗したかは示しません。API サーバーのログには、拒否されたすべての交換がセキュリティイベントとして記録されます。トークンの検証には成功したものの一致するバインディングがなかった場合は、トークンのクレームも記録されます。

## 関連項目 {#see-also}

* プロバイダー、バインディング、セッションの背後にあるモデルについては、[About workload identity federation](../../concepts/workload-identity-federation.md)。
* サブジェクトの照合ルール、条件の環境、トークンの要件については、[ワークロード ID のリファレンス](../../reference/workload-identity.md)。
* リクエストとレスポンスのスキーマについては、[REST API v2 リファレンス](../../reference/api/v2.md)。
* サービスアカウントに付与する権限については、[Permissions](../../reference/permissions.md)。

[k8s-sa]: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/
[spiffe-federation]: https://github.com/spiffe/spiffe/blob/main/standards/SPIFFE_Federation.md
[spiffe-jwt-svid]: https://github.com/spiffe/spiffe/blob/main/standards/JWT-SVID.md
[spire-agent]: https://spiffe.io/docs/latest/deploying/spire_agent/
