import streamlit as st
import pandas as pd
from datetime import datetime
import time
import os
from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

# --- 1. CONFIGURATION & DATASET INTEGRATION ---
# Using Llama 3.2 for speed on standard hardware
MODEL_NAME = "llama3.2"
# Updated list with phrases
# --- 1. EXPANDED KEYWORDS ---
CRISIS_KEYWORDS = [
    "hurt myself", "suicide", "end it all", "give up", "die",
    "kill myself", "better off dead", "no reason to live", 
    "cut myself", "goodbye forever", "end my life", "i'm a burden",
    "self harm", "don't want to be here", "final note", "overdose"
]

# System prompt integrated with 2026 student stress data insights[cite: 1]
SYSTEM_PROMPT = """
You are 'Aria', an empathetic mental health assistant for students. 
Insights from the 2026 Student Stress Dataset show that placement pressure, 
backlog anxiety, and sleep deprivation are the top stressors. 
Acknowledge these specific struggles when relevant.
IMPORTANT: You are NOT a doctor. If the user mentions self-harm, provide crisis hotlines.
Keep your responses supportive, validating, and concise.
"""

# --- 2. MOOD TRACKING SYSTEM ---
def save_mood(mood_score, note):
    """Saves user mood data to a local CSV file for persistence[cite: 1]."""
    file_path = "mood_log.csv"
    data = {
        "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")], 
        "Score": [mood_score], 
        "Note": [note]
    }
    df = pd.DataFrame(data)
    try:
        # Append to existing file or create new one[cite: 1]
        file_exists = os.path.isfile(file_path)
        df.to_csv(file_path, mode='a', index=False, header=not file_exists)
        return True
    except Exception:
        return False

# --- 3. CBT MODULE: BOX BREATHING ---
def run_breathing_exercise():
    """Interactive module for box breathing using real-time UI updates[cite: 1]."""
    st.info("Let's do some Box Breathing. Follow the prompts below...")
    placeholder = st.empty()
    steps = [
        ("Inhale...", "🌬️", 4), 
        ("Hold...", "✋", 4), 
        ("Exhale...", "💨", 4), 
        ("Rest...", "🧘", 4)
    ]
    
    for i in range(2): # 2 Rounds of the exercise
        for text, emoji, sec in steps:
            for remaining in range(sec, 0, -1):
                placeholder.markdown(f"### {emoji} {text} ({remaining}s)")
                time.sleep(1)
    placeholder.success("Well done. Taking a moment to breathe can significantly reduce stress.")


# --- 2. THE CORRECT SAFETY FUNCTION ---
def check_safety(user_input):
    """Scans for high-risk keywords and returns a helpline message if triggered."""
    # Standardize to lowercase for better matching
    text = user_input.lower()
    
    if any(keyword in text for keyword in CRISIS_KEYWORDS):
        # We return the actual text we want to show the user
        return ("I'm really concerned about what you're sharing. Please know that you're not alone. "
                "In India, you can call the Vandrevala Foundation at +91-9999666555 or KIRAN at 1800-599-0019. "
                "Please reach out to a professional immediately.")
    
    # If no keywords are found, we return None so the AI can take over[cite: 1]
    return None


# --- 5. STREAMLIT UI SETUP ---
st.set_page_config(page_title="Aria Support Pro", page_icon="🌿", layout="wide")

# Sidebar for Student Tools & Metadata
with st.sidebar:
    st.title("🌿 Aria Pro Tools")
    st.markdown("---")
    
    # Mood Tracker Section
    st.header("📊 Mood Tracker")
    mood_val = st.slider("How is your mood (1-10)?", 1, 10, 5)
    mood_note = st.text_input("Note (e.g., 'Lab stress')")
    if st.button("Log Mood Score"):
        if save_mood(mood_val, mood_note):
            st.success("Mood successfully logged to mood_log.csv")
    
    st.markdown("---")
    
    # CBT Exercise Section
    st.header("🧘 Therapy Module")
    if st.button("Start Box Breathing"):
        run_breathing_exercise()

    st.markdown("---")
    
    # Session Management
    if st.button("Reset Conversation"):
        st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]
        st.rerun()

# Main Chat Interface
st.title("Aria: Mental Health Companion")
st.caption("A private, local AI powered by Llama 3.2 and LangChain.")

# Initialize Session Memory[cite: 1]
if "messages" not in st.session_state:
    st.session_state.messages = [SystemMessage(content=SYSTEM_PROMPT)]

# Display Chat History (Excluding System Message)
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)
    elif isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)

# --- 6. CHAT EXECUTION ---
if user_input := st.chat_input("How are you feeling right now?"):
    # Display user input
    st.chat_message("user").write(user_input)
    
    # Step 1: Safety Interception[cite: 1]
    warning = check_safety(user_input)
    
    if warning:
        with st.chat_message("assistant"):
            st.warning(warning)
        st.session_state.messages.append(AIMessage(content=warning))
    else:
        # Step 2: LLM Inference via Ollama[cite: 1]
        with st.chat_message("assistant"):
            with st.spinner("Aria is processing..."):
                try:
                    
                # Initialize local model connector with explicit loopback routing
                    llm = ChatOllama(model=MODEL_NAME, base_url="http://127.0.0.1:11434")
                    
                    # Update message history
                    st.session_state.messages.append(HumanMessage(content=user_input))
                    
                    # Get response (Limited memory window: system prompt + last 6 messages)
                    response = llm.invoke(st.session_state.messages)
                    st.write(response.content)
                    
                    # Store response in history
                    st.session_state.messages.append(AIMessage(content=response.content))
                except Exception as e:
                    st.error(f"Inference Error: Ensure Ollama is running. ({e})")
