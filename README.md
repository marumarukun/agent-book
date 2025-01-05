# marumarukun's template

<center>

<!-- ![image.png](docs/logo.png) -->

</center>

<div align="center">
    <img alt="python versions" src="https://img.shields.io/badge/python-3.12-blue?color=5271FF">
    <a href="https://opensource.org/licenses/MIT">
        <img alt="MIT License" src="https://img.shields.io/badge/license-MIT-green?color=5271FF">
    </a>
    <a href="https://github.com/astral-sh/uv">
        <img alt="uv" src="https://img.shields.io/badge/package%20manager-uv-blue?color=5271FF">
    </a>
    <a href="https://github.com/astral-sh/ruff">
        <img alt="ruff" src="https://img.shields.io/badge/code%20style-ruff-000000.svg?color=5271FF">
    </a>
    <a href="https://github.com/python/mypy">
        <img alt="mypy" src="https://img.shields.io/badge/typing-mypy-blue?color=5271FF">
    </a>
</div>
<br />


## Description

機械学習プロジェクトを進める際に使用するテンプレートリポジトリ
以下の機能を含んでいます：

- Dockerを使用した環境の分離と管理
- uvを使用したPythonパッケージの管理
- Ruffを使用したコードスタイルのチェック
- Mypyを使用した型チェック
- pytestを使用したテストフレームワーク

## Used libraries

- python3.12
- VSCode(Cursor)
- Docker
- uv
- ruff
- mypy
- pytest
## How to use

### Dockerを使用しない場合

#### 1. uvのインストール
uvがインストールされていない場合は、以下のコマンドでインストールしてください：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 2. 依存関係のインストール
プロジェクトのルートディレクトリで以下のコマンドを実行し、必要なパッケージをインストールします：
```bash
uv sync
```

### Dockerを使用する場合

#### dockerコンテナ ビルド & 起動

mac環境用

```bash
docker compose up -d --build mac
```

GPU環境用

```bash
docker compose up -d --build gpu
```

### コンテナにアタッチ

次にVScode左下の`><`ボタンより`コンテナで再度開く`でコンテナにアクセス

### 拡張機能インストール

無事コンテナが開いたら, 「拡張機能の推奨事項があります」という通知が出ると思います.
この通知を許可すると, `.vscode/extensions.json`に記載されている拡張機能が自動的にインストールされます.
もし通知が出なかった場合は, 左のメニューから`拡張機能`を選択し, `フィルターアイコン`->`推奨`‐>`インストールアイコン`を押せば一括インストールできます.

