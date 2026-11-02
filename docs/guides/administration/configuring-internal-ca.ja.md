# 社内 CA の信頼を設定する

デフォルトでは、Dependency-Track のコンテナーイメージに同梱されている Java ランタイムは、広く知られた公的な認証局だけを信頼します。環境で社内 CA やプライベート CA が署名した TLS 証明書を使っている場合、それらのエンドポイントへの接続は証明書の検証エラーで失敗します。

```text
PKIX path building failed: sun.security.provider.certpath.SunCertPathBuilderException:
unable to find valid certification path to requested object
```

この問題がよく発生するケースは次のとおりです。

- **LDAPS**: TLS を使って LDAP サーバーに接続する場合([LDAP を設定する](configuring-ldap.md))
- **OIDC**: ID プロバイダーがプライベートに署名された証明書を使っている場合([OpenID Connect を設定する](configuring-oidc.md))
- **HTTP プロキシ**: TLS を傍受するプロキシが Dependency-Track と外部サービスの間にある場合
- **社内の脆弱性データソース**: プライベートに署名された証明書を使う、NVD や OSV の社内ミラーがある場合([脆弱性データソースを設定する](configuring-vulnerability-sources.md)と[エアギャップ環境で運用する](running-air-gapped.md)を参照)

解決するには、社内 CA の証明書を JVM のトラストストアにインポートし、変更したトラストストアをコンテナーにマウントします。

## ステップ 1: デフォルトのトラストストアをエクスポートする {#step-1-export-the-default-truststore}

API サーバーのイメージから一時的なコンテナーを実行し、デフォルトのトラストストアをコピーして取り出します。

```shell linenums="1"
docker run --rm \
  --entrypoint cp \
  ghcr.io/dependencytrack/hyades-apiserver:latest \
  /opt/java/openjdk/lib/security/cacerts /tmp/cacerts-modified

docker cp \
  $(docker ps -lq) \
  /tmp/cacerts-modified \
  ./cacerts-modified
```

または、`docker create` を使って 1 つのコマンドで実行します。

```shell linenums="1"
container_id=$(docker create ghcr.io/dependencytrack/hyades-apiserver:latest)
docker cp "$container_id:/opt/java/openjdk/lib/security/cacerts" ./cacerts-modified
docker rm "$container_id"
```

## ステップ 2: 社内 CA の証明書をインポートする {#step-2-import-your-internal-ca-certificate}

`keytool` ユーティリティ(すべての JDK に含まれています)を使って CA 証明書をインポートします。デフォルトのトラストストアのパスワードは `changeit` です。

```shell linenums="1"
keytool -import \
  -trustcacerts \
  -keystore ./cacerts-modified \
  -storepass changeit \
  -noprompt \
  -alias internal-ca \
  -file /path/to/your/internal-ca.crt
```

インポートが成功したことを確認します。

```shell linenums="1"
keytool -list -keystore ./cacerts-modified -storepass changeit | grep internal-ca
```

## ステップ 3: トラストストアをコンテナーにマウントする {#step-3-mount-the-truststore-into-the-container}

Compose ファイルまたは Kubernetes マニフェストに、デフォルトのトラストストアを変更後のものに置き換えるボリュームマウントを追加します。

=== "Docker Compose"

    ```yaml linenums="1"
    services:
      apiserver:
        image: ghcr.io/dependencytrack/hyades-apiserver:latest
        volumes:
          - "./cacerts-modified:/opt/java/openjdk/lib/security/cacerts:ro"
    ```

=== "Kubernetes"

    ```yaml linenums="1"
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: dt-truststore
    binaryData:
      cacerts: <base64-encoded contents of cacerts-modified>
    ---
    # In the Deployment spec:
    volumes:
      - name: truststore
        configMap:
          name: dt-truststore
    containers:
      - name: apiserver
        volumeMounts:
          - name: truststore
            mountPath: /opt/java/openjdk/lib/security/cacerts
            subPath: cacerts
            readOnly: true
    ```

    !!! tip
        サイズが大きい証明書や頻繁にローテーションする証明書の場合は、ConfigMap に埋め込むのではなく、Secret や init コンテナーを使ってトラストストアを書き込むことを検討してください。

## ステップ 4: コンテナーを再起動する {#step-4-restart-the-container}

新しいボリュームマウントを反映するために、コンテナーを再作成します。

```shell
docker compose up -d --force-recreate apiserver
```

次回の起動時から、Dependency-Track は変更したトラストストアを使い、社内 CA が署名したエンドポイントとの TLS 接続を正常に確立します。

## トラブルシューティング {#troubleshooting}

トラストストアをマウントした後も接続が失敗する場合は、次の点を確認してください。

- 正しい CA 証明書をインポートしていること(サーバー証明書そのものではないこと)。
- `cacerts-modified` ファイルが、*現在*のバージョンのコンテナーイメージからエクスポートしたものであること。ベースイメージのデフォルトのトラストストアはリリース間で変わることがあるため、アップグレード後はエクスポートとインポートをやり直してください。
- ボリュームマウントのパスが、コンテナー内の Java ホームと一致していること。確認するには、`docker exec <container> readlink -f $(which java)` を実行し、`lib/security/cacerts` のパスまでたどってください。
