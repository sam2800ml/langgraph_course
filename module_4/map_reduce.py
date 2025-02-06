"""
Map reduce is an operation essential for efficient task decomposition and parallel processing
- Map = Breaks a task into smaller sub task, processing each sub task in parallel
- Reduce = Aggregate the result across all of the completed sub task
example:
Map create a set of jokes about a topic
Reduce picks the best joke from the list

"""

from langchain_ollama import ChatOllama
import operator
from typing import Annotated, TypedDict
from pydantic import BaseModel
from langgraph.constants import Send
from langgraph.graph import StateGraph, START, END
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

os.environ["GROQ_API_KEY"] = ""
print()
subject_prompt = """Generate a comma separated list of between 2 and 5 examples related to: {topic}"""
joke_prompt = """Generate a joke about {subject}"""
best_joke_prompt = """Below are a bunch of jokes about {topic}, select the best one! return the ID of the best one, starting 0 as the ID"""

#model = ChatOllama(model="granite3-dense:8b")

model = ChatGroq(temperature=0, model_name="mixtral-8x7b-32768")

class Subjects(BaseModel):
    subjects: list[str]


class bestJoke(BaseModel):
    id: int

class overallState(BaseModel):
    topic: str
    subjects: list = []
    jokes: Annotated[list, operator.add] = []
    best_selected_joke: str = ""

def generate_topic(state: overallState):
    prompt = subject_prompt.format(topic=state.topic)
    response = model.with_structured_output(Subjects).invoke(prompt)
    print(response)
    return {'subjects':response.subjects }

def continue_to_jokes(state: overallState):
    return {"next": [("generate_joke", {"subject": s}) for s in state.subjects]}


class JokeState(TypedDict):
    subject:str

class Joke(BaseModel):
    joke:str

def generate_joke(state: JokeState):
    prompt = joke_prompt.format(subject=state.subject)
    response = model.with_structured_output(Joke).invoke(prompt)
    return {"jokes": [response.joke]}

def best_joke(state: overallState):
    jokes = "\n\n".join(state['jokes'])
    prompt = best_joke_prompt.format(topic= state.topic, jokes=jokes)
    response = model.with_structured_output(bestJoke).invoke(prompt)
    return {'best_selected_joke': state['jokes'][response.id]}

graph = StateGraph(overallState)
graph.add_node("generate_topic", generate_topic)
graph.add_node("generate_joke", generate_joke)
graph.add_node("best_joke", best_joke)
graph.add_edge(START, "generate_topic")
graph.add_conditional_edges("generate_topic",continue_to_jokes, ["generate_joke"])
graph.add_edge("generate_joke", "best_joke")
graph.add_edge("best_joke", END)
app = graph.compile()

for s in app.stream({"topic":"animal"}):
    print(s)