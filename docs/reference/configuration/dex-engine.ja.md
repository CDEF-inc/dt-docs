# 永続実行エンジン

[永続実行エンジン](../../concepts/architecture/design/durable-execution.md)(dex)は、バックグラウンドタスクのスケジューリングと実行を担います。このページでは、ワーカーの種類、タスクキュー、デフォルトの設定について説明します。

チューニングの指針については、[スケーリング](../../guides/administration/scaling.md#increase-background-throughput)を参照してください。

## ワーカー {#workers}

ワーカーはタスクキューをポーリングしてタスクを実行します。各ワーカーには、インスタンスごとに同時に処理するタスク数を制限する最大同時実行数を設定できます。

ワーカーの同時実行数は次の形式で設定します。

```ini
dt.dex-engine.<worker-type>.<worker-name>.max-concurrency=<N>
```

`<worker-type>` は `workflow-worker` または `activity-worker` のどちらかです。

| ワーカーの種類    | ワーカー名                     | キュー                          | デフォルトの同時実行数 |
|-------------------|--------------------------------|---------------------------------|--------------------:|
| `workflow-worker` | `default`                      | `default`                       |                 100 |
| `activity-worker` | `default`                      | `default`                       |                  25 |
| `activity-worker` | `vuln-analysis`                | `vuln-analyses`                 |                  10 |
| `activity-worker` | `artifact-import`              | `artifact-imports`              |                   5 |
| `activity-worker` | `package-metadata-resolution`  | `package-metadata-resolutions`  |                   3 |
| `activity-worker` | `notification`                 | `notifications`                 |                   5 |
| `activity-worker` | `vuln-analysis-reconciliation` | `vuln-analysis-reconciliations` |                   5 |
| `activity-worker` | `policy-evaluation`            | `policy-evaluations`            |                   5 |
| `activity-worker` | `metrics-update`               | `metrics-updates`               |                   5 |

## タスクキュー {#task-queues}

タスクキューの容量は、クラスター全体で保留できるタスク数を制限します。キューが容量に達すると、スケジューラーはそのキューへの新しいタスクの作成を止め、バックプレッシャーをかけます。

キューの負荷は、関連する 3 つの用語で表します。

- **容量**は、キューの保留中タスク数の上限で、クラスター全体で適用されます。
- **深さ**は、現在キューで保留中のタスク数で、0 から容量までの値をとります。スケジューラーはサイクルごとに最大 `capacity - depth` 個の新しいタスクを作成するため、深さが容量を超えることはありません。
- **バックログ**はアクティビティキューにのみ当てはまります。ワークフローの実行はスケジューラーとは独立してアクティビティタスクを直接作成するため、[アクティビティタスクスケジューラー](../../concepts/architecture/design/durable-execution.md#activity-task-scheduler)がキューに移すよりも速く、`CREATED` 状態のタスクがたまることがあります。バックログとは、スケジュール可能な状態にありながら、キューの容量によってまだ受け入れられていないタスクの集合です。ワークフローキューにはバックログはありません。スケジューラー自身がタスクを作成し、容量を超えることがないためです。

`dt_dex_engine_activity_task_queue_backlog` メトリクスは、スケーリングの判断に使うバックログを報告します。[ワーカーを水平スケールする](../../guides/administration/scaling.md#scale-workers-horizontally)を参照してください。

キューの容量は、管理パネルの *Workflows* > *Task Queues*、または REST API から実行時に変更できます。

| 種類       | キュー                          | デフォルトの容量 |
|------------|---------------------------------|-----------------:|
| `workflow` | `default`                       |             1000 |
| `activity` | `default`                       |             1000 |
| `activity` | `artifact-imports`              |               25 |
| `activity` | `metrics-updates`               |               25 |
| `activity` | `notifications`                 |               25 |
| `activity` | `package-metadata-resolutions`  |               25 |
| `activity` | `policy-evaluations`            |               25 |
| `activity` | `vuln-analyses`                 |               25 |
| `activity` | `vuln-analysis-reconciliations` |               25 |
