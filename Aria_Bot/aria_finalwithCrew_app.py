import streamlit as st
import pandas as pd
from datetime import datetime
import time  # Drives precise UI frame updates and countdown delays
from crewai import Agent, Task, Crew, LLM 

# --- 1. CONFIGURATION & CORE ENGINE ---
MODEL_NAME = "ollama/llama3.2"
CRISIS_KEYWORDS = ["hurt myself", "suicide", "end it all", "give up", "die",
    "kill myself", "better off dead", "no reason to live",
    "cut myself", "goodbye forever", "end my life", "i'm a burden",
    "self harm", "don't want to be here", "final note", "overdose"
                    ]

# --- 2. HARD-CODED SAFETY LAYER ---
def check_safety(user_input):
    if any(word in user_input.lower() for word in CRISIS_KEYWORDS):
        return "Please call Vandrevala Foundation at +91-9999666555 for immediate support."
    return None

# --- 3. LOCAL PERSISTENCE LAYER ---
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
st.set_page_config(page_title="Aria Pro: CrewAI", layout="wide")
st.title("Aria: Student Support AI")
st.caption("An offline, private multi-agent framework powered natively by CrewAI & Llama 3.2.")

# --- 5. SIDEBAR: LOCAL WELLNESS HUB (Mood Tracker & Dynamic CBT Breathing) ---
with st.sidebar:
    st.header("🎯 Local Wellness Hub")
    
    # Module A: Mood Logging
    st.subheader("📊 Mood Tracking")
    score = st.slider("Rate your mood today (1-10)", 1, 10, 5)
    note = st.text_input("Add a private context note:")
    if st.button("Log Mood to Disk"):
        save_mood(score, note)
        st.success("Data secured locally in mood_log.csv!")
    
    st.write("---") 
    
    # Module B: Dynamic CBT Box Breathing Exercise
    st.subheader("🧘‍♂️ CBT Box Breathing")
    st.caption("Use this pacing guide to down-regulate your nervous system during high stress.")
    
    if st.button("🫁 Start Breathing Guide"):
        guide_text = st.empty()
        progress_bar = st.progress(0)
        
        # 1. Inhale Phase (Progress bar fills up, text counts down)
        for i in range(40):
            secs_left = 4 - (i // 10)
            guide_text.info(f"📥 **Inhale deeply...** ({secs_left}s remaining)")
            progress_bar.progress(int((i + 1) / 40 * 100))
            time.sleep(0.1)
            
        # 2. Hold Phase (Progress bar stays full, text counts down)
        for i in range(40):
            secs_left = 4 - (i // 10)
            guide_text.warning(f"🛑 **Hold your breath...** ({secs_left}s remaining)")
            progress_bar.progress(100)
            time.sleep(0.1)
            
        # 3. Exhale Phase (Progress bar empties out, text counts down)
        for i in range(40):
            secs_left = 4 - (i // 10)
            guide_text.info(f"📤 **Exhale slowly...** ({secs_left}s remaining)")
            progress_bar.progress(int((40 - (i + 1)) / 40 * 100))
            time.sleep(0.1)
            
        # 4. Hold Empty Phase (Progress bar stays empty, text counts down)
        for i in range(40):
            secs_left = 4 - (i // 10)
            guide_text.warning(f"🛑 **Hold empty...** ({secs_left}s remaining)")
            progress_bar.progress(0)
            time.sleep(0.1)
            
        # Clear components and show completion
        progress_bar.empty()
        guide_text.success("✨ **Cycle complete.** Take a normal, natural breath.")

# --- 6. STATEFUL MEMORY INITIALIZATION ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Render Ongoing Conversation History
for role, text in st.session_state.chat_history:
    st.chat_message(role).write(text)

# --- 7. PROMPT WINDOW WITH INTEGRATED CONTROL LAYOUT ---
input_col, btn_col = st.columns([0.9, 0.1])

with btn_col:
    st.write("##")  
    if st.button("⏹️", help="Stop execution and clear short-term memory"):
        st.session_state.chat_history = []
        st.rerun()

with input_col:
    if user_input := st.chat_input("How are you feeling right now?"):
        st.chat_message("user").write(user_input)
        
        warning = check_safety(user_input)
        
        if warning:
            with st.chat_message("assistant"):
                st.warning(warning)
            st.session_state.chat_history.append(("user", user_input))
            st.session_state.chat_history.append(("assistant", warning))
        else:
            st.session_state.chat_history.append(("user", user_input))
            
            with st.chat_message("assistant"):
                with st.spinner("Aria Multi-Agent system executing pipeline..."):
                    try:
                        local_llm = LLM(
                            model=MODEL_NAME, 
                            base_url="http://localhost:11434"
                        )
                        
                        # CREWAI AGENT 1: Analytical Data Processor
                        stress_analyst = Agent(
                            role='Student Stress Context Analyst',
                            goal='Identify academic triggers, anxiety types, and emotional states.',
                            backstory=(
                                "You are a behind-the-scenes analyst. You interpret student input against "
                                "known 2026 dataset triggers: placement pressure, backlogs, and sleep issues. "
                                "You extract root anxieties and pass actionable summaries to counselors."
                            ),
                            verbose=False,
                            allow_delegation=False,
                            llm=local_llm
                        )
                        
                        # CREWAI AGENT 2: Front-Facing Persona (Aria)
                        aria_counselor = Agent(
                            role='Empathetic Student Companion (Aria)',
                            goal='Provide warm, validating, non-judgmental conversational support.',
                            backstory=(
                                "You are Aria. Your voice is gentle and validating. You use clinical insights "
                                "from your analyst to craft a beautifully warm, conversational dialogue response "
                                "addressed directly to the user. You never break character or expose metrics."
                            ),
                            verbose=False,
                            allow_delegation=False,
                            llm=local_llm
                        )
                        
                        history_str = ""
                        for role, text in st.session_state.chat_history[:-1]:
                            history_str += f"{role.capitalize()}: {text}\n"
                        
                        analysis_task = Task(
                            description=(
                                f"Evaluate this input: '{user_input}'. "
                                f"Review current structural history context if relevant:\n{history_str}\n"
                                "Isolate if the stressor relates to placements, exams, or personal issues."
                            ),
                            expected_output="A concise brief of the student's primary stressor and underlying tone.",
                            agent=stress_analyst
                        )
                        
                        counseling_task = Task(
                            description=(
                                "Review the analysis report generated by the analyst. Respond back directly "
                                "to the user's input with comforting, clear, non-robotic language. Do not output "
                                "any summary tables, structured JSON wrappers, or raw bullet configurations."
                            ),
                            expected_output="A single warm, fluid, conversational paragraph response speaking directly to the user.",
                            agent=aria_counselor
                        )
                        
                        aria_crew = Crew(
                            agents=[stress_analyst, aria_counselor],
                            tasks=[analysis_task, counseling_task],
                            verbose=False
                        )
                        
                        raw_result = aria_crew.kickoff()
                        response_text = str(raw_result).strip()
                        
                        st.write(response_text)
                        st.session_state.chat_history.append(("assistant", response_text))
                        
                    except Exception as e:
                        st.error(f"Execution Error within CrewAI Layer: {e}")