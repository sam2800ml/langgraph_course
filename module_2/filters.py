from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage
from langchain_ollama import ChatOllama
from langgraph.graph import MessagesState, START, StateGraph, END
from langchain_core.messages import RemoveMessage, trim_messages

model = ChatOllama(model="granite3-dense:8b")


messages = [AIMessage(f"Hi", name="bob")]
messages.append(HumanMessage(f"hi", name="pedrito"))
messages.append(AIMessage(f"Yes, im a researcher of ipads", name="pedrito"))
messages.append(HumanMessage(f"wow ipads? whats that", name="pedrito"))
messages.append(HumanMessage(f"i dont know you tell me", name="pedrito"))

def chat_model(state: MessagesState):
    return {"messages": model.invoke(state["messages"])}

def filter_messages(state: MessagesState):
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"messages": delete_messages}

def chat_model_trim(state: MessagesState):
    messages = trim_messages(
        state["messages"],
        max_tokens=10,
        strategy="last",
        token_counter=ChatOllama(model="granite3-dense:8b"),
        allow_partial = True
    )

    return {"messages": model.invoke(messages)}

builder = StateGraph(MessagesState)
builder.add_node("chat_model", chat_model_trim)
#builder.add_node("filter_node", filter_messages)
builder.add_edge(START,"chat_model")
#builder.add_edge("filter_node","chat_model")
builder.add_edge("chat_model", END)
graph = builder.compile()

output = graph.invoke({'messages':messages})
for m in output['messages']:
    m.pretty_print()
