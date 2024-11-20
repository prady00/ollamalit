from typing import Generator, List, Dict
import ollama
import streamlit as st
from ollama import Client

# Streamlit app configuration
st.set_page_config(layout="wide", page_title="OllamaLit")

# Helper functions
def initialize_session_state() -> None:
    """Initialize session state variables if they don't exist."""
    if "ollama_host" not in st.session_state:
        st.session_state.ollama_host = "http://localhost:11434"
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []

def get_ollama_models() -> List[str]:
    """Fetches available model names from the Ollama client."""
    return [model["name"] for model in ollama.list()["models"]]

def display_chat_history(messages: List[Dict[str, str]]) -> None:
    """Displays chat history based on user and assistant messages."""
    for message in messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def ask_ollama(ollama_url: str, model_name: str, messages: List[Dict[str, str]]) -> Generator:
    """Generates responses from Ollama model via streaming."""
    stream = Client(host=ollama_url).chat(
        model=model_name,
        messages=messages,
        stream=True
    )
    for chunk in stream:
        yield chunk['message']['content']

# Main function to render the app UI
def main() -> None:
    st.title("OllamaLit")

    # Initialize session state
    initialize_session_state()

    with st.expander("Configuration"):
        # Sidebar inputs for host URL and model selection
        st.session_state.ollama_host = st.text_input("Ollama Host:", st.session_state.ollama_host)
        st.session_state.selected_model = st.selectbox("Select the model:", get_ollama_models())

    # Display chat history
    display_chat_history(st.session_state.messages)

    # Input for user message
    if prompt := st.chat_input("How can I help you?"):
        # Append user message to the session state
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user's message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate and display assistant's response
        with st.chat_message("assistant"):
            response = "".join(ask_ollama(
                st.session_state.ollama_host,
                st.session_state.selected_model,
                st.session_state.messages
            ))
            st.markdown(response)

        # Append assistant's response to the session state
        st.session_state.messages.append({"role": "assistant", "content": response})

# Run the app
if __name__ == "__main__":
    main()
