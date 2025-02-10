import operator
from datetime import datetime
from typing import Annotated, Any

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field

from src.passive_goal_creator.main import Goal, PassiveGoalCreator
from src.prompt_optimizer.main import OptimizedGoal, PromptOptimizer
from src.response_optimizer.main import ResponseOptimizer


class DecomposedTasks(BaseModel):
    values: list[str] = Field(default_factory=list, min_items=3, max_items=5, description="3~5個に分解されたタスク")


class SinglePathPlanGenerationState(BaseModel):
    query: str = Field(..., description="ユーザーが入力したクエリ")
    optimized_goal: str = Field(default="", description="最適化された目標")
    optimized_response: str = Field(default="", description="最適化されたレスポンス定義")
    tasks: list[str] = Field(default_factory=list, description="実行するタスクのリスト")
    current_task_index: int = Field(default=0, description="現在実行中のタスクの番号")
    results: Annotated[list[str], operator.add] = Field(default_factory=list, description="実行済みタスクの結果リスト")
    final_output: str = Field(default="", description="最終的な出力結果")


class QueryDecomposer:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.current_date = datetime.now().strftime("%Y-%m-%d")

    def run(self, query: str) -> DecomposedTasks:
        prompt = ChatPromptTemplate.from_template(
            f"CURRENT_DATE: {self.current_date}\n"
            "-----\n"
            "タスク: 与えられた目標を具体的で実行可能なタスクに分解してください。\n"
            "要件:\n"
            "1. 以下の行動だけで目標を達成すること。決して指定された以外の行動をとらないこと。\n"
            "   - インターネットを利用して、目標を達成するための調査を行う。\n"
            "2. 各タスクは具体的かつ詳細に記載されており、単独で実行ならびに検証可能な情報を含めること。一切抽象的な表現を含まないこと。\n"  # noqa: E501
            "3. タスクは実行可能な順序でリスト化すること。\n"
            "4. タスクは日本語で出力すること。\n"
            "目標: {query}"
        )
        chain = prompt | self.llm.with_structured_output(DecomposedTasks)
        return chain.invoke({"query": query})


class TaskExecutor:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.tools = [TavilySearchResults(max_results=4)]

    def run(self, task: str) -> str:
        agent = create_react_agent(self.llm, self.tools)
        result = agent.invoke(
            {
                "messages": [
                    (
                        "human",
                        (
                            "次のタスクを実行し、詳細な回答を提供してください。\n\n"
                            f"タスク: {task}\n\n"
                            "要件:\n"
                            "1. 必要に応じて提供されたツールを使用してください。\n"
                            "2. 実行は徹底的かつ包括的に行ってください。\n"
                            "3. 可能な限り具体的な事実やデータを提供してください。\n"
                            "4. 発見した内容を明確に要約してください。\n"
                        ),
                    )
                ]
            }
        )
        return result["messages"][-1].content


class ResultAggregator:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm

    def run(self, query: str, response_definition: str, results: list[str]) -> str:
        prompt = ChatPromptTemplate.from_template(
            "与えられた目標:\n{query}\n\n"
            "調査結果:\n{results}\n\n"
            "与えられた目標に対し、調査結果を用いて、以下の指示に基づいてレスポンスを生成してください。\n"
            "{response_definition}"
        )
        results_str = "\n\n".join(f"Info {i+1}:\n{result}" for i, result in enumerate(results))
        chain = prompt | self.llm | StrOutputParser()
        return chain.invoke(
            {
                "query": query,
                "results": results_str,
                "response_definition": response_definition,
            }
        )


class SinglePathPlanGeneration:
    def __init__(self, llm: ChatOpenAI):
        self.passive_goal_creator = PassiveGoalCreator(llm=llm)
        self.prompt_optimizer = PromptOptimizer(llm=llm)
        self.response_optimizer = ResponseOptimizer(llm=llm)
        self.query_decomposer = QueryDecomposer(llm=llm)
        self.task_executor = TaskExecutor(llm=llm)
        self.result_aggregator = ResultAggregator(llm=llm)
        self.graph = self._create_graph()

    @property
    def plot_graph(self) -> str:
        graph_str = self.graph.get_graph().draw_mermaid()
        print("\nグラフ構造:")
        print("```mermaid")
        print(graph_str)
        print("```")
        return graph_str

    def _create_graph(self) -> StateGraph:
        graph = StateGraph(SinglePathPlanGenerationState)
        graph.add_node("goal_setting", self._goal_setting)
        graph.add_node("decompose_query", self._decompose_query)
        graph.add_node("execute_task", self._execute_task)
        graph.add_node("aggregate_results", self._aggregate_results)

        graph.set_entry_point("goal_setting")
        graph.add_edge("goal_setting", "decompose_query")
        graph.add_edge("decompose_query", "execute_task")
        graph.add_conditional_edges(
            "execute_task",
            lambda state: state.current_task_index < len(state.tasks),
            {True: "execute_task", False: "aggregate_results"},
        )
        graph.add_edge("aggregate_results", END)
        return graph.compile()

    def _goal_setting(self, state: SinglePathPlanGenerationState) -> dict[str, Any]:
        # プロンプト最適化
        goal: Goal = self.passive_goal_creator.run(query=state.query)
        optimized_goal: OptimizedGoal = self.prompt_optimizer.run(query=goal.text)
        # レスポンス最適化
        optimized_response: str = self.response_optimizer.run(query=optimized_goal.text)

        return {
            "optimized_goal": optimized_goal.text,
            "optimized_response": optimized_response,
        }

    def _decompose_query(self, state: SinglePathPlanGenerationState) -> dict[str, Any]:
        decomposed_tasks: DecomposedTasks = self.query_decomposer.run(query=state.optimized_goal)
        return {"tasks": decomposed_tasks.values}

    def _execute_task(self, state: SinglePathPlanGenerationState) -> dict[str, Any]:
        current_task = state.tasks[state.current_task_index]
        result = self.task_executor.run(task=current_task)
        return {
            "results": [result],
            "current_task_index": state.current_task_index + 1,
        }

    def _aggregate_results(self, state: SinglePathPlanGenerationState) -> dict[str, Any]:
        final_output = self.result_aggregator.run(
            query=state.optimized_goal,
            response_definition=state.optimized_response,
            results=state.results,
        )
        return {"final_output": final_output}

    def run(self, query: str) -> str:
        initial_state = SinglePathPlanGenerationState(query=query)
        # recursion_limitは実行グラフの再帰的な実行の制限を設定するパラメータ
        # execute_taskノードが複数回実行される可能性があるため、
        # DecomposedTasksのmax_length(5)より大きい値を設定
        final_state = self.graph.invoke(initial_state, {"recursion_limit": 10})
        return final_state.get("final_output", "Failed to generate a final response.")


# 実行例
# uv run python -m src.single_path_plan_generation.main --query "カレーの作り方を教えて"
def main():
    import argparse

    from src.settings import Settings

    settings = Settings()

    parser = argparse.ArgumentParser(description="SinglePathPlanGenerationを実行します。")
    parser.add_argument("--query", type=str, required=True, help="実行するクエリ")
    args = parser.parse_args()

    llm = ChatOpenAI(model=settings.openai_mini_model, temperature=settings.temperature)

    single_path_plan_generation = SinglePathPlanGeneration(llm=llm)
    final_output = single_path_plan_generation.run(query=args.query)

    print(f"{final_output}")


if __name__ == "__main__":
    main()
