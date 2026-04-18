# CommandSetup 外部仕様書

## 概要

設定ファイルと空の保存領域を初期化するコマンドクラス。  
初回利用時に `config.yaml`・`gists.yaml`・`snapshots.yaml` を出力して利用可能な状態にする。

**モジュール:** `ghrepo.command_setup`  
**基底クラス:** `yklibpy.command.command.Command`

---

## コンストラクタ

```python
def __init__(self, appstore: AppStore) -> None
```

### 引数

| 引数 | 型 | 説明 |
|---|---|---|
| `appstore` | `AppStore` | 設定・DB ファイルアクセスオブジェクト |

---

## メソッド

### `run`

```python
def run(self, key: str, default_json_fields: list[str]) -> None
```

設定値と空の DB を出力して初回利用状態を整える。

#### 引数

| 引数 | 型 | 説明 |
|---|---|---|
| `key` | `str` | コンフィグファイル内の JSON フィールドリストのキー名 |
| `default_json_fields` | `list[str]` | `gh repo list --json` に渡すデフォルトフィールドリスト |

#### 動作手順

1. `CommandGhUser().run()` で現在の GitHub ユーザー名を取得する。
2. 取得できない場合は `CommandGhUser.DEFAULT_VALUE_USER` を使用する。
3. 以下の内容でコンフィグファイルを出力する。

   ```yaml
   <key>: <default_json_fields>
   USER: <appstore.user>
   ```

4. `gists.yaml` を空辞書 `{}` で出力する。
5. `snapshots.yaml` を空辞書 `{}` で出力する。

#### 戻り値

なし（`None`）

---

## 利用箇所

`Ghrepo.setup()` クラスメソッド内でインスタンス化・呼び出しされる。

```python
command = CommandSetup(appstore)
command.run(AppConfigx.key, AppConfigx.default_json_fields)
```
