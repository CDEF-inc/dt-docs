# シークレット管理を設定する

Dependency-Track は、差し替え可能なシークレットストレージプロバイダーをサポートしています。このガイドでは、プロバイダーの選択と暗号鍵の管理について説明します。

アプリでシークレットを作成、更新、削除する方法については、[シークレットを管理する](../user/managing-secrets.md)を参照してください。

## プロバイダー {#providers}

シークレット管理の仕組みは、さまざまなプロバイダーをサポートするように設計されています。

現在利用できるのは、[データベース](#database)プロバイダーと[環境変数](#environment-variables)プロバイダーだけです。[AWS secrets manager]、[Azure Key Vault]、[HashiCorp Vault] / [OpenBao] などの外部サービスのサポートが計画されています。これらの選択肢の実装はユーザーの要望に応じて進めるため、必要な場合は機能拡張リクエストを提出してください。

### データベース {#database}

デフォルトのプロバイダーで、シークレットを `SECRET` データベーステーブルに保存します。

シークレットは [AES-GCM-256] で暗号化されます。このプロバイダーは、[鍵のローテーション](#kek-rotation)を可能にするために[エンベロープ暗号化][envelope encryption]を実装しています。すべての暗号処理は [Google Tink] が担います。

#### 設定 {#configuration}

このプロバイダーは、次のプロパティで設定できます。

* [`dt.secret-management.provider`](../../reference/configuration/properties.md#dtsecret-managementprovider)
* [`dt.secret-management.database.datasource.name`](../../reference/configuration/properties.md#dtsecret-managementdatabasedatasourcename)
* [`dt.secret-management.database.kek`](../../reference/configuration/properties.md#dtsecret-managementdatabasekek)
* [`dt.secret-management.database.kek-keyset.path`](../../reference/configuration/properties.md#dtsecret-managementdatabasekek-keysetpath)
* [`dt.secret-management.database.kek-keyset.create-if-missing`](../../reference/configuration/properties.md#dtsecret-managementdatabasekek-keysetcreate-if-missing)

!!! note
    [データソースの設定](../../reference/configuration/datasources.md)に関するドキュメントも参照してください。

#### 鍵の管理 {#key-management}

シークレットは[エンベロープ暗号化][envelope encryption]で暗号化されます。各シークレットには専用のデータ暗号化鍵(DEK)があり、DEK 自体は鍵暗号化鍵(KEK)で暗号化されます。KEK は、[Google Tink] が管理する[キーセット][keysets]ファイルに保存されます。

KEK キーセットは起動時に自動的に作成されますが、[手動で作成したキーセット](#creating-kek-keysets)を指定することもできます。本番環境のデプロイでは、[Kubernetes のシークレット][Kubernetes secrets]などの仕組みを使って **KEK キーセットを実行時にマウント**し、キーセットファイルをアプリのユーザーだけが読み取れるようにしてください。

#### 設定ベースの KEK {#config-based-kek}

キーセットファイルの代わりに、[`dt.secret-management.database.kek`](../../reference/configuration/properties.md#dtsecret-managementdatabasekek) プロパティで、base64 エンコードした AES-256 鍵(32 バイト)として KEK を直接指定することもできます。このプロパティを設定すると、キーセットファイルの設定よりも優先されます。

これは、ノード間でキーセットファイルを共有するのが不便なマルチインスタンス構成で役立ちます。たとえば、値をファイルではなく環境変数として公開するシークレットマネージャーに KEK を保存している場合です。

!!! warning
    設定ベースの KEK は [KEK のローテーション](#kek-rotation)をサポート**しません**。KEK をローテーションする予定がある場合は、代わりに[ファイルベースのキーセット方式](#creating-kek-keysets)を使用してください。

#### KEK キーセットを作成する {#creating-kek-keysets}

新しい KEK キーセットを作成するには、次の前提条件を満たす必要があります。

* 動作する [Google Tinkey] のインストール

`AES256_GCM` プリセットを使用して新しいキーセットを作成します。

```shell linenums="1"
tinkey create-keyset \
  --key-template AES256_GCM \
  --out secret-management-kek.json \
  --out-format json
```

新しいキーセット内の鍵を一覧表示し、有効な鍵が生成されたことを確認します。

```shell linenums="1"
tinkey list-keyset \
  --in secret-management-kek.json \
  --in-format json
```

??? info "出力例"
    ```
    primary_key_id: 1115312215
    key_info {
      type_url: "type.googleapis.com/google.crypto.tink.AesGcmKey"
      status: ENABLED
      key_id: 1115312215
      output_prefix_type: TINK
    }
    ```

次の手順で、Dependency-Track にこのキーセットを使用させます。

1. ファイルを API サーバーのコンテナーにマウントします
2. [`kek-keyset.path`](../../reference/configuration/properties.md#dtsecret-managementdatabasekek-keysetpath) を、ファイルをマウントした場所を指すように設定します
3. [`kek-keyset.create-if-missing`](../../reference/configuration/properties.md#dtsecret-managementdatabasekek-keysetcreate-if-missing) オプションを無効にします

??? example "Kubernetes Secret の例"
    ```yaml linenums="1"
    apiVersion: v1
    kind: Secret
    metadata:
      name: secret-management-kek
    type: Opaque
    stringData:
      keyset.json: |
        {
          "primaryKeyId": 1115312215,
          "key": [
            {
              "keyData": {
                "typeUrl": "type.googleapis.com/google.crypto.tink.AesGcmKey",
                "value": "GhD...",
                "keyMaterialType": "SYMMETRIC"
              },
              "status": "ENABLED",
              "keyId": 1115312215,
              "outputPrefixType": "TINK"
            }
          ]
        }
    ---
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: dependency-track-apiserver
    spec:
      template:
        spec:
          containers:
          - name: apiserver
            # ...
            env:
            - name: DT_SECRET_MANAGEMENT_PROVIDER
              value: "database"
            - name: DT_SECRET_MANAGEMENT_DATABASE_KEK_KEYSET_PATH
              value: "/run/secrets/secret-management-kek/keyset.json"
            - name: DT_SECRET_MANAGEMENT_DATABASE_KEK_KEYSET_CREATE_IF_MISSING
              value: "false"
            volumeMounts:
            - name: kek-keyset
              mountPath: /run/secrets/secret-management-kek
              readOnly: true
          volumes:
          - name: kek-keyset
            secret:
              secretName: secret-management-kek
              defaultMode: 0400
    ```

#### KEK のローテーション {#kek-rotation}

KEK のローテーションを行うには、次の前提条件を満たす必要があります。

* 動作する [Google Tinkey] のインストール
* KEK キーセットへのアクセス

まず、キーセットに現在含まれている鍵を一覧表示します。

```shell linenums="1"
tinkey list-keyset \
  --in secret-management-kek.json \
  --in-format json
```

??? info "出力例"
    ```
    primary_key_id: 1115312215
    key_info {
      type_url: "type.googleapis.com/google.crypto.tink.AesGcmKey"
      status: ENABLED
      key_id: 1115312215
      output_prefix_type: TINK
    }
    ```

`AES256_GCM` テンプレートを使用して新しい鍵を追加します。

```shell linenums="1"
tinkey add-key \
  --key-template AES256_GCM \
  --in secret-management-kek.json \
  --in-format json \
  --out secret-management-kek-new.json \
  --out-format json
```

新しいキーセットファイル内の鍵を一覧表示し、複数の鍵が含まれるようになったことを確認します。

```shell linenums="1"
tinkey list-keyset \
  --in secret-management-kek-new.json \
  --in-format json
```

??? info "出力例"
    ```
    primary_key_id: 1115312215
    key_info {
      type_url: "type.googleapis.com/google.crypto.tink.AesGcmKey"
      status: ENABLED
      key_id: 1115312215
      output_prefix_type: TINK
    }
    key_info {
      type_url: "type.googleapis.com/google.crypto.tink.AesGcmKey"
      status: ENABLED
      key_id: 3812494172
      output_prefix_type: TINK
    }
    ```

両方の鍵が `ENABLED` になっていますが、`primary_key_id` では引き続き古い鍵の ID が参照されていることに注目してください。新しいデータを暗号化するのはプライマリ鍵だけですが、`ENABLED` になっているほかの鍵も復号には引き続き使用できます。

新しいキーセットを Dependency-Track インスタンスにロールアウトします。これにより、後で新しい KEK をプライマリ鍵にしたときに、すべてのインスタンスが新しい KEK を使って DEK を復号できるようになります。それまでは、DEK は引き続き古い KEK で暗号化されます。

!!! warning
    KEK キーセットは起動時にのみ読み込まれます。DT インスタンスを再起動し、新しい KEK キーセットファイルがマウントされていることを確認してください。

新しい KEK 鍵のロールアウトが完了したら、その鍵をプライマリ鍵に昇格できます。

```shell linenums="1"
tinkey promote-key \
  --in secret-management-kek-new.json \
  --in-format json \
  --key-id 3812494172 \
  --out secret-management-kek-new-promoted.json \
  --out-format json
```

もう一度鍵を一覧表示し、昇格が成功したことを確認します。

```shell linenums="1"
tinkey list-keyset \
  --in secret-management-kek-new-promoted.json \
  --in-format json
```

??? info "出力例"
    ```
    primary_key_id: 3812494172
    key_info {
      type_url: "type.googleapis.com/google.crypto.tink.AesGcmKey"
      status: ENABLED
      key_id: 1115312215
      output_prefix_type: TINK
    }
    key_info {
      type_url: "type.googleapis.com/google.crypto.tink.AesGcmKey"
      status: ENABLED
      key_id: 3812494172
      output_prefix_type: TINK
    }
    ```

`primary_key_id` が新しい鍵を参照していることを確認したら、この新しいキーセットを Dependency-Track のデプロイにロールアウトします。

これ以降、新しいシークレットが作成されるか既存のシークレットの値が変更されるたびに、DEK は新しい KEK で暗号化されます。

!!! warning
    `tinkey` では、キーセット内の鍵をオフにしたり、破棄したり、削除したりできます。これらの操作を行う前に、データベース内の暗号化されたシークレットを復号できなくなる可能性があることに注意してください。Dependency-Track には現在、既存のシークレットを再暗号化する仕組みがありません。これが重要な場合は、機能拡張リクエストを提出してください。

### 環境変数 {#environment-variables}

環境変数からシークレットを読み取るシンプルなプロバイダーです。テスト用のデプロイ、シークレットがめったに変わらない場合、またはサービスの可用性が重要でない場合に便利です。

!!! warning
    このプロバイダーは**読み取り専用**です。シークレットは起動時に**一度だけ**環境から読み込まれます。実行時にシークレットを*追加*、*更新*、*削除*することは**できません**。シークレットの値を変更するには、Dependency-Track インスタンスを再起動する必要があります。

プロバイダーに認識させるには、環境変数に `DT_SECRET_` というプレフィックスを付ける必要があります。プレフィックスの大文字と小文字は区別されませんが、プレフィックスの*後*の大文字と小文字はそのまま保持されます。例:

```ini linenums="1"
# Picked up as secret "GITHUB_TOKEN":
DT_SECRET_GITHUB_TOKEN=foo

# Picked up as secret "github_token":
dt_secret_github_token=foo

# NOT recognized as secret due to missing prefix:
GITHUB_TOKEN=foo
```

プロバイダーは、起動時に検出したシークレットの名前をログに出力します。シークレットが 1 つも見つからなかった場合は、警告のログメッセージも出力します。

#### 設定 {#configuration_1}

このプロバイダーは、次のプロパティで設定できます。

* [`dt.secret-management.provider`](../../reference/configuration/properties.md#dtsecret-managementprovider)

??? info "設定例"
    ```ini linenums="1"
    dt.secret-management.provider=env
    ```

[AES-GCM-256]: https://en.wikipedia.org/wiki/Galois/Counter_Mode
[AWS secrets manager]: https://aws.amazon.com/secrets-manager/
[Azure Key Vault]: https://azure.microsoft.com/en-us/products/key-vault
[Google Tink]: https://developers.google.com/tink/what-is
[Google Tinkey]: https://developers.google.com/tink/tinkey-overview
[HashiCorp Vault]: https://www.hashicorp.com/en/products/vault
[Kubernetes secrets]: https://kubernetes.io/docs/concepts/configuration/secret/
[OpenBao]: https://openbao.org/
[envelope encryption]: https://en.wikipedia.org/wiki/Hybrid_cryptosystem#Envelope_encryption
[keysets]: https://developers.google.com/tink/design/keysets
