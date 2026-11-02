# コンポーネントの完全性検証について

Dependency-Track は、BOM が各コンポーネントについて宣言しているハッシュを、そのコンポーネントの上流のパッケージリポジトリが公開しているハッシュと比較します。両者が食い違う場合は、ビルドに含まれるアーティファクトがレジストリの配布するアーティファクトと異なることを示しており、タイポスクワッティング、レジストリ側での改ざん、よく似たパッケージへの偶発的な置き換えを検出できます。

## 検証のしくみ {#how-verification-works}

上流のハッシュは BOM には含まれません。[パッケージメタデータの解決](architecture/design/package-metadata-resolution.md)のしくみが、スケジュールされたバックグラウンドのワークフローでパッケージリポジトリからハッシュを取得し、その結果を解決済みのアーティファクトとともに永続化します。

コンポーネントについて両方の値がそろうと、Dependency-Track はアルゴリズムごとにそれらを比較します。比較では大文字と小文字を区別しません。共通するいずれかのアルゴリズムで一致すれば、そのコンポーネントは検証済みとなります。共通するいずれかのアルゴリズムで差異があれば、失敗となります。

検証の対象は 4 つのハッシュアルゴリズム(`MD5`、`SHA-1`、`SHA-256`、`SHA-512`)です。BOM には、SHA-384、SHA3、BLAKE2b、BLAKE3 など、他のアルゴリズムのハッシュを含めることができます。Dependency-Track はそれらの値をコンポーネントに保持して API で公開しますが、サポート対象のパッケージリポジトリが対応する値を公開していないため、検証には使用しません。

## サポート対象のエコシステム {#supported-ecosystems}

検証が実行されるのは、上流のリポジトリがハッシュを公開しており、かつそのエコシステムにハッシュを読み取るリゾルバーがあるコンポーネントだけです。

| エコシステム | 上流から取得できるハッシュ |
|:----------|:-------------------------------|
| Maven     | SHA-1 |
| npm       | SHA-1, SHA-512 |
| PyPI      | MD5, SHA-256 |

PyPI のコンポーネントでは、リゾルバーがリリースの中から正しいファイルを選べるように、PURL に `file_name` 修飾子が含まれている必要があります。PyPI はリリースごとに 1 つのソース配布物と多数の wheel を公開しており、それぞれに独自のハッシュがあります。修飾子は、どれと比較すべきかを Dependency-Track に伝えます。`file_name` 修飾子のない PyPI のコンポーネントは、リポジトリのハッシュがないものとして表示されます。

Cargo、Go モジュール、Composer、Hex、CPAN、Nixpkgs など、Dependency-Track がパッケージメタデータを解決するその他のエコシステムは、現時点ではアーティファクトのハッシュを返しません。これらのエコシステムのコンポーネントが不一致としてフラグ付けされることはありません。UI では、リポジトリのハッシュがないものとして表示されます。

検証は、リゾルバーの実行時に各リポジトリが Dependency-Track から到達可能で、レート制限を受けていないことにも依存します。到達できないリポジトリや HTTP 429 を返すリポジトリからは、次に解決が成功するまで、該当するコンポーネントのハッシュは得られません。

## 非同期の解決 {#asynchronous-resolution}

Dependency-Track は、上流のハッシュを非同期に解決します。BOM をアップロードすると解決がスケジュールされますが、ワークフローは公開レジストリのレート制限の範囲内に収まるように、コンポーネントを制御されたバッチで処理します。このしくみについては、[パッケージメタデータの解決](architecture/design/package-metadata-resolution.md)のページで詳しく説明しています。

その結果、次の 2 つのことが起こります。

- インポートされたばかりのコンポーネントには、リゾルバーの処理が追いつくまでリポジトリのハッシュが表示されません。待ち時間は、小規模なポートフォリオでは数分、大規模なポートフォリオではそれ以上になることがあります。
- 上流のリポジトリに到達できない間、またはリポジトリが Dependency-Track をレート制限している間は、そこから取得したコンポーネントに完全性の状態が表示されません。通常であれば Failed と表示される不一致も、次に更新が成功するまでは見えません。

