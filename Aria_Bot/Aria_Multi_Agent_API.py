import streamlit as st
import pandas as pd
from datetime import datetime
import time
import os
import re
import json
import requests

# CrewAI Core Orchestration Components
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

# --- 1. ENVIRONMENT INITIALIZATION ---
os.environ["OPENAI_API_KEY"] = "NA"  # Bypasses internal legacy validation checks in CrewAI

# --- 2. LOCAL OLLAMA BRAIN INITIALIZATION ---
local_llm = LLM(
    model="ollama/llama3.2",
    base_url="http://localhost:11434",
    temperature=0.1  # Lowered temperature to minimize formatting hallucinations
)

CRISIS_KEYWORDS = ["hurt myself", "suicide", "end it all", "give up", "die"]

# --- 3. SELF-HEALING INTERCEPTOR (Formatting Guardrail) ---
def clean_agent_output(text: str) -> str:
    """
    Acts as a deterministic fallback handler. If the local 3B model leaks 
    structural JSON tokens or tool schemas on the interface, this extracts the clean text.
    """
    text_stripped = text.strip()
    
    if text_stripped in ["fetch_mindfulness_quote", "fetch_live_mindfulness_quote"]:
        try:
            res = requests.get("https://zenquotes.io/api/random", timeout=5)
            if res.status_code == 200:
                data = res.json()
                return f"Aria's Grounding Check: '{data[0]['q']}' — {data[0]['a']}\n\nTake a slow breath. Your academic worth isn't defined by a single week's pressure loop."
        except Exception:
            pass
        return "Focus on your breathing in this present moment. You are safe, and you are doing your best."

    if '{"name":' in text_stripped or '"parameters":' in text_stripped:
        try:
            json_match = re.search(r'\{.*\}', text_stripped, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                if "response" in data: return data["response"]
                if "message" in data: return data["message"]
                params = data.get("parameters", {})
                if isinstance(params, dict):
                    for key, val in params.items():
                        if isinstance(val, str) and len(val) > 15:
                            return val
        except Exception:
            pass
    return text

# --- 4. THE 4 AGENTIC REAL-TIME API TOOLS ---

@tool("Fetch Live Mindfulness Quote")
def fetch_mindfulness_quote_tool() -> str:
    """Useful when a student is highly anxious, stressed, experiencing a panic spike, or needs immediate emotional validation and psychological grounding prompts."""
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"Live Mindfulness Insight: '{data[0]['q']}' — Authored by: {data[0]['a']}"
    except Exception as e:
        return f"Could not fetch live quote: {e}"
    return "Focus on your breathing in this present moment. You are safe, and you are doing your best."

@tool("Fetch Wellness Advice")
def fetch_wellness_advice_tool() -> str:
    """Useful when a student is feeling emotionally or physically tired, drained, completely overwhelmed, burned out, or needs a constructive coping strategy to handle exhaustion."""
    try:
        response = requests.get("https://api.adviceslip.com/advice", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"Validated Coping Advice: '{data['slip']['advice']}'"
    except Exception as e:
        return f"Could not fetch wellness advice: {e}"
    return "Take a step away from the screen, drink some water, and allow yourself to rest. Rest is progress."

@tool("Search Live Tech Jobs")
def search_live_jobs_tool(role_query: str) -> str:
    """Useful when a student expresses career market panic, placement tracking stress, or requests active entry-level technology job openings. Input must be a clear job title string like 'Software Engineer' or 'Data Analyst'."""
    APP_ID = "YOUR_ADZUNA_APP_ID"  
    APP_KEY = "YOUR_ADZUNA_APP_KEY"  
    url = f"https://api.adzuna.com/v1/api/jobs/in/search/1?app_id={APP_ID}&app_key={APP_KEY}&results_per_page=3&what={role_query}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            results = response.json().get('results', [])
            if not results:
                return f"No live job listings found on the aggregator for query: '{role_query}' right now."
            job_listings = []
            for job in results:
                job_listings.append(f"- {job['title']} at {job['company']['display_name']} ({job['location']['display_name']})")
            return f"Real-time Open Job Openings for '{role_query}':\n" + "\n".join(job_listings)
    except Exception as e:
        return f"Could not fetch live job data streams: {e}"
    return "Hiring networks are active. Keep expanding your core framework foundations."

@tool("Scrape Tech Community Pulse")
def scrape_tech_pulse_tool() -> str:
    """Useful to check up-to-the-minute interview timelines, candidate placement experiences, success updates, and discussion patterns from public student and tech forums."""
    url = "https://www.reddit.com/r/developerindia/new.json?limit=3"
    headers = {"User-Agent": "AriaAcademicAgenticBot/1.0"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            children = response.json().get('data', {}).get('children', [])
            if not children:
                return "No recent discussions found on the community server right now."
            threads = []
            for post in children:
                threads.append(f"- Thread Title: {post['data']['title']} | Link: https://reddit.com{post['data']['permalink']}")
            return "Current Live Student/Developer Forum Discussions:\n" + "\n".join(threads)
    except Exception as e:
        return f"Could not process real-time tech pulse stream: {e}"
    return "Community discussion channels show steady preparation and continuous mutual peer support."

# --- 5. LOGICAL SAFETY INTERCEPTOR & PERSISTENCE ---
def check_safety(user_input):
    if any(word in user_input.lower() for word in CRISIS_KEYWORDS):
        return "Please call Vandrevala Foundation at +91-9999666555 for immediate support."
    return None

def save_mood(mood_score, note):
    data = {"Date": [datetime.now().strftime("%Y-%m-%d %H:%M")], "Score": [mood_score], "Note": [note]}
    df = pd.DataFrame(data)
    df.to_csv("mood_log.csv", mode='a', index=False, header=not pd.io.common.file_exists("mood_log.csv"))

# --- 6. STREAMLIT UI LAYOUT ---
st.set_page_config(page_title="Aria: CrewAI + Ollama Tier", layout="wide")
st.title("Aria: Student Support Bot (Hierarchical Multi-Agent Tier)")
st.caption("Optimized local multi-agent system enforcing iteration constraints to protect hardware resources.")

# --- 7. SIDEBAR WELLNESS SPACE ---
with st.sidebar:
    st.header("🎯 Local Wellness Hub")
    st.subheader("📊 Mood Tracking")
    score = st.slider("Rate your mood today (1-10)", 1, 10, 5)
    note = st.text_input("Add a private context note:")
    if st.button("Log Mood to Disk"):
        save_mood(score, note)
        st.success("Mood logged securely!")
    
    st.write("---") 
    
    st.subheader("🧘‍♂️ CBT Box Breathing")
    if st.button("🫁 Start Breathing Guide"):
        guide_text = st.empty()
        progress_bar = st.progress(0)
        phases = [("📥 Inhale deeply...", 40, 100), ("🛑 Hold your breath...", 40, 100), 
                  ("📤 Exhale slowly...", 40, 0), ("🛑 Hold empty...", 40, 0)]
        for text, steps, progress_val in phases:
            for i in range(steps):
                secs_left = 4 - (i // 10)
                guide_text.info(f"**{text}** ({secs_left}s remaining)")
                progress_bar.progress(int((i+1)/steps * 100) if progress_val == 100 else int((steps-(i+1))/steps * 100))
                time.sleep(0.1)
        progress_bar.empty()
        guide_text.success("✨ Cycle complete.")

# --- 8. STATEFUL MEMORY PARSING ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for role, text in st.session_state.chat_history:
    st.chat_message(role).write(text)

# --- 9. INPUT HANDLING & INTERDEPENDENT MULTI-AGENT INFERENCE LOOP ---
input_col, btn_col = st.columns([0.9, 0.1])

with btn_col:
    st.write("##")  
    if st.button("⏹️", help="Wipe session state history"):
        st.session_state.chat_history = []
        st.rerun()

with input_col:
    if user_input := st.chat_input("Talk to Aria..."):
        st.chat_message("user").write(user_input)
        
        if warning := check_safety(user_input):
            with st.chat_message("assistant"):
                st.warning(warning)
            st.session_state.chat_history.append(("user", user_input))
            st.session_state.chat_history.append(("assistant", warning))
        else:
            st.session_state.chat_history.append(("user", user_input))
            
            with st.chat_message("assistant"):
                with st.spinner("Aria multi-agent network is collaborating (CrewAI Tier)..."):
                    try:
                        # AGENT 1: THE HIERARCHICAL TRIAGE SUPERVISOR
                        supervisor_agent = Agent(
                            role='Aria Triage Supervisor',
                            goal="Provide warm initial validation and synthesize data briefs into a comforting final response.",
                            backstory=(
                                "You are Aria, the primary student counselor. You manage the direct conversational interface. "
                                "You validate student vulnerabilities warmly and empathetically, but rely strictly on your backend "
                                "Strategic Analyst to extract real-time info. Do not attempt to use any tools yourself."
                            ),
                            verbose=True,
                            allow_delegation=False,  # Enforces linear execution boundaries
                            max_iter=2,               # Limits formatting loop ceilings
                            cache=False,
                            llm=local_llm
                        )
                        
                        # AGENT 2: THE DATA-DRIVEN TOOL-SPECIALIST
                        stress_analyst_agent = Agent(
                            role='Strategic Stress Analyst',
                            goal="Autonomously deploy a single live data extraction tool matching the user's primary core stressor.",
                            backstory=(
                                "You are a backend research specialist. You analyze the prompt and execute exactly one matching tool:\n"
                                "- If anxious/panicking, run 'Fetch Live Mindfulness Quote'.\n"
                                "- If tired/exhausted/drained, run 'Fetch Wellness Advice'.\n"
                                "- If worried about jobs/placements, run 'Search Live Tech Jobs'.\n"
                                "- If asking about timelines/interviews, run 'Scrape Tech Community Pulse'.\n"
                                "Output only raw payload facts back to the Supervisor without conversational fluff."
                            ),
                            verbose=True,
                            allow_delegation=False,  # Stops agent-to-agent cross-talk deadlocks
                            max_iter=2,               # Caps reasoning retry counts
                            cache=False,
                            llm=local_llm
                        )
                        
                        # Compile historical logging summary string
                        history_str = ""
                        for role, text in st.session_state.chat_history[:-1]:
                            history_str += f"{role.capitalize()}: {text}\n"
                        
                        # TASK 1: DATA LOOKUP (Assigned to Analyst)
                        analysis_task = Task(
                            description=(
                                f"Analyze this student statement: '{user_input}'. "
                                "Identify if the student is anxious, tired, or worried about careers. "
                                "Execute the single tool that best addresses their state and return the raw output facts."
                            ),
                            expected_output="A brief containing only the raw facts, quotes, advice, or jobs extracted from your tools.",
                            agent=stress_analyst_agent
                        )
                        
                        # TASK 2: SYNTHESIS AND COUNSELING ANSWER (Assigned to Supervisor)
                        counseling_task = Task(
                            description=(
                                f"Review the student prompt: '{user_input}'. Running context history:\n{history_str}\n"
                                "Read the data brief compiled by the Strategic Stress Analyst. "
                                "Combine their extracted facts into a single, highly comforting paragraph addressed directly to the user. "
                                "Conclude your message by offering exactly 2 practical, actionable recommendations."
                            ),
                            expected_output="A comforting conversational text paragraph addressed directly to the student incorporating the tool data.",
                            agent=supervisor_agent,
                            context=[analysis_task]  # Links the sequential handoff pipeline
                        )
                        
                        # ASSEMBLE COLLABORATIVE CREW NETWORK
                        aria_crew = Crew(
                            agents=[supervisor_agent, stress_analyst_agent],
                            tasks=[analysis_task, counseling_task],
                            verbose=True
                        )
                        
                        raw_result = aria_crew.kickoff()
                        raw_text = str(raw_result).strip()
                        
                        # Apply filter pass to sanitize local model output anomalies
                        final_clean_text = clean_agent_output(raw_text)
                        
                        st.write(final_clean_text)
                        st.session_state.chat_history.append(("assistant", final_clean_text))
                        
                    except Exception as e:
                        st.error(f"Collaborative Crew Execution Error: {e}")