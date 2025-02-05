from pprint import pprint
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_groq import ChatGroq


def multiply(a: int, b:int) -> int:
    """ Multiply a and b.

    Args:
        a: first int
        b: second int
    
    """
    return a * b


def add(a:int, b:int) -> int:
    """ add a and b

    Args:
        a: first int
        b: second int
    """
    return a + b


def divide(a:int, b:int) -> float:
    """ divide a and b

    Args:
        a: first int
        b: second int
    """
    return a / b


tools = [add, multiply, divide]

model = ChatOllama(model="granite3-dense:8b").bind_tools(tools)

sys_mg = SystemMessage(content="Youre a helpful assistant tasked with performing arithmetic on a set of inputs")

class messagesState(MessagesState):
    pass

def assistant(state: messagesState):
    response = model.invoke([sys_mg] + state["messages"])
    return {"messages": [response]}

builder = StateGraph(messagesState)

builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call →> tools condition routes to tools
    # # If the latest message (result) from assistant is a not a tool call →> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools","assistant")
graph =  builder.compile()

mensages = [HumanMessage(content="Hello")]
mensages = graph.invoke({"messages":mensages})
for m in mensages['messages']:
    m.pretty_print()

mensages = [HumanMessage(content="add 3 and 4, then multiply by 4, and finally divide by 5")]
mensages = graph.invoke({"messages":mensages})
for m in mensages['messages']:
    m.pretty_print()
