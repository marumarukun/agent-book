#!/bin/bash
# 実行前にchmod +x setup.sh

# uvのインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# PATHを更新（新しいシェルセッションを開始せずにuvを使用できるようにする）
export PATH="$HOME/.local/bin:$PATH"

# uv syncの実行
uv sync

echo "uvのインストールと同期が完了しました"
