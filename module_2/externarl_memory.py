from langchain_ollama import ChatOllama
from langgraph.graph import START, END, StateGraph, MessagesState
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3


db_path = 'module_2/example.db'
conn = sqlite3.connect(db_path, check_same_thread=False)
memory = SqliteSaver(conn)

model = ChatOllama(model="granite3-dense:8b")
class State(MessagesState):
    summary: str


def call_model(state: State):
    #get the summary if exist
    summary = state.get("summary", "")
    if summary:
        system_message = f"summary of conversation earlier {summary} "
        messages = {[SystemMessage(content=system_message)], + state["messages"]}
    else:
        messages = state["messages"]
    
    response = model.invoke(messages)
    return {"messages": response}

def summarize_conversation(state:State):
    summary = state.get("summary","")

    if summary:
        summary_message = (
            f"This is a summary of the conversation to date: {summary}"
        )
    else:
        summary_message = "create a summary of this conversation"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    response = model.invoke(messages)

    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"]]
    return {"summary": response.content, "messages":delete_messages}

def should_continue(state: State):
    """ Return the next node to execute"""

    messages = state["messages"]

    if len(messages) > 6:
        return "summarize_conversation"
    
    return END

graph = StateGraph(State)

graph.add_node("conversation", call_model)
graph.add_node(summarize_conversation)

graph.add_edge(START, "conversation")
graph.add_conditional_edges("conversation", should_continue)
graph.add_edge("summarize_conversation", END)



grah_chat = graph.compile(checkpointer=memory)

config = {"configurable": {"thread_id":1}}

input_message = HumanMessage(content="hi my name is santiago")
output = grah_chat.invoke({"messages":[input_message]}, config)
for m in output['messages'][-1:]:
    m.pretty_print()

input_message = HumanMessage(content="whats my name")
output = grah_chat.invoke({"messages":[input_message]}, config)
for m in output['messages'][-1:]:
    m.pretty_print()

input_message = HumanMessage(content="i like to eat")
output = grah_chat.invoke({"messages":[input_message]}, config)
for m in output['messages'][-1:]:
    m.pretty_print()

input_message = HumanMessage(content="i like soccer")
output = grah_chat.invoke({"messages":[input_message]}, config)
for m in output['messages'][-1:]:
    m.pretty_print()

print(grah_chat.get_state(config).values.get("summary",""))