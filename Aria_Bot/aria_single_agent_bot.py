import streamlit as st
import pandas as pd
from datetime import datetime
import time  # Controls frame rendering delays for the countdown timer
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# --- 1. CONFIGURATION & CORE ENGINE ---
MODEL_NAME = "llama3.2"
CRISIS_KEYWORDS = ["hurt myself", "suicide", "end it all", "give up", "die"]

SYSTEM_PROMPT = """You are 'Aria', an empathetic mental health assistant for students. 
Insights from the 2026 Student Stress Dataset show that placement pressure, backlog anxiety, 
and sleep deprivation are the top student stressors. Always acknowledge these specific struggles warmly 
when relevant. Keep your tone gentle, supportive, and completely non-judgmental."""

# --- 2. LOGICAL SAFETY INTERCEPTOR ---
def check_safety(user_input):
    if any(word in user_input.lower() for word in CRISIS_KEYWORDS):
        return "Please call Vandrevala Foundation at +91-9999666555 for immediate support."
    return None

# --- 3. LOCAL DATAFRAME PERSISTENCE ---
def save_mood(mood_score, note):
    data = {
        "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")], 
        "Score": [mood_score], 
        "Note": [note]
    }
    df = pd.DataFrame(data)
    df.to_csv("mood_log.csv", mode='a', index=False, 
              header=not pd.io.common.file_exists("mood_log.csv"))

# --- 4. STREAMLIT FRONTEND SETUP ---
st.set_page_config(page_title="Aria: Single Agent", layout="wide")
st.title("Aria: Student Support Bot (Single-Agent Tier)")
st.caption("A private, local chatbot utilizing LangChain orchestration directly with Ollama.")

# --- 5. SIDEBAR WELLNESS SPACE (Mood Tracker & CBT Pacing Guide) ---
with st.sidebar:
    st.header("🎯 Local Wellness Hub")
    
    # Module I: Mood Tracker
    st.subheader("📊 Mood Tracking")
    score = st.slider("Rate your mood today (1-10)", 1, 10, 5)
    note = st.text_input("Add a private context note:")
    if st.button("Log Mood to Disk"):
        save_mood(score, note)
        st.success("Mood locked securely in mood_log.csv!")
    
    st.write("---") 
    
    # Module II: CBT Box Breathing Exercise with High-Refresh Countdown Timers
    st.subheader("🧘‍♂️ CBT Box Breathing")
    st.caption("Synchronize your breathing with this countdown guide to reduce somatic anxiety.")
    
    if st.button("🫁 Start Breathing Guide"):
        guide_text = st.empty()
        progress_bar = st.progress(0)
        
        # 1. Inhale Phase
        for i in range(40):
            secs_left = 4 - (i // 10)
            guide_text.info(f"📥 **Inhale deeply...** ({secs_left}s remaining)")
            progress_bar.progress(int((i + 1) / 40 * 100))
            time.sleep(0.1)
            
        # 2. Hold Phase
        for i in range(40):
            secs_left = 4 - (i // 10)
            guide_text.warning(f"🛑 **Hold your breath...** ({secs_left}s remaining)")
            progress_bar.progress(100)
            time.sleep(0.1)
            
        # 3. Exhale Phase
        for i in range(40):
            secs_left = 4 - (i // 10)
            guide_text.info(f"📤 **Exhale slowly...** ({secs_left}s remaining)")
            progress_bar.progress(int((40 - (i + 1)) / 40 * 100))
            time.sleep(0.1)
            
        # 4. Hold Empty Phase
        for i in range(40):
            secs_left = 4 - (i // 10)
            guide_text.warning(f"🛑 **Hold empty...** ({secs_left}s remaining)")
            progress_bar.progress(0)
            time.sleep(0.1)
            
        progress_bar.empty()
        guide_text.success("✨ **Cycle complete.** Your heart rate should begin stabilizing.")

# --- 6. STATEFUL MEMORY PARSING ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display persistent session chat history
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

# --- 7. INPUT HANDLING & INTEGRATED CONTROL LAYOUT ---
input_col, btn_col = st.columns([0.9, 0.1])

with btn_col:
    st.write("##")  # Pad visual grid gap
    if st.button("⏹️", help="Wipe session state history"):
        st.session_state.messages = []
        st.rerun()

with input_col:
    if user_input := st.chat_input("Talk to Aria..."):
        st.chat_message("user").write(user_input)
        
        # Hardcoded Pre-Inference Interception Check
        warning = check_safety(user_input)
        
        if warning:
            with st.chat_message("assistant"):
                st.warning(warning)
            st.session_state.messages.append(HumanMessage(content=user_input))
            st.session_state.messages.append(AIMessage(content=warning))
        else:
            st.session_state.messages.append(HumanMessage(content=user_input))
            
            with st.chat_message("assistant"):
                with st.spinner("Aria is listening..."):
                    try:
                        # Call local ChatOllama model connector directly
                        llm = ChatOllama(model=MODEL_NAME, base_url="http://127.0.0.1:11434")
                        
                        # Pack context: Persona Prompt + Entire Stored Chat Array
                        payload = [SystemMessage(content=SYSTEM_PROMPT)] + st.session_state.messages
                        
                        # Generate inference via API invocation response loop
                        response = llm.invoke(payload)
                        
                        st.write(response.content)
                        st.session_state.messages.append(AIMessage(content=response.content))
                        
                    except Exception as e:
                        st.error(f"Inference Error: {e}")