# アプリケーション

Dependency-Track の設定システムは [MicroProfile Config] に基づいており、複数の[ソース](#sources)をサポートしています。

!!! tip
    サポートされている設定プロパティの一覧は、[設定リファレンス](properties.md)に記載されています。

## ソース {#sources}

設定プロパティは、次のソースから*この順序で*読み込まれます。

1. JVM システムプロパティ
2. 環境変数
3. `${cwd}/.env` ファイル
4. `${cwd}/config/application.properties` ファイル
5. アプリケーションに組み込まれた `application.properties`

!!! tip
    `${cwd}` は現在の作業ディレクトリを指します。公式のコンテナーイメージを実行する場合は `/opt/owasp/dependency-track` です。

値が見つかると、それ以降のソースは確認されません。たとえば、Dependency-Track が設定プロパティ `foo.bar` を検索する際、JVM が `-Dfoo.bar=321` 付きで起動されていれば、環境変数 `FOO_BAR=123` は無視されます。

## 式 {#expressions}

設定値では、`${...}` で示される式を使って、ほかの値を参照できます。

```ini linenums="1"
dt.datasource.foo.url=jdbc:postgresql://localhost:5432/dtrack
dt.datasource.bar.url=${dt.datasource.foo.url}
```

これは、同じ値を重複して定義するのを避けるのに便利です。

## ファイルから値を読み込む {#loading-values-from-files}

`${file::/path/to/file}` 式を使うと、設定値をファイルから読み込めます。これは、Docker や Kubernetes のシークレットなどを使って、シークレットがファイルとしてコンテナーにマウントされている場合に便利です。

```ini linenums="1"
dt.datasource.password=${file::/var/run/secrets/database-password}
dt.ldap.bind-password=${file::/var/run/secrets/ldap-bind-password}
```

ファイルは起動時に 1 回だけ読み込まれ、UTF-8 としてデコードされ、末尾の空白が取り除かれます。64 KiB を超えるファイルは拒否されます。

## 環境変数へのマッピング {#environment-variable-mapping}

プロパティの正規の表現では、英数字をハイフン(`-`)とピリオド(`.`)で区切ります。たとえば次のとおりです。

```ini linenums="1"
foo.BAR-baz=123
```

<!-- vale DependencyTrack.AIBuzzwords = NO -->
環境変数では一般に、英数字とアンダースコア(`_`)しか使えません。
<!-- vale DependencyTrack.AIBuzzwords = YES -->
この差を埋めるため、Dependency-Track は [MicroProfile Config] で[定義されている](https://download.eclipse.org/microprofile/microprofile-config-3.1/microprofile-config-spec-3.1.html#default_configsources.env.mapping)次の照合方法を使います。

> 1. 完全一致(つまり `foo.BAR-baz`)
> 2. 英数字でも `_` でもない各文字を `_` に置き換える(つまり `foo_BAR_baz`)
> 3. 英数字でも `_` でもない各文字を `_` に置き換え、名前を大文字に変換する(つまり `FOO_BAR_BAZ`)

!!! tip
    [設定リファレンス](properties.md)には、記載されている各設定プロパティに対応する正しい環境変数名が含まれています。

## JVM オプション {#jvm-options}

コンテナーイメージは、`JAVA_OPTIONS` 環境変数で設定された次のデフォルト値で API サーバーを起動します。

| フラグ                              | 目的                                                             |
|-----------------------------------|---------------------------------------------------------------------|
| `-XX:+UseG1GC`                    | 停止時間を予測しやすいように調整されたガベージコレクター。                |
| `-XX:+UseStringDeduplication`     | 同一の `String` 値を重複排除し、ヒープの使用量を削減します。  |
| `-XX:+UseCompactObjectHeaders`    | オブジェクトごとのメモリーのオーバーヘッドを削減します。                                 |
| `-XX:MaxGCPauseMillis=250`        | G1GC の目標停止時間(ミリ秒)。                            |
| `-XX:MaxRAMPercentage=80.0`       | JVM のヒープの上限を、コンテナーで利用可能なメモリーの 80% にします。       |

コンテナーのメモリーの残り 20% は、オフヒープメモリー、スレッドスタック、OS に充てられます。

デフォルト値を置き換えずに拡張するには、`EXTRA_JAVA_OPTIONS` 環境変数で追加のフラグを設定します。

```ini
EXTRA_JAVA_OPTIONS="-XX:MaxGCPauseMillis=100"
```

起動時に、コンテナーは `EXTRA_JAVA_OPTIONS` を `JAVA_OPTIONS` の後ろに追加します。同じフラグについては、後のフラグが前の値を上書きします。

## 設定の解決をデバッグする {#debugging-configuration-resolution}

設定値が正しく解決されているか、どのソースから解決されたかを確認するには、[`dt.config.log-values`](properties.md#dtconfiglog-values) と、`DEBUG` に設定した [`dt.logging.level."io.smallrye.config"`](properties.md) でデバッグログを有効にします。

!!! warning
    シークレットはマスクも省略も*されません*。**本番環境では使用しないでください。**

[MicroProfile Config]: https://microprofile.io/specifications/config/
