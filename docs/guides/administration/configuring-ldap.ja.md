# LDAP を設定する

Dependency-Track は、Microsoft Active Directory、ApacheDS、その他の LDAP 互換サーバーなどの LDAP ディレクトリに対してユーザーを認証できます。有効にすると、ユーザーはローカルで管理されるパスワードではなく、ディレクトリの認証情報でログインします。

## 認証フロー {#authentication-flow}

Dependency-Track は LDAP ユーザーを認証する際、まずサービスアカウントでバインドしてユーザーのディレクトリエントリーを検索し、次にユーザー自身の認証情報でバインドを試みてパスワードを検証します。成功すると、システムはアクセスを許可します。ユーザーのプロビジョニングが有効な場合、Dependency-Track は初回ログイン時にアカウントを自動的に作成します。

ログインに成功するたびに、Dependency-Track はユーザーの識別名(DN)とメールアドレスをディレクトリから更新し、(チームの同期が有効な場合は)ユーザーの現在の LDAP グループに基づいてチームのメンバーシップを再評価します。一度もログインしないユーザーは、プロビジョニング時に取得した属性を保持し続けます。

## 前提条件 {#prerequisites}

- ユーザーとグループの読み取り権限を持つ、LDAP ディレクトリ内のサービスアカウント。
- Dependency-Track の API サーバーから LDAP サーバーへのネットワーク接続。
- LDAPS(本番環境では推奨)の場合は、LDAP サーバー上の有効な TLS 証明書。社内 CA が証明書を発行した場合は、[社内 CA の信頼を設定する](configuring-internal-ca.md)を参照してください。

## 設定 {#configuration}

