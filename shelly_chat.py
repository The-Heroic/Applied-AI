import ollama

def run_shelly_chat():
    model_name = 'llama3.2:1b'  # Still using the fast, small model
    
    print("\n--- Shelly AI: Active ---")
    print("Type 'exit' to stop chatting.")

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Shelly: Goodbye, Anurag! Closing session...")
            break

        try:
            print("Shelly: ", end="", flush=True)
            
            stream = ollama.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': user_input}],
                stream=True,
            )

            for chunk in stream:
                print(chunk['message']['content'], end="", flush=True)
            print() 

        except Exception as e:
            print(f"\n[System Error]: {e}")
            break

if __name__ == "__main__":
    run_shelly_chat()