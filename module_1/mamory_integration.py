from langgraph.graph import START, END, StateGraph, MessagesState
from langchain_ollama import ChatOllama
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool

@tool
def multiply(a: int, b:int) -> int:
    """ Multiply a and b.

    Args:
        a: first int
        b: second int
    
    """
    return a * b

@tool
def add(a:int, b:int) -> int:
    """ add a and b

    Args:
        a: first int
        b: second int
    """
    return a + b

@tool
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

def assistant(state: MessagesState):
    response = model.invoke([sys_mg] + state["messages"])
    return {"messages": [response]}

builder = StateGraph(MessagesState)

builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges(
    "assistant",
    # If the latest message (result) from assistant is a tool call →> tools condition routes to tools
    # # If the latest message (result) from assistant is a not a tool call →> tools_condition routes to END
    tools_condition,
)

builder.add_edge("tools", "assistant")

memory = MemorySaver()
react_graph = builder.compile(checkpointer=memory)

config = {"configurable":{"thread_id":"1"}}

mensages = [HumanMessage(content="use the tool to add 3 and 4")]
mensages = react_graph.invoke({"messages":mensages},config)
for m in mensages['messages']:
    m.pretty_print()

mensages = [HumanMessage(content="use the tool then multiply by 7")]
mensages = react_graph.invoke({"messages":mensages},config)
for m in mensages['messages']:
    m.pretty_print()