from typing_extensions import TypedDict
from langgraph.graph import START, END, StateGraph

class State(TypedDict):
    foo: int

def node1(state):
    print("node1")
    return {"foo":state['foo'] + 1}

builder = StateGraph(State)

builder.add_node("node1", node1)
builder.add_edge(START, "node1")
builder.add_edge("node1", END)

graph = builder.compile()

print(graph.invoke({"foo":1}))