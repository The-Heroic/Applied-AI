import streamlit as st
import pandas as pd
from datetime import datetime
import time
import os
import requests
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool

# --- 1. CORE CONFIGURATION ---
MODEL_NAME = "llama3.2"
BASE_URL = "http://localhost:11434"
CRISIS_KEYWORDS = ["hurt myself", "suicide", "end it all", "give up", "die"]

# --- 2. DEFINING EXPLICIT AGENTIC TOOLS ---

@tool
def fetch_mindfulness_quote() -> str:
    """Useful when a student is highly anxious, stressed, experiencing a panic spike, or needs immediate emotional validation and grounding prompts."""
    try:
        response = requests.get("https://zenquotes.io/api/random", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"Live Mindfulness Insight: '{data[0]['q']}' — Authored by: {data[0]['a']}"
    except Exception as e:
        return f"Could not fetch live quote: {e}"
    return "Focus on your breathing in this present moment. You are safe, and you are doing your best."

@tool
def fetch_wellness_advice() -> str:
    """Useful when a student is feeling emotionally or physically tired, drained, completely overwhelmed, or needs a constructive coping strategy to handle exhaustion."""
    try:
        response = requests.get("https://api.adviceslip.com/advice", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return f"Validated Coping Advice: '{data['slip']['advice']}'"
    except Exception as e:
        return f"Could not fetch wellness advice: {e}"
    return "Take a step away from the screen, drink some water, and allow yourself to rest. Rest is progress."

@tool
def search_live_jobs(role_query: str) -> str:
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

@tool
def scrape_tech_pulse() -> str:
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

# Map tools structurally for explicit local python execution loops
TOOLS_MAP = {
    "fetch_mindfulness_quote": fetch_mindfulness_quote,
    "fetch_wellness_advice": fetch_wellness_advice,
    "search_live_jobs": search_live_jobs,
    "scrape_tech_pulse": scrape_tech_pulse
}
ALL_TOOLS = list(TOOLS_MAP.values())

# --- 3. SYSTEM PROMPT SCHEMA ---
SYSTEM_PROMPT = (
    "You are Aria, a compassionate, professional university academic and mental health counselor. "
    "Your job is to converse with students who are reaching out about placement tracking stress, exam pressures, backlogs, or exhaustion.\n\n"
    "Insights from the 2026 student stress guidelines show that academic timelines and career tracking are major contributors to anxiety. "
    "Always validate the user's feelings warmly and empathetically. You have direct access to real-time tools. "
    "If a tool's output is provided to you, incorporate those facts smoothly into your final conversational message. "
    "Always wrap up your response by offering exactly 2 highly targeted, practical recommendations to guide the student forward."
)

# --- 4. DATA PERSISTENCE & SAFETY ---
def check_safety(user_input):
    if any(word in user_input.lower() for word in CRISIS_KEYWORDS):
        return "Please call Vandrevala Foundation at +91-9999666555 for immediate support."
    return None

def save_mood(mood_score, note):
    data = {"Date": [datetime.now().strftime("%Y-%m-%d %H:%M")], "Score": [mood_score], "Note": [note]}
    df = pd.DataFrame(data)
    df.to_csv("mood_log.csv", mode='a', index=False, header=not pd.io.common.file_exists("mood_log.csv"))

# --- 5. STREAMLIT UI SETUP ---
st.set_page_config(page_title="Aria: Single-Agent Tier", layout="wide")
st.title("Aria: Student Support Bot (Single-Agent Tool-Bound Tier)")
st.caption("Deterministic local execution framework binding explicit API tools to Ollama's Llama 3.2 model endpoint.")

# --- 6. SIDEBAR WELLNESS SPACE ---
with st.sidebar:
    st.header("🎯 Local Wellness Hub")
    st.subheader("📊 Mood Tracking")
    score = st.slider("Rate your mood today (1-10)", 1, 10, 5)
    note = st.text_input("Add a private context note:")
    if st.button("Log Mood to Disk"):
        save_mood(score, note)
        st.success("Mood locked securely to disk!")
    
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
        guide_text.success("✨ Cycle complete. Your heart rate should begin stabilizing.")

# --- 7. STATEFUL CONVERSATION MEMORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage) and msg.content:
        st.chat_message("assistant").write(msg.content)

# --- 8. SINGLE AGENT DETERMINISTIC EXECUTION LOOP ---
input_col, btn_col = st.columns([0.9, 0.1])
with btn_col:
    st.write("##")  
    if st.button("⏹️", help="Wipe session state history"):
        st.session_state.messages = []
        st.rerun()

with input_col:
    if user_input := st.chat_input("Talk to Aria..."):
        st.chat_message("user").write(user_input)
        
        if safety_warning := check_safety(user_input):
            with st.chat_message("assistant"):
                st.warning(safety_warning)
            st.session_state.messages.append(HumanMessage(content=user_input))
            st.session_state.messages.append(AIMessage(content=safety_warning))
        else:
            st.session_state.messages.append(HumanMessage(content=user_input))
            
            with st.chat_message("assistant"):
                with st.spinner("Ollama is processing core tool schemas..."):
                    try:
                        # Establish connection to your local background Ollama instance
                        llm = ChatOllama(model=MODEL_NAME, base_url=BASE_URL, temperature=0.2)
                        llm_with_tools = llm.bind_tools(ALL_TOOLS)
                        
                        # Build standard structural messaging context history pipeline
                        payload = [SystemMessage(content=SYSTEM_PROMPT)] + st.session_state.messages
                        
                        # Initial model evaluation pass to parse tool requirements
                        response = llm_with_tools.invoke(payload)
                        
                        # Programmatic Interception: Check if the model requested an API tool execution
                        if response.tool_calls:
                            for tool_call in response.tool_calls:
                                tool_name = tool_call["name"].lower()
                                tool_args = tool_call["args"]
                                
                                with st.status(f"🛠️ Executing local system tool: {tool_name}...", expanded=False) as status:
                                    if tool_name in TOOLS_MAP:
                                        # Execute the native python code explicitly
                                        tool_result = TOOLS_MAP[tool_name].invoke(tool_args)
                                        st.write(tool_result)
                                        status.update(label="API Data successfully captured!", state="complete")
                                    else:
                                        tool_result = "Tool not found."
                                        status.update(label="Execution mismatch encountered.", state="error")
                                
                                # Append the live API payload stream straight back into the conversation context
                                payload.append(AIMessage(content=f"[System Executed Tool Result for {tool_name}]: {tool_result}"))
                            
                            # Final evaluation pass forcing the model to read the newly collected web data
                            final_response = llm.invoke(payload)
                            final_text = final_response.content
                        else:
                            final_text = response.content
                        
                        # Output clean text securely onto the front-facing chat stream
                        st.write(final_text)
                        st.session_state.messages.append(AIMessage(content=final_text))
                        
                    except Exception as e:
                        st.error(f"Inference Connection Crash: {e}")