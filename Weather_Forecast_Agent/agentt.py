import os
os.environ["OPENAI_API_KEY"] = "local"

import requests
from crewai import LLM
from crewai import Agent, Task, Crew, Process, LLM



# -------- LLM --------

llm = LLM(
    model="ollama/llama3.2",
    base_url="http://localhost:11434"
)


# -------- TOOL FUNCTION --------

NEWS_KEY = "pub_d1fe43fae14445758642b03a745be803"


def get_news():

    url = f"https://newsdata.io/api/1/news?apikey={NEWS_KEY}&country=in"

    r = requests.get(url).json()

    if "results" not in r:
        return "No news"

    titles = []

    for a in r["results"][:5]:
        titles.append(a["title"])

    return "\n".join(titles)


# -------- AGENTS --------

news_agent = Agent(
    role="News Finder",
    goal="Find latest news",
    backstory="You find news",
    llm=llm,
    verbose=True,
)

writer_agent = Agent(
    role="Writer",
    goal="Summarize news",
    backstory="You summarize",
    llm=llm,
    verbose=True,
)


# -------- TASKS --------

task1 = Task(
    description=f"Get latest news for sports and return them:\n{get_news()}",
    expected_output="News list",
    agent=news_agent,
)

task2 = Task(
    description="Summarize the news in 5 points in Hindi for sports not in other language",
    expected_output="Summary",
    agent=writer_agent,
)


# -------- CREW --------

crew = Crew(
    agents=[news_agent, writer_agent],
    tasks=[task1, task2],
    process=Process.sequential,
    verbose=True,
)


# -------- RUN --------

print(crew.kickoff())