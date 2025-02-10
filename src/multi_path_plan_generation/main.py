import operator
from datetime import datetime
from typing import Annotated, Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from src.passive_goal_creator.main import Goal, PassiveGoalCreator
from src.prompt_optimizer.main import OptimizedGoal, PromptOptimizer
from src.response_optimizer.main import ResponseOptimizer


class TaskOption(BaseModel):
    description: str = Field(default="", description="タスクオプションの説明")


class Task(BaseModel):
    task_name: str = Field(..., description="タスクの名前")
    task_options: list[TaskOption] = Field(
        default_factory=list, min_items=2, max_items=3, description="2~3個のタスクオプション"
    )


class DecomposedTasks(BaseModel):
    values: list[Task] = Field(default_factory=list, min_items=3, max_items=5, description="3~5個に分解されたタスク")


class MultiPathPlanGeneration(BaseModel):
    query: str = Field(..., description="ユーザーが入力したクエリ")
    optimized_goal: str = Field(default="", description="最適化された目標")
    optimized_response: str = Field(default="", description="最適化されたレスポンス")
    tasks: DecomposedTasks = Field(default_factory=DecomposedTasks, description="複数のオプションを持つタスクのリスト")
    current_task_index: int = Field(default=0, description="現在のタスクのインデックス")
    chosen_options: Annotated[list[int], operator.add] = Field(
        default_factory=list, description="各タスクで選択されたオプションのインデックス"
    )
    results: Annotated[list[str], operator.add] = Field(default_factory=list, description="実行されたタスクの結果")
    final_output: str = Field(default="", description="最終出力")


class QueryDecomposer:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.current_date = datetime.now().strftime("%Y-%m-%d")

    def run(self, query: str) -> DecomposedTasks:
        prompt = ChatPromptTemplate.from_template(
            f"CURRENT_DATE: {self.current_date}\n"
            "-----\n"
            "タスク: 与えられた目標を3〜5個の高レベルタスクに分解し、各タスクに2〜3個の具体的なオプションを提供してください。\n"
            "要件:\n"
            "1. 以下の行動だけで目標を達成すること。決して指定された以外の行動をとらないこと。\n"
            "   - インターネットを利用して、目標を達成するための調査を行う。\n"
            "2. 各高レベルタスクは具体的かつ詳細に記載されており、単独で実行ならびに検証可能な情報を含めること。一切抽象的な表現を含まないこと。\n"
            "3. 各項レベルタスクに2〜3個の異なるアプローチまたはオプションを提供すること。\n"
            "4. タスクは実行可能な順序でリスト化すること。\n"
            "5. タスクは日本語で出力すること。\n\n"
            "REMEMBER: 実行できないタスク、ならびに選択肢は絶対に作成しないでください。\n\n"
            "目標: {query}"
        )
        chain = prompt | self.llm.with_structured_output(DecomposedTasks)
        return chain.invoke({"query": query})


class OptionPresenter:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm.configurable_fields(max_tokens=ConfigurableField(id="max_tokens"))
        
    def run(self, task: Task) -> int:
        


def main():
    pass


if __name__ == "__main__":
    main()
