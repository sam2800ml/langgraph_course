from langgraph.graph import MessagesState, StateGraph, START, END
from typing_extensions import TypedDict


class inputState(TypedDict):
    question: str

class outputState(TypedDict):
    answer: str

class overallState(TypedDict):
    question: str
    answer: str
    notes: str

def thinking(state: inputState): # this writes to the overall state, thats why we passed it to the other model
    return {"answer": "bye", "notes":".. his name is santiago"}

def answer_node(state: overallState) -> outputState:
    return {"answer":"Bye santi"}

graph = StateGraph(overallState, input=inputState, output=outputState)

graph.add_node("answer_node", answer_node)
graph.add_node("thinking_node", thinking)

graph.add_edge(START, "thinking_node")
graph.add_edge("thinking_node","answer_node")
graph.add_edge("answer_node",END)

graph = graph.compile()

print(graph.invoke({"question":"hi"}))
