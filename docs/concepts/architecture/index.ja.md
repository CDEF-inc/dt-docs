# アーキテクチャ

このセクションでは、Dependency-Track v5 の内部アーキテクチャについて、主要なサブシステム、その設計の根拠、トレードオフを説明します。

## トポロジー {#topology}

- [デプロイのトポロジー](deployment.md): Dependency-Track クラスターの構成要素、ネットワークポート、協調動作のモデル、インスタンス障害からの復旧について説明します。

## 設計ドキュメント {#design-documents}

- [永続実行](design/durable-execution.md): バックグラウンド処理を高い信頼性とスケーラビリティで実行する、組み込みのワークフローエンジンです。
- [脆弱性分析](design/vulnerability-analysis.md): 永続的なワークフローによって、コンポーネントを脆弱性データベースと照合するしくみです。
- [通知](design/notifications.md): イベントを発行し、ルーティングし、外部システムに配信するしくみです。
- [パッケージメタデータの解決](design/package-metadata-resolution.md): 上流のレジストリからパッケージメタデータを、制御された形でレート制限を考慮しながら取得するしくみです。
