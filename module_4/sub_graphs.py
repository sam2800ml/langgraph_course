#Subgraphs -> allows you ti create and manage different states in different parts of your graph
#overlapping keys the parent must have the same states as the childs to be able to communicate between them


from operator import add
from typing import List, TypedDict, Optional, Annotated, Dict
from langgraph.graph import StateGraph, START, END


class Log(TypedDict):
    id: str
    question: str
    docs: Optional[list]
    answer: str
    grade = Optional[int]
    grader: Optional[str]
    feedback: Optional[str]

class FaillureAnalysisState(TypedDict):
    cleaned_logs: List[Log]
    failures: List[Log]
    fa_summary: str
    processed_logs: List[str]

class failureAnalysisOutputState(TypedDict):
    fa_summary: str
    processed_logs: List[str]

def get_failures(state):
    """get logs that contain a failure"""
    cleaned_logs = state["cleaned_logs"]
    failures = [log for log in cleaned_logs if "grade" in log ]
    return {"failures": failures}

def generate_summary(state):
    """Generate summary of failures"""
    failures = state["failures"]
    fa_summary = "Poor quality retrieval of chroma documentation"
    return {"fa_summary": fa_summary, "processed_logs":[f"failure-analysis-on-log-{failure['id']}" for failure in failures]}

fa_builder = StateGraph(input=FaillureAnalysisState, output=failureAnalysisOutputState)
fa_builder.add_node("get_failures", get_failures)
fa_builder.add_node("generate_summary", generate_summary)
fa_builder.add_edge(START, "get_failures")
fa_builder.add_edge("get_failures", "generate_summary")
fa_builder.add_edge("generate_summary", END)

graph = fa_builder.compile()

class QuestionSummarizationState(TypedDict):
    cleaned_logs: List[Log]
    qa_summary: str
    report: str
    processed_logs: List[str]

class QuestionSummarizationOutputState(TypedDict):
    report: str
    processed_logs: List[str]

def generate_summary(state):
    cleaned_logs = state["cleaned_logs"]
    summary = "Questions focused on usage of chatOllama and Chroma vector store"
    return {"qa_summary": summary, "processed_los":[f"summary-on-log-{log["id"]}" for log in cleaned_logs]}

def send_to_slack(state):
    qa_summary = state["qa_summary"]
    report = "foo bar baz"
    return {"report": report}

qs_builder = StateGraph(input=QuestionSummarizationState, output=QuestionSummarizationOutputState)
qs_builder.add_node("generate_summary", generate_summary)
qs_builder.add_node("send_to_slack", send_to_slack)
qs_builder.add_edge(START, "generate_summary")
qs_builder.add_edge("generate_summary", "send_to_slack")
qs_builder.add_edge("send_to_slack", END)

graph = qs_builder.compile()

class EntryGraphState(TypedDict):
    raw_logs: List[Log]
    cleaned_logs: List[Log] # this is going to be used in both sungraphs
    fa_summary: str # only in the fa graph
    report: str # this is only in the qs graph
    processed_logs: Annotated[List[Log],add] # both subgraph

def clean_logs(state):
    raw_logs = state["raw_logs"]
    cleaned_logs = raw_logs
    return {"cleaned_logs": cleaned_logs}


entry_builder = StateGraph(EntryGraphState)
entry_builder.add_node("clean_logs", clean_logs)
entry_builder.add_node("question_summarization", qs_builder.compile())
entry_builder.add_node("failure_analysis", fa_builder.compile())

entry_builder.add_edge(START, "clean_logs")
entry_builder.add_edge("clean_logs", "question_summarization")
entry_builder.add_edge("clean_logs", "failure_analysis")
entry_builder.add_edge("question_summarization", END)
entry_builder.add_edge("failure_analysis", END)

graph = entry_builder.compile()

question_answer = Log(
    id="1",
    question="How can i import chatOllama",
    answer="To import ChatOllama, use: 'import Chatollama'",
)
question_answer_feedback = Log(
    id="2",
    question="How can i import chroma",
    answer="just import chroma with langchain",
    grade=0,
    grader="Document Relevance Recall",
    feedback="the retrieve documents disccus vector stores in general, not just chroma"
)

raw_logs = [question_answer,question_answer_feedback]
print(graph.invoke({"raw_logs": raw_logs}))