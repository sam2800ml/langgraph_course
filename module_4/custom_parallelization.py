import operator
from typing import Annotated, Any
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END


"""
We can make a custom function to be able to do either go for a route and complete it and then do the next one

"""
def sorting_reducer(left, right):
    """ combines and sorts the values in a list"""
    if not isinstance(left, list):
        left = [left]
    
    if not isinstance(right, list):
        right= [right]

    return sorted(left + right, reverse=False)

class State(TypedDict):
    state: Annotated[list, sorting_reducer] # add updates to the list



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
builder.add_edge(["B2", "c"], "d")
builder.add_edge("d", END)

graph = builder.compile()

print(graph.invoke({"state": []}))