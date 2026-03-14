クラスCommandListを、以下の要望を満たすように変更した、クラス定義と(必要であれば)クラスとは独立した関数の外部仕様書(_private/sub_command-spec.md)を作成して。

# 用語の定義
- ユーザ
gh auth login　で認証されたGitHubのアカウント
指定されGitHubアカウントのアカウント名と同一のユーザ名を持つ
- ユーザディレクトリ
ディレクトリ名はユーザ名
以下の位置に存在する
　AppData\Local\ghrepo\ユーザ名

この下にfetchファイル、repolistディレクトリが存在する
fetchディレクトリは複数個存在することができる。

- fetchファイル
gh repo list を実行した回数を記録するYAML形式ファイル
gh repo list の実行が成功した後に更新される。

フォーマットは、以下の通り
　回数: 実行時のタイムスタンプ

- repolistディレクトリ
ディレクトリ名はgh repo listを実行した回数
gh repo listの出力を格納するdb.yamlをもつ。

