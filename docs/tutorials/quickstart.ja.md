# クイックスタート

このチュートリアルでは、Docker Compose を使って Dependency-Track をローカルで起動し、初めてフロントエンドにログインします。

## 必要なもの {#what-we-need}

- [Docker](https://docs.docker.com/get-docker/) または [Podman](https://podman.io/)
- [Compose v2](https://docs.docker.com/compose/install/)

## Dependency-Track を起動する {#starting-dependency-track}

Compose ファイルをダウンロードし、スタックを起動します。

=== ":fontawesome-brands-linux: Linux / :fontawesome-brands-apple: macOS"

    ```shell
    curl -O https://raw.githubusercontent.com/DependencyTrack/docs/main/docs/tutorials/docker-compose.quickstart.yml
    docker compose -f docker-compose.quickstart.yml up
    ```

=== ":fontawesome-brands-windows: Windows (PowerShell)"

    ```powershell
    Invoke-WebRequest -Uri "https://raw.githubusercontent.com/DependencyTrack/docs/main/docs/tutorials/docker-compose.quickstart.yml" -OutFile "docker-compose.quickstart.yml"
    docker compose -f docker-compose.quickstart.yml up
    ```

必要なイメージが取得され、データベースが初期化され、すべてのサービスが起動します。

??? note "Compose ファイルの内容"
    ```yaml
    --8<-- "docs/tutorials/docker-compose.quickstart.yml"
    ```

## ログインする {#logging-in}

スタックが起動したら、フロントエンド **<http://localhost:8081>** を開き、デフォルトの認証情報でログインします。

| ユーザー名 | パスワード |
|------------|------------|
| `admin`    | `admin`    |

!!! note
    初回ログイン時に、Dependency-Track からパスワードの変更を求められます。

## 次のステップ {#whats-next}

- [コンポーネントポリシーを作成する](creating-a-component-policy.md): 組織の基準に違反するコンポーネントを検出します
- [通知を設定する](setting-up-notifications.md): イベントを Slack、メール、Webhook に送信します
- [本番環境にデプロイする](../guides/administration/deploying-to-production.md): このクイックスタートから実際のデプロイに移行します
