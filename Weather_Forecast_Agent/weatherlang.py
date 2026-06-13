# ======================================================
# SINGLE FILE: COMPLETE AGENTIC WEATHER AI
# (OLLAMA + CREWAI + WEATHER API)
# ======================================================

import os
import requests
from crewai import Agent, Task, Crew
from ollama import chat

# ------------------------------------------------------
# 1. LLM FUNCTION (Ollama direct)
# ------------------------------------------------------
def llm_call(prompt):
    response = chat(
        model="llama3.2",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["message"]["content"]


# ------------------------------------------------------
# 2. WEATHER TOOL (API)
# ------------------------------------------------------
def get_weather(city="Ghaziabad"):
    api_key = "32159fdae35c48c861f0aff3472a240c"

    if not api_key:
        raise ValueError("❌ Set WEATHER_API_KEY")

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    data = requests.get(url).json()

    if "main" not in data:
        raise ValueError(f"❌ API Error: {data}")

    return data["main"]["temp"], data["main"]["humidity"]


# ------------------------------------------------------
# 3. AGENTS (PROMPT-DRIVEN)
# ------------------------------------------------------

def data_agent_task(temp, humidity):
    prompt = f"""
    You are a weather data analyst.

    Temperature: {temp}
    Humidity: {humidity}

    Summarize the current weather.
    """
    return llm_call(prompt)


def prediction_agent_task(temp, humidity):
    prompt = f"""
    You are a weather predictor.

    Temperature: {temp}
    Humidity: {humidity}

    Classify:
    - Heatwave (>40°C)
    - Coldwave (<10°C)
    - Normal

    Explain reasoning.
    """
    return llm_call(prompt)


def alert_agent_task(temp):
    prompt = f"""
    Based on temperature {temp}:

    Generate alert:
    - Heatwave alert
    - Coldwave alert
    - Normal

    Give advice.
    """
    return llm_call(prompt)


# ------------------------------------------------------
# 4. MAIN AGENT SYSTEM
# ------------------------------------------------------
def run_agent(city="Ghaziabad"):
    print("\n🚀 Running Agentic Weather AI...\n")

    # Step 1: Fetch Data
    temp, humidity = get_weather(city)

    print(f"🌦 Temperature: {temp}°C")
    print(f"💧 Humidity: {humidity}%\n")

    # Step 2: Agent Tasks
    print("📊 Data Agent...")
    data_result = data_agent_task(temp, humidity)

    print("🧠 Prediction Agent...")
    prediction_result = prediction_agent_task(temp, humidity)

    print("⚠️ Alert Agent...")
    alert_result = alert_agent_task(temp)

    # Step 3: Final Output
    print("\n🎯 FINAL OUTPUT\n--------------------")
    print("📊 Data Analysis:\n", data_result)
    print("\n🧠 Prediction:\n", prediction_result)
    print("\n⚠️ Alert:\n", alert_result)


# ------------------------------------------------------
# 5. RUN
# ------------------------------------------------------
if __name__ == "__main__":
    run_agent()