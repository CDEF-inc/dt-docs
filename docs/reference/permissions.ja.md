# 権限

アクセス制御モデルのしくみ(ユーザー、チーム、ACL)の背景については、[アクセス制御について](../concepts/access-control.md)を参照してください。

## 権限 {#permissions_1}

Dependency-Track は 2 段階の権限モデルを使います。粗い粒度の権限(たとえば `PORTFOLIO_MANAGEMENT`)は、ある機能へのフルアクセスを付与します。きめ細かい権限(たとえば `PORTFOLIO_MANAGEMENT_CREATE`)を使うと、アクセスを特定の操作に制限できます。粗い粒度の権限は、そのきめ細かいバリアントをすべて含みます。

### ポートフォリオ {#portfolio}

手順については、[プロジェクトを階層に整理する](../guides/user/organizing-projects.md)と[プロジェクトのバージョンを管理する](../guides/user/managing-project-versions.md)を参照してください。

| 権限                        | 説明                                                            |
|:----------------------------------|:-----------------------------------------------------------------------|
| `BOM_UPLOAD`                      | CycloneDX のソフトウェア部品表をアップロードします。                          |
| `PROJECT_CREATION_UPLOAD`         | BOM のアップロード時に、プロジェクトが存在しなければ自動作成します。              |
| `VIEW_PORTFOLIO`                  | プロジェクト、コンポーネント、ライセンス、依存関係グラフ、メトリクスを読み取ります。|
| `PORTFOLIO_ACCESS_CONTROL_BYPASS` | ポートフォリオのアクセス制御をバイパスし、すべてのプロジェクトへのアクセスを付与します。      |
| `PORTFOLIO_MANAGEMENT`            | プロジェクトとポートフォリオのデータを作成、更新、削除します。                |
| `PORTFOLIO_MANAGEMENT_CREATE`     | プロジェクトとポートフォリオのデータを作成します。                                    |
| `PORTFOLIO_MANAGEMENT_READ`       | ポートフォリオのデータを読み取ります。                                                   |
| `PORTFOLIO_MANAGEMENT_UPDATE`     | プロジェクトとポートフォリオのデータを更新します。                                    |
| `PORTFOLIO_MANAGEMENT_DELETE`     | プロジェクトとポートフォリオのデータを削除します。                                    |

### 脆弱性分析 {#vulnerability-analysis}

| 権限                        | 説明                                                                      |
|:----------------------------------|:---------------------------------------------------------------------------------|
| `VIEW_VULNERABILITY`              | プロジェクトに影響する脆弱性を表示します。                                       |
| `VULNERABILITY_ANALYSIS`          | 脆弱性の分析の判断を行い、VEX データを管理します。                   |
| `VULNERABILITY_ANALYSIS_CREATE`   | プロジェクトに VEX ドキュメントをアップロードします。                                               |
| `VULNERABILITY_ANALYSIS_READ`     | プロジェクトの VEX ドキュメントを読み取ります。                                                |
| `VULNERABILITY_ANALYSIS_UPDATE`   | 脆弱性の分析の判断を行い、VEX ドキュメントをアップロードします。              |

### 脆弱性の管理 {#vulnerability-management}

| 権限                          | 説明                                             |
|:------------------------------------|:--------------------------------------------------------|
| `VULNERABILITY_MANAGEMENT`          | 内部の脆弱性を完全に管理します。  |
| `VULNERABILITY_MANAGEMENT_CREATE`   | 内部の脆弱性を作成します。              |
| `VULNERABILITY_MANAGEMENT_READ`     | 内部の脆弱性を読み取ります。                |
| `VULNERABILITY_MANAGEMENT_UPDATE`   | 内部の脆弱性とタグを更新します。     |
| `VULNERABILITY_MANAGEMENT_DELETE`   | 内部の脆弱性を削除します。              |

### ポリシーの管理 {#policy-management}