LDAP の設定はすべて[アプリケーションのプロパティ](../../reference/configuration/properties.md)で行います。以下の例ではプロパティ名を使います。プロパティ名と環境変数の対応については、[Application configuration](../../reference/configuration/application.md#environment-variable-mapping) を参照してください。

### 最小限の設定 {#minimal-configuration}

LDAP を有効にし、サーバーへの接続を設定します。

```properties linenums="1"
dt.ldap.enabled=true
dt.ldap.server-url=ldap://ldap.example.com:389
dt.ldap.base-dn=dc=example,dc=com
dt.ldap.security-auth=simple
dt.ldap.bind-username=cn=dt-service,dc=example,dc=com
dt.ldap.bind-password=changeme
dt.ldap.username-format=uid=%s,ou=users,dc=example,dc=com
dt.ldap.name-attribute=cn
dt.ldap.mail-attribute=mail
```

!!! tip
    Dependency-Track は、`dt.ldap.username-format` 内のプレースホルダー `%s` を、ログイン時に入力されたユーザー名に置き換えます。

### ユーザーのプロビジョニング {#user-provisioning}

有効にすると、LDAP ユーザーが初めてログインしたときに Dependency-Track がアカウントを自動的に作成します。無効の場合は、ユーザーがログインできるようになる前に、管理者が各アカウントを作成する必要があります。

```properties
dt.ldap.user-provisioning=true
```

### チームの同期 {#team-synchronisation}

有効にすると、Dependency-Track はチームのメンバーシップを LDAP グループのメンバーシップと同期させます。チームと LDAP グループの対応付けは **Administration > Access Management > Teams** で行います。

```properties
dt.ldap.team-synchronization=true
dt.ldap.user-groups-filter=(&(objectClass=groupOfUniqueNames)(uniqueMember={USER_DN}))
dt.ldap.group-search-filter=(&(objectClass=groupOfUniqueNames)(cn=*{SEARCH_TERM}*))
```

!!! tip
    Dependency-Track は、`{USER_DN}` を認証されたユーザーの識別名に、`{SEARCH_TERM}` をフロントエンドでの検索入力に置き換えます。

---

## 動作確認済みの設定 {#tested-configurations}

以下の設定は、特定のディレクトリ実装で動作します。ベース DN、バインドの認証情報、属性名などの値は、環境に合わせて変更してください。

### Microsoft Active Directory {#microsoft-active-directory}

Active Directory では、フォレスト全体の検索にグローバルカタログのポート(3268/3269)を使います。ユーザーは通常、ユーザープリンシパル名(`user@domain.com`)で認証します。

```properties linenums="1"
dt.ldap.enabled=true
dt.ldap.server-url=ldap://ldap.example.com:3268
dt.ldap.base-dn=dc=example,dc=com
dt.ldap.security-auth=simple
dt.ldap.bind-username=CN=DT Service Account,DC=example,DC=com
dt.ldap.bind-password=changeme
dt.ldap.username-format=%s@example.com
dt.ldap.name-attribute=userPrincipalName
dt.ldap.mail-attribute=mail
dt.ldap.user-groups-filter=(&(objectClass=group)(objectCategory=Group)(member:1.2.840.113556.1.4.1941:={USER_DN}))
dt.ldap.group-search-filter=(&(objectClass=group)(objectCategory=Group)(cn=*{SEARCH_TERM}*))
```

!!! tip
    ユーザーグループのフィルターにある `member:1.2.840.113556.1.4.1941:=` という OID は、再帰的なグループメンバーシップの検索(LDAP_MATCHING_RULE_IN_CHAIN)を有効にします。これにより、Dependency-Track はネストされたグループのメンバーシップを正しく解決します。

LDAPS(本番環境では推奨)を使う場合は、ポートを `3269` に変更し、URL を更新します。

```properties
dt.ldap.server-url=ldaps://ldap.example.com:3269
```

### ApacheDS {#apacheds}

```properties linenums="1"
dt.ldap.enabled=true
dt.ldap.server-url=ldap://ldap.example.com:389
dt.ldap.base-dn=dc=example,dc=com
dt.ldap.security-auth=simple
dt.ldap.bind-username=uid=admin,ou=system
dt.ldap.bind-password=changeme
dt.ldap.username-format=uid=%s,ou=users,dc=example,dc=com
dt.ldap.name-attribute=cn
dt.ldap.mail-attribute=mail
dt.ldap.user-groups-filter=(&(objectClass=groupOfUniqueNames)(uniqueMember={USER_DN}))
dt.ldap.group-search-filter=(&(objectClass=groupOfUniqueNames)(cn=*{SEARCH_TERM}*))
```

### Fedora 389 Directory Server {#fedora-389-directory-server}

```properties linenums="1"
dt.ldap.enabled=true
dt.ldap.server-url=ldap://ldap.example.com:389
dt.ldap.base-dn=dc=example,dc=com
dt.ldap.security-auth=simple
dt.ldap.bind-username=cn=Directory Manager
dt.ldap.bind-password=changeme
dt.ldap.username-format=uid=%s,ou=people,dc=example,dc=com
dt.ldap.name-attribute=uid
dt.ldap.mail-attribute=mail
dt.ldap.user-groups-filter=(&(objectClass=groupOfUniqueNames)(uniqueMember={USER_DN}))
dt.ldap.group-search-filter=(&(objectClass=groupOfUniqueNames)(cn=*{SEARCH_TERM}*))
```

### NetIQ / Novell eDirectory {#netiq-novell-edirectory}

eDirectory では通常、ポート 636 の LDAPS と、組織を基点とした DN 構造を使います。

```properties linenums="1"
dt.ldap.enabled=true
dt.ldap.server-url=ldaps://ldap.example.com:636
dt.ldap.base-dn=o=example
dt.ldap.security-auth=simple
dt.ldap.bind-username=cn=admin,o=example
dt.ldap.bind-password=changeme
dt.ldap.username-format=uid=%s,ou=users,o=example
dt.ldap.name-attribute=uid
dt.ldap.mail-attribute=mail
dt.ldap.user-groups-filter=(&(objectClass=groupOfUniqueNames)(uniqueMember={USER_DN}))
dt.ldap.group-search-filter=(&(objectClass=groupOfUniqueNames)(cn=*{SEARCH_TERM}*))
```

---

## LDAP のすべてのプロパティ {#all-ldap-properties}

LDAP 関連の設定プロパティの完全な一覧と、それぞれの型、デフォルト値、対応する環境変数については、[設定リファレンス](../../reference/configuration/properties.md#ldap)を参照してください。

## 関連項目 {#see-also}

- [Permissions](../../reference/permissions.md): LDAP グループを Dependency-Track のチームに対応付ける
- [OpenID Connect を設定する](configuring-oidc.md): OpenID Connect を使った LDAP の代替手段
- [社内 CA の信頼を設定する](configuring-internal-ca.md): LDAPS 用に社内の TLS 証明書を信頼する
