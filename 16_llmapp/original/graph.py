import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from typing import Annotated
from typing_extensions import TypedDict

# 環境変数を読み込む
load_dotenv(".env")
if 'API_KEY' in os.environ:
    os.environ['OPENAI_API_KEY'] = os.environ['API_KEY']

# 使用するモデル名
MODEL_NAME = "gpt-4o-mini"

# MemorySaverインスタンスの作成（会話履歴をスレッド毎に保持）
memory = MemorySaver()

# グラフを保持する変数の初期化
graph = None


# ===== Stateクラスの定義 =====
class State(TypedDict):
    messages: Annotated[list, add_messages]


# ===== システムプロンプト =====
def build_system_prompt(character: str) -> str:
    """指定されたキャラクターになりきるためのシステムプロンプトを生成"""
    return (
        f"あなたはこれから「{character}」になりきってユーザーと会話します。\n"
        f"・一人称、口調、性格、話し方の癖、考え方などをすべて「{character}」に合わせてください。\n"
        f"・「私はAIです」などのメタ発言はせず、常に「{character}」として振る舞ってください。\n"
        f"・「{character}」が実在・架空のどちらでも、そのキャラクターらしい返答をしてください。\n"
        f"・返答は日本語で、自然な会話になるように簡潔にまとめてください。"
    )


# ===== グラフの構築 =====
def build_graph(model_name, memory):
    """シンプルな1ノードのチャットグラフを構築"""
    graph_builder = StateGraph(State)

    llm = ChatOpenAI(model_name=model_name)

    def chatbot(state: State):
        return {"messages": [llm.invoke(state["messages"])]}

    graph_builder.add_node("chatbot", chatbot)
    graph_builder.set_entry_point("chatbot")
    graph_builder.set_finish_point("chatbot")

    return graph_builder.compile(checkpointer=memory)


# ===== 応答を返す関数 =====
def get_bot_response(user_message, character, memory, thread_id):
    """
    ユーザーのメッセージに基づき、ボットの応答を取得します。
    thread_id毎に会話履歴が蓄積されます。キャラクターはシステムメッセージで指定。
    """
    global graph
    if graph is None:
        graph = build_graph(MODEL_NAME, memory)

    # 既存の履歴を確認し、初回のみシステムメッセージを追加
    config = {"configurable": {"thread_id": thread_id}}
    existing = memory.get(config)
    has_history = bool(existing) and bool(
        existing.get('channel_values', {}).get('messages')
    )

    new_messages = []
    if not has_history:
        new_messages.append(SystemMessage(content=build_system_prompt(character)))
    new_messages.append(HumanMessage(content=user_message))

    response = graph.invoke(
        {"messages": new_messages},
        config,
        stream_mode="values"
    )
    return response["messages"][-1].content


# ===== メッセージ一覧を取得する関数 =====
def get_messages_list(memory, thread_id):
    """メモリから会話履歴を取得し、ユーザー/ボットのメッセージに分類"""
    messages = []
    state = memory.get({"configurable": {"thread_id": thread_id}})
    if not state:
        return messages
    memories = state.get('channel_values', {}).get('messages', [])
    for message in memories:
        if isinstance(message, HumanMessage):
            messages.append({
                'class': 'user-message',
                'text': message.content.replace('\n', '<br>')
            })
        elif isinstance(message, AIMessage) and message.content != "":
            messages.append({
                'class': 'bot-message',
                'text': message.content.replace('\n', '<br>')
            })
    return messages