| 権限                    | 説明                                                      |
|:------------------------------|:-----------------------------------------------------------------|
| `POLICY_MANAGEMENT`           | ポリシー、サービス、ライセンスグループを作成、更新、削除します。|
| `POLICY_MANAGEMENT_CREATE`    | ポリシーを作成します。                                                  |
| `POLICY_MANAGEMENT_READ`      | ポリシーを読み取ります。                                                    |
| `POLICY_MANAGEMENT_UPDATE`    | ポリシーを更新します。                                                  |
| `POLICY_MANAGEMENT_DELETE`    | ポリシーを削除します。                                                  |
| `POLICY_VIOLATION_ANALYSIS`   | ポリシー違反の分析の判断を行います。                     |
| `VIEW_POLICY_VIOLATION`       | ポートフォリオ全体のポリシー違反を表示します。                      |

### アクセスの管理 {#access-management}

| 権限                    | 説明                                                         |
|:------------------------------|:--------------------------------------------------------------------|
| `ACCESS_MANAGEMENT`           | ユーザー、サービスアカウント、チーム、権限、API キー、ワークロード ID を管理します。 |
| `ACCESS_MANAGEMENT_CREATE`    | ユーザー、サービスアカウント、チーム、API キー、ワークロード ID プロバイダー、バインディングを作成します。 |
| `ACCESS_MANAGEMENT_READ`      | ユーザー、サービスアカウント、チーム、API キー、ワークロード ID プロバイダー、バインディングを読み取ります。 |
| `ACCESS_MANAGEMENT_UPDATE`    | ユーザー、サービスアカウント、チーム、API キー、ワークロード ID プロバイダーを更新します。 |
| `ACCESS_MANAGEMENT_DELETE`    | ユーザー、サービスアカウント、チーム、API キー、ワークロード ID プロバイダー、バインディングを削除します。 |

### システム設定 {#system-configuration}

| 権限                       | 説明                                                                          |
|:---------------------------------|:-------------------------------------------------------------------------------------|
| `SYSTEM_CONFIGURATION`           | システム設定(通知、パッケージリポジトリ、メール設定)へのフルアクセスです。   |
| `SYSTEM_CONFIGURATION_CREATE`    | システム設定のエントリーを作成します。                                                 |
| `SYSTEM_CONFIGURATION_READ`      | システム設定を読み取ります。                                                           |
| `SYSTEM_CONFIGURATION_UPDATE`    | システム設定を更新します。                                                         |
| `SYSTEM_CONFIGURATION_DELETE`    | システム設定のエントリーを削除します。                                                 |

### シークレットの管理 {#secret-management}

| 権限                    | 説明                       |
|:------------------------------|:----------------------------------|
| `SECRET_MANAGEMENT`           | シークレットの管理へのフルアクセスです。    |
| `SECRET_MANAGEMENT_CREATE`    | シークレットを作成します。                   |
| `SECRET_MANAGEMENT_UPDATE`    | シークレットを更新します。                   |
| `SECRET_MANAGEMENT_DELETE`    | シークレットを削除します。                   |

### タグ {#tags}

| 権限            | 説明                              |
|:----------------------|:-----------------------------------------|
| `TAG_MANAGEMENT`      | タグを更新、削除します。                  |
| `TAG_MANAGEMENT_DELETE`| タグを削除します。                            |

## デフォルトのチーム {#default-teams}

Dependency-Track は、初回起動時に次のデフォルトのチームを作成します。

| チーム            | 目的                                                                                                                     |
|:----------------|:----------------------------------------------------------------------------------------------------------------------------|
| Administrators  | フルアクセスです。初期設定と継続的な管理に使います。メンバーはすべての権限を受け取ります。                             |
| Portfolio Managers | 管理者のアクセス権を必要とせずに、プロジェクトとポートフォリオを管理するユーザーを想定しています。                              |
| Automation      | CI/CD パイプラインと自動化ツールを想定しています。通常は `BOM_UPLOAD` と `PROJECT_CREATION_UPLOAD` を持ちます。              |
