# データベース

Dependency-Track の動作には、[PostgreSQL] または PostgreSQL 互換のデータベースが必要です。

サポートされる最も古いバージョンは 14 です。[利用可能な最新バージョン][newest available version]を使うことをお勧めします。

ホスティングソリューションの選び方や、PostgreSQL のデプロイとチューニングについては、[データベースを設定する](../../guides/administration/configuring-database.md)を参照してください。

## 拡張機能 {#extensions}

Dependency-Track では、次の PostgreSQL の[拡張機能](https://www.postgresql.org/docs/current/external-extensions.html)が**必須**です。ホスティングソリューションを選ぶ際は、これらがサポートされていることを確認してください。

* [`pg_trgm`](https://www.postgresql.org/docs/current/pgtrgm.html): *トライグラムマッチングによるテキストの類似度のサポート*

!!! note
    Dependency-Track は、[スキーマのマイグレーション](#schema-migrations)中に必要な `CREATE EXTENSION IF NOT EXISTS` ステートメントを実行します。拡張機能を手動で有効にする必要はありません。

Dependency-Track が使用する拡張機能は、次の条件を満たすものに限られます。

1. PostgreSQL に[標準で同梱されている](https://www.postgresql.org/docs/current/contrib.html)
2. デフォルトで [trusted](https://www.postgresql.org/about/featurematrix/detail/347/) である

## チューニングパラメーター {#tuning-parameters}

Dependency-Track は、本番環境のデプロイに次の PostgreSQL パラメーターを推奨します。これらをいつ、なぜ適用するかについては、[高度なチューニング](../../guides/administration/configuring-database.md#advanced-tuning)を参照してください。

### `autovacuum_vacuum_scale_factor` {#autovacuum_vacuum_scale_factor}

<table>
  <tbody style="border: 0">
    <tr>
      <th style="text-align: right">デフォルト</th>
      <td style="border-width: 0"><code>0.2</code></td>
    </tr>
    <tr>
      <th style="text-align: right">推奨値</th>
      <td style="border-width: 0"><code>0.02</code></td>
    </tr>
    <tr>
      <th style="text-align: right">テーブル</th>
      <td style="border-width: 0">
        <ul>
          <li><code>COMPONENT</code></li>
        </ul>
      </td>
    </tr>
    <tr>
      <th style="text-align: right">参考文献</th>
      <td style="border-width: 0"><a href="https://postgresqlco.nf/doc/en/param/autovacuum_vacuum_scale_factor/">ドキュメント</a></td>
    </tr>
  </tbody>
</table>

### `default_toast_compression` {#default_toast_compression}

<table>
  <tbody style="border: 0">
    <tr>
      <th style="text-align: right">デフォルト</th>
      <td style="border-width: 0"><code>pglz</code></td>
    </tr>
    <tr>
      <th style="text-align: right">推奨値</th>
      <td style="border-width: 0"><code>lz4</code></td>
    </tr>
    <tr>
      <th style="text-align: right">参考文献</th>
      <td style="border-width: 0">
        <ul>
          <li><a href="https://postgresqlco.nf/doc/en/param/default_toast_compression/">ドキュメント</a></li>
          <li><a href="https://www.postgresql.fastware.com/blog/what-is-the-new-lz4-toast-compression-in-postgresql-14">富士通による比較</a></li>
          <li><a href="https://www.tigerdata.com/blog/optimizing-postgresql-performance-compression-pglz-vs-lz4">Tiger Data による比較</a></li>
        </ul>
      </td>
    </tr>
  </tbody>
</table>

### `wal_compression` {#wal_compression}

<table>
  <tbody style="border: 0">
    <tr>
      <th style="text-align: right">デフォルト</th>
      <td style="border-width: 0"><code>off</code></td>
    </tr>
    <tr>
      <th style="text-align: right">推奨値</th>
      <td style="border-width: 0"><code>lz4</code> または <code>zstd</code></td>
    </tr>
    <tr>
      <th style="text-align: right">参考文献</th>
      <td style="border-width: 0">
        <ul>
          <li><a href="https://postgresqlco.nf/doc/en/param/wal_compression/">ドキュメント</a></li>
          <li><a href="https://www.enterprisedb.com/blog/you-can-now-pick-your-favorite-compression-algorithm-your-wals">EnterpriseDB による比較</a></li>
          <li><a href="https://www.percona.com/blog/wal-compression-in-postgresql-and-recent-improvements-in-version-15/">Percona による解説</a></li>
        </ul>
      </td>
    </tr>
  </tbody>
</table>

### `jit` {#jit}

<table>
  <tbody style="border: 0">
    <tr>
      <th style="text-align: right">デフォルト</th>
      <td style="border-width: 0"><code>on</code></td>
    </tr>
    <tr>
      <th style="text-align: right">推奨値</th>
      <td style="border-width: 0"><code>off</code></td>
    </tr>
    <tr>
      <th style="text-align: right">参考文献</th>
      <td style="border-width: 0">
        <ul>
          <li><a href="https://postgresqlco.nf/doc/en/param/jit/">ドキュメント</a></li>
          <li><a href="https://www.postgresql.org/docs/current/jit-decision.html">When to JIT?(PostgreSQL)</a></li>
          <li><a href="https://www.postgresql.org/message-id/E1w8GWU-002bSL-31@gemulon.postgresql.org">PostgreSQL 19 でのデフォルトの変更</a></li>
        </ul>
      </td>
    </tr>
  </tbody>
</table>

## スキーマのマイグレーション {#schema-migrations}

デフォルトでは、スキーマのマイグレーションは起動時に[初期化タスク](init-tasks.md)として [Flyway] を使って実行されます。[アップグレードガイド](../../guides/upgrading/index.md)に明記されていない限り、古いバージョンの Dependency-Track からのアップグレードに手動の作業は必要ありません。

[Flyway]: https://www.red-gate.com/products/flyway/
[PostgreSQL]: https://www.postgresql.org/
[newest available version]: https://www.postgresql.org/support/versioning/