検証の状態は、アップロード時点の BOM の状態ではなく、直近に成功した解決の結果を反映します。

## 検証結果の表示場所 {#where-verification-surfaces}

完全性の状態は、**Integrity** という列として次の 2 か所に表示されます。

- プロジェクトの **Components** タブ。
- **Component Search** ビュー。

どちらのビューでも、この列はデフォルトで非表示です。テーブルの列の表示切り替えから有効にしてください。

![コンポーネント検索ビューの Integrity 列](../assets/images/concepts/component-integrity-verification/component-search.png)

各行には、次の 5 つの状態のいずれかが表示されます。

<!-- vale Google.Units = NO -->

| 状態 | アイコン | 意味 |
|:------|:-----|:--------|
| Passed | :fontawesome-solid-circle-check:{ style="color: #4dbd74" } | 共通するアルゴリズムの少なくとも 1 つが一致し、差異のあるものはありません。 |
| Failed | :fontawesome-solid-circle-xmark:{ style="color: #f86c6b" } | 共通するアルゴリズムの少なくとも 1 つに差異があります。 |
| Unknown | :fontawesome-solid-circle-question:{ style="color: #ffc107" } | 両方がハッシュを宣言していますが、共通するアルゴリズムがありません。 |
| No component hash | :fontawesome-solid-circle-minus:{ style="color: #9e9e9e" } | BOM がこのコンポーネントのハッシュを宣言していません。 |
| No repository hash | :fontawesome-regular-circle-question:{ style="color: #9e9e9e" } | 上流のハッシュがまだ取得できていないか、エコシステムがサポートされていません。 |

<!-- vale Google.Units = YES -->

この表のアイコンは、UI での表示を近似したものです。正確な見た目についてはスクリーンショットを参照してください。

![プロジェクトのコンポーネントビューの Integrity 列](../assets/images/concepts/component-integrity-verification/project-components.png)

Passed と Failed のアイコンはクリックできます。選択するとモーダルが開き、アルゴリズムごとに、コンポーネントで宣言された値とリポジトリの値が並べて表示され、どのアルゴリズムが一致したかが示されます。モーダルには、上流のハッシュを提供したリポジトリの名前も表示されます。

![ハッシュ検証の失敗を示すモーダル](../assets/images/concepts/component-integrity-verification/failed-hash-verification.png)

## ポリシーで検証を使用する {#using-verification-in-policies}

コンポーネントポリシーでは、`component.has_package_artifact_hash_mismatch()` という条件式を使って、ハッシュが一致しないコンポーネントにフラグを付けることができます。この関数は、UI の表の Failed の状態に一致します。その意味と、ポリシーの実例については、[Condition expressions](../reference/policies/condition-expressions.md#has_package_artifact_hash_mismatch) を参照してください。

Failed は、完全性チェックが返しうる状態の 1 つにすぎません。この関数は不一致が確認された場合にのみ発火するため、この関数に基づくポリシーは、まだリポジトリのハッシュがないコンポーネントや、ハッシュのアルゴリズムが上流のリポジトリと共通しないコンポーネントにはフラグを付けません。ポリシーでそれらのケースにも対応する必要がある場合は、他の条件と組み合わせてください。

## まだ対応していないこと {#what-is-not-yet-covered}

完全性検証には、次の制限があります。

- 状態は[時系列メトリクス](./time-series-metrics.md)には出力されません。
- **Project Components** ビューと **Component Search** ビューでは、完全性を並べ替えやフィルターのパラメーターとして使用できません。
- 検証はリゾルバーの対応範囲と上流のリポジトリへの到達可能性に依存するため、リポジトリのハッシュがないコンポーネントが検証済みであるとは限りません。
