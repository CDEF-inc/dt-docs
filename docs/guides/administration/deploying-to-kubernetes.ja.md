# Kubernetes にデプロイする

Kubernetes で Dependency-Track を実行するための `dependency-track` Helm チャートは、コミュニティによってメンテナンスされています。インストール方法、values のリファレンス、OpenShift との互換性については、[helm-charts リポジトリ][helm-charts repository]に記載されています。

チャート 2.x は Dependency-Track 5.0.0 以降を対象としています。チャート 1.x は Dependency-Track 4.x を対象としています。

[本番環境にデプロイする][Deploying to production]で説明しているサイジング、データベース、運用に関するガイダンスは、プラットフォームにかかわらず適用されます。

## 既存のリリースをアップグレードする {#upgrading-an-existing-release}

チャート 2.x は、チャート 1.x や `hyades` チャートからそのまま置き換えてアップグレードできるものではありません。どちらの場合も再インストールが必要です。チャートの[アップグレードガイド][upgrade guide]では、データベースのバックアップ、チャート 2.x が想定する Secret、ファイルストレージ、values の変換、切り替えを含む手順全体を説明しています。

!!! warning "`hyades` チャートは使用しないでください"
    独立した `hyades` チャートは、Dependency-Track v5 のプレビュー用のチャートとして提供されていました。メンテナーは `dependency-track` チャートを優先してこのチャートを非推奨にしており、今後の更新はありません。新しいデプロイには使用しないでください。すでに使用している場合は、チャートの[アップグレードガイド][upgrade guide]に従って `dependency-track` チャートに移行してください。

[Deploying to production]: deploying-to-production.md
[helm-charts repository]: https://github.com/DependencyTrack/helm-charts/tree/main/charts/dependency-track
[upgrade guide]: https://github.com/DependencyTrack/helm-charts/blob/main/charts/dependency-track/UPGRADING.md
