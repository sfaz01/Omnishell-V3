import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

# 1. Load the secrets
load_dotenv()

# 2. Initialize Llama 3.3 via Groq
# This is the "Fixed" model name that works in Dec 2025
llm = ChatGroq(
    model="llama-3.3-70b-versatile", 
    temperature=0.7,
    groq_api_key=os.getenv("GROQ_API_KEY") 
)

# 3. Test it
print("🤖 Connecting to Llama 3.3 (Free Tier)...")
try:
    response = llm.invoke("Hello! I am building an AI agent. Briefly, what is the most exciting thing about AI agents?")
    print(f"\n✅ SUCCESS! Llama 3.3 says:\n{response.content}")
except Exception as e:
    print(f"\n❌ Error: {e}")