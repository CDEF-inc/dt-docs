# シークレットを管理する

Dependency-Track はサードパーティのシステムと連携します。その多くは、認証のために API キー、パスワード、アクセストークンといった何らかの認証情報を必要とします。こうしたシークレットは、漏洩を防ぐために安全に保管する必要があります。

Dependency-Track は、シークレットを一元的に管理する機能を備えています。ここで行った変更は、再起動しなくてもクラスター内のすべてのノードですぐに利用できるようになります。

設定された[プロバイダー](../administration/configuring-secret-management.md#providers)の機能に応じて、シークレットを[作成](#creating-secrets)、[更新](#updating-secrets)、[削除](#deleting-secrets)できます。

![シークレット管理の概要](../../assets/images/guides/user/managing-secrets/secret-management-overview.png)

!!! info
    作成したシークレットの値を*表示*することはできません。シークレットはプラットフォームによって必要に応じて復号されますが、REST API やユーザーインターフェースで開示されることはありません。

## シークレットを作成する {#creating-secrets}

`SECRET_MANAGEMENT` 権限または `SECRET_MANAGEMENT_CREATE` 権限を持つユーザーは、*Create* ボタンをクリックして新しいシークレットを作成できます。次の情報を入力するダイアログが開きます。

* シークレットの一意な名前
* シークレットの値
* 任意の説明

![シークレット作成ダイアログ](../../assets/images/guides/user/managing-secrets/create-secret.png)

## シークレットを更新する {#updating-secrets}

`SECRET_MANAGEMENT` 権限または `SECRET_MANAGEMENT_UPDATE` 権限を持つユーザーは、シークレットの *Actions* 列にある :fontawesome-solid-pen: ボタンをクリックして、既存のシークレットを更新できます。次の情報を入力するダイアログが開きます。

* 新しいシークレットの値
* 任意の説明

![シークレット更新ダイアログ](../../assets/images/guides/user/managing-secrets/update-secret.png)

*value* の入力欄を空のままにすると、既存の値が維持されます。新しい値を入力すると、古い値は元に戻せない形で上書きされます。

## シークレットを削除する {#deleting-secrets}

`SECRET_MANAGEMENT` 権限または `SECRET_MANAGEMENT_DELETE` 権限を持つユーザーは、シークレットの *Actions* 列にある :fontawesome-solid-trash-alt: ボタンをクリックして、既存のシークレットを削除できます。確認を求めるダイアログが開きます。

![シークレット削除ダイアログ](../../assets/images/guides/user/managing-secrets/delete-secret.png)

削除したシークレットは復元できません。慎重に操作してください。

## シークレットを使う {#using-secrets}

シークレットは、:key: が付いた設定フィールドで使用できます。

![設定フォームのシークレット入力フィールド](../../assets/images/guides/user/managing-secrets/use-secret.png)

これらのフィールドにはドロップダウンと検索の機能があり、利用可能なシークレットを簡単に見つけられます。
