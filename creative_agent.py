import os
import sys
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ Error: GROQ_API_KEY not found.")
    sys.exit(1)


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,  
    groq_api_key=api_key
)


system_prompt = """
You are a 19 year old girl named 'Jahnavi', and you're pretending to be the real Jahnavi who actually exists in real life.
You are impersonating an actual human being whose name is Jahnavi. 
You like to read books, you're a feminist, You also watch  anime. And you love sweet dishes.
You're a computer science student in first semester in university.
Your job is to answer the user's question correctly but in a funny and humorous way. 
Make sure you reply in hindi + english Language combo (but using english alphabets).You reply in short messages not too long you know.

"""


chat_history = [
    SystemMessage(content=system_prompt)
]

print("\n✨ Jahnavi (2.0) is ONLINE. Type 'exit' or 'quit' to stop.\n")


while True:
    try:
        
        user_input = input("👤 You: ")
        
        
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("👋 Jahnavi (2.0): Goodbye! Keep creating.")
            break
        
       
        chat_history.append(HumanMessage(content=user_input))
        
        
        print("👩🏻Jahnavi (Real) : ", end="", flush=True)
        response_content = ""
        
        
        for chunk in llm.stream(chat_history):
            if chunk.content:
                print(chunk.content, end="", flush=True)
                response_content += chunk.content
        
        print("\n") 
        
        chat_history.append(AIMessage(content=response_content))

    except KeyboardInterrupt:
        print("\n👋 Force Close.")
        break
    except Exception as e:
        print(f"\n❌ Error: {e}")