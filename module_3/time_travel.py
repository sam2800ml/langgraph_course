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

graph = builder.compile(checkpointer=memory)

intial_input = {"messages": "multiply 2 by 3"}

thread = {"configurable": {"thread_id":2}}
for event in graph.stream(intial_input, thread, stream_mode="values"):
    event["messages"][-1].pretty_print()

print(graph.get_state({'configurable':{"thread_id":2}})) 
"""
Statesnashot is the current state at our graph, the current message, metadata, next node to go 
checkpoint id, just service checkpoints 

but if we use get_state_history we can see al the history, the first elemnt is the current state
graph.get_state we get the current state
"""

all_states = [s for s in graph.get_state_history(thread)]
len(all_states)

for i in range(len(all_states)):
    print(f"-----------state {i}------------")
    print(all_states[i])


# Forking

to_fork = all_states[-2]
to_fork.values["messages"]

print(to_fork.config)

fork_config = graph.update_state(
    to_fork.config,
    {"messages": [HumanMessage(content="multiply 5 and 3", id=to_fork.values["messages"][0].id)]}
)