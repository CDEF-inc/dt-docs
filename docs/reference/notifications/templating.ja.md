# テンプレート

パブリッシャーは [Pebble](https://pebbletemplates.io/) テンプレートを使って、通知を送信先の形式にレンダリングします。組み込みの各パブリッシャーにはデフォルトのテンプレートが付属しています。管理者は、ここで説明する変数とフィルターを使ったカスタムテンプレートで置き換えることができます。

## テンプレートのコンテキスト {#template-context}

次の変数は、すべてのテンプレートで利用できます。

| 変数                    | 型                                                                                                           | 説明                                                                                                                                       |
|:------------------------|:-------------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------------------------------------------------|
| `baseUrl`               | string                                                                                                       | オペレーターが設定した Dependency-Track フロントエンドのベース URL。設定されていない場合は空文字列。                                         |
| `timestampEpochSeconds` | long                                                                                                         | Unix エポックからの秒数で表した通知のタイムスタンプ。                                                                          |
| `timestamp`             | string                                                                                                       | [ISO 8601] のローカル日時(`uuuu-MM-dd'T'HH:mm:ss.SSSSSSSSS`)形式で表した通知のタイムスタンプ。                                     |
| `notification`          | [`Notification`](schema.md#notification) メッセージ                                         | 通知全体。フィールドは `level`、`scope`、`group`、`title`、`content`、`timestamp`、`subject` です。                              |
| `subject`               | メッセージ                                                                                                   | 通知の型付きサブジェクト。サブジェクトを送出するグループの場合にのみ存在します。具体的なメッセージ型は通知の `group` によって異なります。 |
| `subjectJson`           | string                                                                                                       | `subject` の JSON 表現。通知に `subject` がある場合にのみ存在します。                                                      |

`subject` の構造は通知グループによって異なります。各グループが送出するメッセージ型については、[通知スキーマのリファレンス](schema.md)を参照してください。

!!! note
    変数名は `timestampEpochSeconds`(複数形)です。Dependency-Track v4 から引き継いだテンプレートは `timestampEpochSecond`(単数形)を参照しているため、更新が必要です。

## カスタムフィルター {#custom-filters}

[Pebble の組み込みフィルター][built-in Pebble filters]に加えて、Dependency-Track は通知専用のフィルターを 2 つ登録しています。

### `formatTimestamp` {#formattimestamp}

`google.protobuf.Timestamp` の値(`notification.timestamp` など)を ISO 8601 のローカル日時の文字列に整形します。

```pebble
{{ notification.timestamp | formatTimestamp }}
```

### `summarize` {#summarize}

`Project` または `Component` の値から、人間が読める短い識別子を生成します。

プロジェクトの場合、結果は `name` で、必要に応じてその後に `` ` : ` `` と `version` が続きます。コンポーネントの場合、`purl` が設定されていれば結果は `purl` です。設定されていなければ `name` で、必要に応じてその前に `` `group : ` `` が付き、その後に `` ` : ` `` と `version` が続きます。それ以外の型の入力は、その文字列表現が返されます。

```pebble
{{ notification.subject.component | summarize }}
```

## テンプレートの制限 {#template-restrictions}

セキュリティ上の理由から、次の Pebble の機能は通知テンプレートでは利用**できません**。

- `include` タグ。テンプレートはファイルシステムからほかのファイルを読み込めません。
- ファイルシステムからの読み込みや任意のコードの実行を行うタグや関数。

デフォルトの出力エスケープ方式は `json` です。これは、Webhook やチャットプラットフォームのように JSON のボディを使う送信先に適しています。ほかの形式(プレーンテキストのメールなど)を出力するテンプレートでは、該当する Pebble の構文を使ってエスケープ方式を上書きしてください。

[ISO 8601]: https://en.wikipedia.org/wiki/ISO_8601
[built-in Pebble filters]: https://pebbletemplates.io/wiki/guide/basic-usage/#filters
