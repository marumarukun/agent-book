import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーションの設定を管理するクラス。

    このクラスは以下の設定を管理します：
    1. 外部APIの認証情報（OPENAI_API_KEY, ANTHROPIC_API_KEY等）
    2. LangChainの設定
    3. アプリケーション固有の設定（モデル選択、パラメータ等）

    .envファイルから設定を読み込み、必要に応じて環境変数として設定します。
    """

    model_config = SettingsConfigDict(
        env_file=".env",  # 設定ファイルのパス
        env_file_encoding="utf-8",  # 設定ファイルのエンコーディング
        extra="allow",
    )

    # 外部APIの認証情報（環境変数として設定）
    OPENAI_API_KEY: str  # OpenAI APIキー（必須）
    ANTHROPIC_API_KEY: str = ""  # Anthropic APIキー（オプション）
    TAVILY_API_KEY: str  # Tavily APIキー（必須）

    # LangChain関連の設定
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "agent-book"

    # アプリケーション固有の設定
    openai_smart_model: str = "gpt-4o"  # メインのGPTモデル
    openai_mini_model: str = "gpt-4o-mini"  # 軽量なGPTモデル
    openai_embedding_model: str = "text-embedding-3-small"  # エンベッディングモデル
    anthropic_smart_model: str = "claude-3-5-sonnet-20240620"  # Anthropicのモデル
    temperature: float = 0.0  # 生成時の温度パラメータ
    default_reflection_db_path: str = "tmp/reflection_db.json"  # リフレクションDBのパス

    def __init__(self, **values):
        """設定を初期化し、環境変数を設定"""
        super().__init__(**values)
        self._set_env_variables()

    def _set_env_variables(self):
        """大文字のフィールドを環境変数として設定

        このメソッドは以下の処理を行います：
        1. クラスの型アノテーションから全てのフィールドを取得
        2. 大文字のフィールド（例：OPENAI_API_KEY）のみを環境変数として設定
        3. 外部ライブラリが環境変数から設定を読み取れるようにする
        """
        for key in self.__annotations__.keys():
            if key.isupper():  # 大文字のフィールドのみを処理（例：OPENAI_API_KEY）
                os.environ[key] = getattr(self, key)  # フィールドの値を環境変数として設定
