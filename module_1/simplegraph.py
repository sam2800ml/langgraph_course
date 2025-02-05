from typing import TypedDict, Literal
import random
from langgraph.graph import StateGraph, START, END
import graphviz

class State(TypedDict):
    graph_state: str

def node1(state):
    print("Node1")
    return {"graph_state":state['graph_state'] + " I am"}
def node2(state):
    print("Node 2")
    return {"graph_state":state['graph_state'] + " Happy"}
def node3(state):
    print("Node 3")
    return {"graph_state":state['graph_state'] + " Sad"}

def decide_mood(state) -> Literal["node2", "node3"]:
    user_input = state['graph_state']

    if random.random() < 0.5:
        return "node2"
    return "node3"

builder = StateGraph(State)
builder.add_node("node1", node1)
builder.add_node("node2", node2)
builder.add_node("node3", node3)

builder.add_edge(START, "node1")
builder.add_conditional_edges("node1", decide_mood)
builder.add_edge("node2",END)
builder.add_edge("node3",END)

graph = builder.compile()

print(graph.invoke({'graph_state':'hi this is santiago'})) # run the graphs synchronously