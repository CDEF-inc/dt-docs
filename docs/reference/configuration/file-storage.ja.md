# ファイルストレージ

Dependency-Track は、バックグラウンド処理の中間データ(アップロードされた BOM、脆弱性分析の結果、サイズの大きい通知など)にファイルストレージを使います。ファイルは短期間だけ保持され、処理後に自動的に削除されます。

ストレージプロバイダーは [`dt.file-storage.provider`](properties.md#dtfile-storageprovider) で選択します。

どちらのプロバイダーも、保存するファイルを [zstd](https://facebook.github.io/zstd/) で圧縮します。圧縮レベルはプロバイダーごとに設定できます(デフォルト: 5、範囲: -7 から 22)。レベルを上げるほど圧縮率は高くなりますが、CPU の負荷も増えます。

## プロバイダー {#providers}

### ローカル {#local}

`local` プロバイダーは、ローカルファイルシステムにファイルを保存します。これがデフォルトです。

```ini
dt.file-storage.provider=local
dt.file-storage.local.directory=/data/storage
```

複数のインスタンスを実行する場合は、すべてのノードが同じディレクトリにアクセスできる必要があります。これには共有の永続ボリューム(たとえば NFS)が適しています。

設定:

- [`dt.file-storage.local.directory`](properties.md#dtfile-storagelocaldirectory)
- [`dt.file-storage.local.compression-level`](properties.md#dtfile-storagelocalcompression-level)

### S3 {#s3}

`s3` プロバイダーは、S3 互換のオブジェクトストア(AWS S3、MinIO など)にファイルを保存します。共有ボリュームを用意するのが難しい場合に使います。

バケットは起動前に作成しておく必要があります。Dependency-Track は起動時にバケットの存在を確認し、見つからない場合は起動に失敗します。

```ini
dt.file-storage.provider=s3
dt.file-storage.s3.endpoint=https://s3.amazonaws.com
dt.file-storage.s3.bucket=dtrack-files
dt.file-storage.s3.access-key=<access-key>
dt.file-storage.s3.secret-key=<secret-key>
dt.file-storage.s3.region=us-east-1
```

#### 認証 {#authentication}

`s3` プロバイダーの認証方法は `dt.file-storage.s3.credentials-source` で制御します。デフォルトは `static` です。

**静的な認証情報**(`credentials-source=static`、デフォルト)。`dt.file-storage.s3.access-key` と `dt.file-storage.s3.secret-key` の両方を設定します。どちらかが欠けていると、Dependency-Track は起動に失敗します。このモードは、どの S3 互換オブジェクトストアでも使えます。

**AWS 環境の認証情報**(`credentials-source=aws`)。Dependency-Track は実行環境から認証情報を解決し、次のソースのうち認証情報を提供する最初のものを使います。

1. 環境変数 `AWS_ACCESS_KEY_ID` と `AWS_SECRET_ACCESS_KEY`
2. AWS の共有設定ファイル(デフォルトでは `~/.aws/credentials`)
3. Amazon EKS の IAM Roles for Service Accounts(IRSA)
4. Amazon ECS のタスクロール
5. Amazon EC2 のインスタンスプロファイル

```ini
dt.file-storage.provider=s3
dt.file-storage.s3.endpoint=https://s3.us-east-1.amazonaws.com
dt.file-storage.s3.bucket=dtrack-files
dt.file-storage.s3.region=us-east-1
dt.file-storage.s3.credentials-source=aws
```

Dependency-Track は、起動時にバケットを確認する際に認証情報を解決します。どのソースからも認証情報が得られない場合や、`credentials-source=aws` と一緒に静的な認証情報が設定されている場合は、起動に失敗します。

!!! note
    Amazon EKS Pod Identity はサポートされていません。S3 クライアントは Pod Identity Agent が提供するトークンファイルを読み取らず、また、エージェントのエンドポイントはループバックアドレスではないため拒否します。Amazon EKS では IRSA を使ってください。

設定:

- [`dt.file-storage.s3.endpoint`](properties.md#dtfile-storages3endpoint)
- [`dt.file-storage.s3.bucket`](properties.md#dtfile-storages3bucket)
- [`dt.file-storage.s3.credentials-source`](properties.md#dtfile-storages3credentials-source)
- [`dt.file-storage.s3.access-key`](properties.md#dtfile-storages3access-key)
- [`dt.file-storage.s3.secret-key`](properties.md#dtfile-storages3secret-key)
- [`dt.file-storage.s3.region`](properties.md#dtfile-storages3region)
- [`dt.file-storage.s3.compression-level`](properties.md#dtfile-storages3compression-level)
- [`dt.file-storage.s3.connect-timeout-ms`](properties.md#dtfile-storages3connect-timeout-ms)
- [`dt.file-storage.s3.read-timeout-ms`](properties.md#dtfile-storages3read-timeout-ms)
- [`dt.file-storage.s3.write-timeout-ms`](properties.md#dtfile-storages3write-timeout-ms)
