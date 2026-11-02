# コンテナーイメージ

Dependency-Track は、一連のコンテナーイメージとして提供されます。コンポーネントごとに専用のイメージがあります。リリースはまず GitHub Container Registry に公開され、その後 Docker Hub に非同期でミラーされます。

## コンポーネント {#components}

| コンポーネント | 説明 |
|:----------|:------------|
| API サーバー | バックエンドサービス。REST API を公開し、分析を実行します。 |
| フロントエンド | Web UI。静的なシングルページアプリケーションを配信します。 |
| v4 移行ツール | v4 のデータベースを v5 に移行するための単発実行のツール。[v4 から v5 に移行する](../guides/administration/migrating-from-v4.md)を参照してください。 |

Dependency-Track v4 では、API サーバーとフロントエンドを組み合わせた「バンドル」イメージを公開していました。v5 にはこのイメージはありません。運用者は 2 つのコンポーネントを別々のコンテナーとして実行する必要があります。

## レジストリ {#registries}

イメージは 2 つのレジストリでホストされています。

| レジストリ | 役割 |
|:---------|:-----|
| `ghcr.io` | プライマリー。新しいタグが最初に公開されます。 |
| `docker.io` | ミラー。`ghcr.io` から非同期で更新されます。 |

新しく公開されたタグは、`ghcr.io` にはすぐに表示され、`docker.io` にはミラーのジョブが完了した時点で表示されます。リリース直後にタグが Docker Hub に見当たらない場合は、`ghcr.io` から pull するか、ミラーが追いついてから再試行してください。

## イメージの座標 {#image-coordinates}

| コンポーネント | GHCR | Docker Hub |
|:----------|:-----|:-----------|
| API サーバー | `ghcr.io/dependencytrack/apiserver` | `docker.io/dependencytrack/apiserver` |
| フロントエンド | `ghcr.io/dependencytrack/frontend` | `docker.io/dependencytrack/frontend` |
| v4 移行ツール | `ghcr.io/dependencytrack/v4-migrator` | `docker.io/dependencytrack/v4-migrator` |

## タグ {#tags}

| タグのパターン | 例 | 説明                                                        |
|:------------|:--------|:------------------------------------------------------------|
| `X.Y.Z` | `5.0.0` | 安定版リリース。                                            |
| `X.Y.Z-rc.N` | `5.1.0-rc.1` | リリース候補。                                              |
| `X-snapshot` | `5-snapshot` | `main` ブランチの最新ビルド。マージのたびに移動します。     |

デプロイは常に完全な `X.Y.Z` タグ、またはイメージダイジェストに固定してください。これにより、ロールアウトの再現性が保たれ、意図しないアップグレードを防げます。

!!! warning
    `latest` タグは使わないでください。このタグは v4 の最新リリースを指しており、2026 年 12 月に v4 がサポート終了を迎えるまでそのままです。`latest` を pull した v5 のユーザーは v4 のイメージを取得することになります。

## 不変性 {#immutability}

Docker Hub 上のリリースタグ(`X.Y.Z`、`X.Y.Z-rc.N`)は[不変](https://docs.docker.com/docker-hub/repos/manage/hub-images/immutable-tags/)です。一度公開されると、リリースタグが指すダイジェストは変更できません。これにより、`5.0.0` に固定したデプロイは、ミラーの状態やレジストリのキャッシュに関係なく、常に同じイメージに解決されることが保証されます。

スナップショットタグ(`5-snapshot`)は、設計上、可変です。新しいビルドのたびに移動します。
