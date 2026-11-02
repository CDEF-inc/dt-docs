# OpenID Connect を設定する

Dependency-Track は、[OpenID Connect](https://openid.net/specs/openid-connect-core-1_0.html)(OIDC)による SSO をサポートしています。有効にすると、ユーザーはローカルで管理されるパスワードではなく、外部の ID プロバイダー(IdP)を通じて認証します。

!!! note "フロントエンドの設定が必要"
    OIDC には、**API サーバー**と**フロントエンド**の両方の設定が必要です。API サーバーはトークンを検証し、フロントエンドは OIDC フローを開始します。両方に同じ発行者(issuer)とクライアント ID を設定してください。

## 認証フロー {#authentication-flow}

フロントエンドは、ユーザーを ID プロバイダーの認可エンドポイントにリダイレクトします。ユーザーが認証すると、IdP はフロントエンドに ID トークンを返し、フロントエンドはそれを検証のために API サーバーに転送します。API サーバーは IdP のディスカバリーエンドポイントに照らしてトークンを検証し、設定されたクレームからユーザー名を取り出します。ユーザーのプロビジョニングが有効な場合、Dependency-Track は初回ログイン時にアカウントを自動的に作成します。

## 前提条件 {#prerequisites}

- クライアント(アプリ)が設定済みの、OIDC 対応の ID プロバイダー。
- クライアントに、Dependency-Track のフロントエンドの URL がリダイレクト URI として登録されていること。
- IdP の[ディスカバリーエンドポイント](https://openid.net/specs/openid-connect-discovery-1_0.html)(`/.well-known/openid-configuration`)に API サーバーから到達できること。

## API サーバーの設定 {#api-server-configuration}

OIDC の設定はすべて[アプリのプロパティ](../../reference/configuration/properties.md)で行います。以下の例ではプロパティ名を使用しています。プロパティ名と環境変数の対応については、[アプリケーションの設定](../../reference/configuration/application.md#environment-variable-mapping)を参照してください。

```properties linenums="1"
dt.oidc.enabled=true
dt.oidc.issuer=https://idp.example.com
dt.oidc.client-id=dependency-track
dt.oidc.username-claim=preferred_username
```

### ユーザーのプロビジョニング {#user-provisioning}

有効にすると、Dependency-Track は初回ログイン時にユーザーアカウントを自動的に作成します。

```properties
dt.oidc.user-provisioning=true
```

### チームの同期 {#team-synchronisation}

有効にすると、Dependency-Track はグループ名の一覧を含むクレームからチームのメンバーシップを導き出します。API サーバーはまず ID トークンからクレームを読み取り、存在しない場合はプロバイダーの userinfo レスポンスにフォールバックします。どちらのソースでも動作するため、IdP が最も出力しやすい場所にクレームを設定してください。チームとそれらのグループ名の対応付けは、**Administration > Access Management > Teams** で行います。

```properties
dt.oidc.team-synchronization=true
dt.oidc.teams-claim=groups
```

## フロントエンドの設定 {#frontend-configuration}

フロントエンドのコンテナーに次の環境変数を渡して、フロントエンドが OIDC フローを開始するように設定します。

```yaml linenums="1" title="Docker Compose Example"
services:
  frontend:
    image: ghcr.io/dependencytrack/hyades-frontend:latest
    environment:
      API_BASE_URL: "https://dtrack.example.com"
      OIDC_ISSUER: "https://idp.example.com"
      OIDC_CLIENT_ID: "dependency-track"
      OIDC_SCOPE: "openid profile email"
      OIDC_LOGIN_BUTTON_TEXT: "Sign in with SSO"
```

`OIDC_LOGIN_BUTTON_TEXT` は省略可能です。設定すると、フロントエンドはその文字列を OpenID Connect のログインボタンのラベルとして使用します。空の場合、ボタンにはデフォルトの OpenID のロゴが表示されます。

フロントエンドのデフォルトは `code` フロー([PKCE](https://datatracker.ietf.org/doc/html/rfc7636) を使用する[認可コード](https://openid.net/specs/openid-connect-core-1_0.html#CodeFlowAuth)フロー)で、最新のすべての IdP で動作し、推奨される設定です。[インプリシットフロー](https://openid.net/specs/openid-connect-core-1_0.html#ImplicitFlowAuth)(`OIDC_FLOW: "implicit"`)が必要になるのは、PKCE と互換性のあるパブリッククライアントの構成がない IdP の場合だけです。[RFC 9700](https://datatracker.ietf.org/doc/html/rfc9700#name-implicit-grant) ではインプリシットフローは推奨されなくなったため、IdP がサポートしている場合は常に `code` を優先してください。

---

## ID プロバイダーの例 {#identity-provider-examples}

以下のセクションでは、主な IdP について動作確認済みの設定に関する注意事項を示します。いずれの場合も、プレースホルダーの値(`https://dtrack.example.com`、クライアント ID など)は環境に合わせて変更してください。

### Keycloak {#keycloak}

1. レルムに新しい **Client** を作成し、**Client Protocol** を `openid-connect` に設定します。
2. **Access Type** を `public` に設定します。
3. **Valid Redirect URIs** に `https://dtrack.example.com/*` を追加します。
4. チームの同期を行う場合は、**Mappers** で、トークンのクレーム名を `groups` とする **Group Membership** マッパーを追加します。

```properties
dt.oidc.issuer=https://keycloak.example.com/realms/your-realm
dt.oidc.client-id=dependency-track
dt.oidc.username-claim=preferred_username
```

### Microsoft Entra ID (Azure AD) {#microsoft-entra-id-azure-ad}

1. Azure portal で新しいアプリを登録します。
2. **Authentication** で、**Single-page app** のリダイレクト URI として `https://dtrack.example.com` を追加します。
3. **Token configuration** で、ID トークンに `preferred_username` のオプションのクレームを追加します。チームの同期を行う場合は、**Groups** クレームを追加します。

```properties
dt.oidc.issuer=https://login.microsoftonline.com/<tenant-id>/v2.0
dt.oidc.client-id=<application-client-id>
dt.oidc.username-claim=preferred_username
```

!!! note
    Entra ID はデフォルトで、グループを表示名ではなくオブジェクト ID(GUID)として返します。チームの同期で人が読めるグループ名を使いたい場合は、トークンの構成で **Groups claim** が `sAMAccountName` または `Group Display Name` を出力するように設定してください。

### Auth0 {#auth0}

1. Auth0 のダッシュボードで新しい **Single Page Application** を作成します。
2. **Allowed Callback URLs**、**Allowed Logout URLs**、**Allowed Web Origins** に `https://dtrack.example.com` を追加します。
3. グループやロールを含めるには、ID トークンに `groups` クレームを挿入するカスタムの Action または Rule を追加します。

```properties
dt.oidc.issuer=https://your-tenant.auth0.com/
dt.oidc.client-id=<auth0-client-id>
dt.oidc.username-claim=nickname
```

### GitLab {#gitlab}

1. GitLab インスタンスまたは `gitlab.com` で、**User Settings > Applications** を開きます。
2. リダイレクト URI として `https://dtrack.example.com` を追加します。
3. `openid`、`profile`、`email` のスコープを選択します。

```properties
dt.oidc.issuer=https://gitlab.com
dt.oidc.client-id=<application-id>
dt.oidc.username-claim=nickname
```

セルフホストの GitLab の場合は、`https://gitlab.com` を GitLab インスタンスの URL に置き換えてください。

### Google {#google}

1. GCP コンソールで、種類が **Web app** の **OAuth 2.0 Client ID** を作成します。
2. **Authorized JavaScript origins** と **Authorized redirect URIs** に `https://dtrack.example.com` を追加します。

```properties
dt.oidc.issuer=https://accounts.google.com
dt.oidc.client-id=<client-id>.apps.googleusercontent.com
dt.oidc.username-claim=email
```

!!! warning
    Google の **Web app** クライアントタイプでは、PKCE を使用する場合でもトークンエンドポイントで `client_secret` が必要です。また、Google は SPA 向けのパブリッククライアントタイプを提供していません。フロントエンドのデフォルトの `code` フローは、ブラウザーのコードにシークレットを公開しない限り、Google に対して完了できません。回避策として、フロントエンドで `OIDC_FLOW: "implicit"` を設定します。ただし、[RFC 9700](https://datatracker.ietf.org/doc/html/rfc9700#name-implicit-grant) ではインプリシットフローは推奨されなくなっていることに注意してください。よりセキュアな構成にするには、PKCE を使用するパブリッククライアントをサポートする IdP(たとえば Keycloak や Auth0)を Google の前段に置きます。

!!! note
    Google は、ID トークンにも userinfo レスポンスにもカスタムのグループクレームを出力しません。プロキシとなる IdP の層を使用しない限り、Google を IdP とする場合はチームの同期を利用できません。

### OneLogin {#onelogin}

1. OneLogin の管理ポータルで、新しい **OpenID Connect** アプリを作成します。
2. **Redirect URI** を `https://dtrack.example.com` に設定します。
3. アプリの SSO タブで **Client ID** と **Issuer URL** を控えておきます。

```properties
dt.oidc.issuer=https://your-subdomain.onelogin.com/oidc/2
dt.oidc.client-id=<client-id>
dt.oidc.username-claim=preferred_username
```

### AWS Cognito {#aws-cognito}

1. AWS コンソールで **User Pool** を作成します。
2. **App clients** で、**authorization code grant** フローを有効にし、**Generate a client secret** をオフにした(パブリッククライアント + PKCE)新しいクライアントを作成します。
3. **Callback URLs** に `https://dtrack.example.com` を追加します。
4. **App client settings** で、`openid`、`profile`、`email` のスコープを選択します。

```properties
dt.oidc.issuer=https://cognito-idp.<region>.amazonaws.com/<user-pool-id>
dt.oidc.client-id=<app-client-id>
dt.oidc.username-claim=cognito:username
```

---

## すべての OIDC プロパティ {#all-oidc-properties}

OIDC に関連する設定プロパティの一覧については、[設定リファレンス](../../reference/configuration/properties.md#dtoidcenabled)を参照してください。

## 関連項目 {#see-also}

- [権限](../../reference/permissions.md): IdP のグループを Dependency-Track のチームに対応付ける
- [LDAP を設定する](configuring-ldap.md): LDAP を使用する OIDC の代替手段
- [社内 CA の信頼を設定する](configuring-internal-ca.md): IdP の社内 TLS 証明書を信頼する
