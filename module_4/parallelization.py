import operator
from typing import Annotated, Any
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END


"""
When we want to do parallelization, we need to make sure to use a reducer, because if we dont add it, this will add at the same time and will give us an error
the use of the reducer is to be able to add them in a sequence
"""
class State(TypedDict):
    state: Annotated[list, operator.add] # add updates to the list

class ReturnNodeValue:
    def __init__(self, node_secret: str):
        self.value = node_secret

    def __call__(self, state: State) -> Any:
        print(f"adding {self.value} to {state['state']}")
        return {"state": [self.value]}

builder = StateGraph(State)

builder.add_node("A", ReturnNodeValue("im a"))
builder.add_node("B", ReturnNodeValue("im b"))
builder.add_node("B2", ReturnNodeValue("im b2"))
builder.add_node("c", ReturnNodeValue("im c"))
builder.add_node("d", ReturnNodeValue("im d"))

builder.add_edge(START, "A")
builder.add_edge("A", "B")
builder.add_edge("A", "c")
builder.add_edge("B", "B2")
builder.add_edge("B2", "d")
builder.add_edge("c", "d")
builder.add_edge("d", END)

graph = builder.compile()

print(graph.invoke({"state": []}))