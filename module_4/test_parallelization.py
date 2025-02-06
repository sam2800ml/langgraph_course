from langgraph.graph import StateGraph, MessagesState, START, END
from typing import TypedDict
from typing_extensions import Annotated
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from langchain_community.document_loaders import WikipediaLoader
from langchain_community.tools import TavilySearchResults
from langchain_ollama import ChatOllama
import operator
import os

Tavily_API_KEY = "api-key"
os.environ["TAVILY_API_KEY"] = Tavily_API_KEY

class State(TypedDict):
    question: str
    answer: str
    context: Annotated[list, operator.add]

model = ChatOllama(model="granite3-dense:8b")

def search_web(state):
    """Retrieve docs from web search"""
    tavily_search = TavilySearchResults(max_results=3)
    search_docs = tavily_search.invoke(state['question'])

    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
            for doc in search_docs
        ]
    )
    return {"context": [formatted_search_docs]}

def search_wikipedia(state):
    """Retrieve docs from wikipedia"""
    search_docs = WikipediaLoader(query=state["question"], load_max_docs=1).load()

    formatted_search_docs = "\n\n---\n\n".join(
        [
            f'<Document source="{doc.metadata["source"]}" page="{doc.metadata.get("page", "")}"/>\n{doc.page_content}\n</Document>'
            for doc in search_docs
        ]
    )
    return {"context": [formatted_search_docs]}

def generate_answer(state):
    """Node to answer a question"""
    context = state["context"]
    question = state["question"]
    answer_template = """Answer the question {question} using the following context: {context}"""
    answer_instructions = answer_template.format(question=question, context=context)

    answer = model.invoke([SystemMessage(content=answer_instructions)] + [HumanMessage(content=question)])

    return {"answer": answer}

builder = StateGraph(State)

builder.add_node("search_web", search_web)
builder.add_node("search_wikipedia", search_wikipedia)
builder.add_node("generate_answer", generate_answer)

builder.add_edge(START, "search_web")
builder.add_edge(START, "search_wikipedia")
builder.add_edge("search_web", "generate_answer")
builder.add_edge("search_wikipedia", "generate_answer")
builder.add_edge("generate_answer", END)

graph = builder.compile()

result = graph.invoke({"question": "whats a gpu"})
print(result)
print(result['answer'].content)