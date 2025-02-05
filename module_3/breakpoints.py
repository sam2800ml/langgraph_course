from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
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

sys_msg = SystemMessage(content="Youre a helpful assitant tasked with performing arithmetic on a set of inputs")

def assistant(state: MessagesState):
    return {"messages": [model.invoke([sys_msg] + state["messages"])]}

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

graph = builder.compile(interrupt_before=["tools"], checkpointer=memory)

intial_input = {"messages": "multiply 2 by 3 and add 20 using the tools"}

thread = {"configurable": {"thread_id":2}}
for event in graph.stream(intial_input, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()

user_approval = input("Do you want to call the tool? (yes/no): ")
if user_approval.lower() == "yes":
    for event in graph.stream(None, thread, stream_mode="values"): # this work by placing the none, because it will track the previous work
        event['messages'][-1].pretty_print()
else:
    print("operation canceled by the user")


#state = graph.get_state(thread)
#print(state.next)