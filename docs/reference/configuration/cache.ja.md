# キャッシュ

Dependency-Track は、外部サービスへの負荷を減らし、繰り返しの検索を高速化するために、コストの高い処理の結果をキャッシュします。各キャッシュには TTL があり、TTL を過ぎるとエントリーは期限切れになり、キャッシュプロバイダーによって破棄されます。

プロバイダーは [`dt.cache.provider`](properties.md#dtcacheprovider) で選択します。

## プロバイダー {#providers}

### データベース {#database}

`database` プロバイダーは、設定されたデータソース上の `CACHE_ENTRY` テーブルにキャッシュエントリーを保存します。これが唯一の組み込みプロバイダーです。

!!! warning
    このプロバイダーは自身のスキーマを管理しません。設定するデータソースは、`default` データソースと同じスキーマを指している必要があります。`CACHE_ENTRY` テーブルは、そのスキーマに Dependency-Track のスキーマのマイグレーションによって作成されます。

!!! tip
    同じスキーマを対象とする[セカンダリーデータソース](datasources.md)をキャッシュに指定することにも意味があります。キャッシュのトラフィックをメインのコネクションプールから分離できるため、キャッシュの処理が API サーバーとデータベース接続を奪い合わずに済みます。

バックグラウンドのメンテナンスワーカーが、期限切れの行を定期的に削除し、キャッシュのメトリクスの元になるキャッシュごとのサイズのカウンターを更新します。

設定:

- [`dt.cache.provider.database.datasource.name`](properties.md#dtcacheproviderdatabasedatasourcename)
- [`dt.cache.provider.database.maintenance.initial-delay-ms`](properties.md#dtcacheproviderdatabasemaintenanceinitial-delay-ms)
- [`dt.cache.provider.database.maintenance.interval-ms`](properties.md#dtcacheproviderdatabasemaintenanceinterval-ms)

## エントリーの TTL {#entry-ttls}

名前付きの各キャッシュには、`dt.cache."<name>".ttl-ms` という形式の TTL プロパティがあります。

### 脆弱性アナライザーの結果 {#vulnerability-analyzer-results}

リモートの脆弱性アナライザーによる検索結果のキャッシュで、コンポーネントの識別子をキーとします。同じコンポーネントを繰り返し分析する際の、上流サービスへの API 呼び出しを削減します。

設定:

- [`dt.cache."vuln-analyzer.oss-index.results".ttl-ms`](properties.md#dtcachevuln-analyzeross-indexresultsttl-ms)
- [`dt.cache."vuln-analyzer.snyk.results".ttl-ms`](properties.md#dtcachevuln-analyzersnykresultsttl-ms)

### パッケージメタデータリゾルバーのレスポンス {#package-metadata-resolver-responses}

パッケージレジストリのメタデータエンドポイントからの HTTP レスポンスのキャッシュで、古いコンポーネントの検出に使われます。

!!! tip
    エントリーにはレスポンス本文とともに `ETag` と `Last-Modified` のバリデーターが含まれます。そのため、鮮度の期間を過ぎた後の更新では条件付きリクエストによる再検証が行われ、上流のレスポンスが変わっていなければ 304 を受け取ります。条件付きリクエストが行われるようにするには、TTL を鮮度の期間である 12 時間より長くする必要があります。

設定:

- [`dt.cache."package-metadata-resolver.cargo.responses".ttl-ms`](properties.md#dtcachepackage-metadata-resolvercargoresponsesttl-ms)
- [`dt.cache."package-metadata-resolver.composer.responses".ttl-ms`](properties.md#dtcachepackage-metadata-resolvercomposerresponsesttl-ms)
- [`dt.cache."package-metadata-resolver.cpan.responses".ttl-ms`](properties.md#dtcachepackage-metadata-resolvercpanresponsesttl-ms)
- [`dt.cache."package-metadata-resolver.gem.responses".ttl-ms`](properties.md#dtcachepackage-metadata-resolvergemresponsesttl-ms)
- [`dt.cache."package-metadata-resolver.github.responses".ttl-ms`](properties.md#dtcachepackage-metadata-resolvergithubresponsesttl-ms)
- [`dt.cache."package-metadata-resolver.gomodules.responses".ttl-ms`](properties.md#dtcachepackage-metadata-resolvergomodulesresponsesttl-ms)
- [`dt.cache."package-metadata-resolver.hackage.responses".ttl-ms`](properties.md#dtcachepackage-metadata-resolverhackageresponsesttl-ms)
- [`dt.cache."package-metadata-resolver.hex.responses".ttl-ms`](properties.md#dtcachepackage-metadata-resolverhexresponsesttl-ms)
- [`dt.cache."package-metadata-resolver.maven.responses".ttl-ms`](properties.md#dtcachepackage-metadata-resolvermavenresponsesttl-ms)
- [`dt.cache."package-metadata-resolver.nixpkgs.responses".ttl-ms`](properties.md#dtcachepackage-metadata-resolvernixpkgsresponsesttl-ms)
- [`dt.cache."package-metadata-resolver.npm.responses".ttl-ms`](properties.md#dtcachepackage-metadata-resolvernpmresponsesttl-ms)
- [`dt.cache."package-metadata-resolver.nuget.responses".ttl-ms`](properties.md#dtcachepackage-metadata-resolvernugetresponsesttl-ms)
- [`dt.cache."package-metadata-resolver.pypi.responses".ttl-ms`](properties.md#dtcachepackage-metadata-resolverpypiresponsesttl-ms)
