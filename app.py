import streamlit as st
import os
import sys

# --- 1. SETUP PAGE ---
st.set_page_config(page_title="Omnishell AI", page_icon="🤖")
st.title("🤖 Omnishell Cloud")
st.caption("Generate and explain Linux commands via the web.")

# --- 2. API KEY BRIDGE ---
# We must inject the secret into the environment BEFORE importing omnishell
# otherwise omnishell.py will crash with sys.exit(1)
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
else:
    st.error("⚠️ GROQ_API_KEY is missing in Streamlit Secrets!")
    st.stop()

# --- 3. IMPORT YOUR LOGIC ---
# Now it is safe to import
try:
    import omnishell
except SystemExit:
    st.warning("⚠️ Omnishell tried to exit. Check your API Key configuration.")

# --- 4. SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 5. CHAT INTERFACE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Describe a task (e.g., 'Update my system')"):
    # 1. Show User Input
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Generate Command using Omnishell's brain
    with st.spinner("Generating command..."):
        try:
            # We call the function from your file
            command = omnishell.generate_command(prompt)
            
            response_text = f"**Suggested Command:**\n```bash\n{command}\n```"
            
            # 3. Get Explanation automatically (better for web)
            explanation = omnishell.get_explanation(command)
            response_text += f"\n\n**Explanation:**\n{explanation}"

        except Exception as e:
            response_text = f"Error: {str(e)}"

    # 4. Show AI Response
    with st.chat_message("assistant"):
        st.markdown(response_text)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})