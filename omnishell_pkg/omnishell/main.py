import os
import sys
import platform
import subprocess
import logging
import argparse
from dotenv import load_dotenv, find_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

# --- CONFIGURATION ---

logging.basicConfig(
    filename='omnishell.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    import distro
except ImportError:
    print("⚠️  Missing library. Please run: pip install distro")
    sys.exit(1)

load_dotenv(find_dotenv())
api_key = os.getenv("GROQ_API_KEY")

if not api_key and "GROQ_API_KEY" not in os.environ:
    print("❌ Error: GROQ_API_KEY not found.")
    sys.exit(1)

# --- CORE LOGIC ---

def detect_system_info():
    try:
        distro_name = distro.name(pretty=True)
        pkg_managers = {
            "arch": "pacman", "cachyos": "pacman", "manjaro": "pacman",
            "ubuntu": "apt", "debian": "apt", "fedora": "dnf", "alpine": "apk"
        }
        pkg_mgr = pkg_managers.get(distro.id(), "unknown")
        if "cachyos" in distro_name.lower(): pkg_mgr = "pacman"
        return distro_name, pkg_mgr
    except:
        return "Linux", "unknown"

distro_name, pkg_manager = detect_system_info()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, groq_api_key=api_key)

# --- NEW: CONTEXT AWARENESS MODULE ---

def get_diagnostic_command(user_query):
    """
    Step 1: The Detective.
    Decides if we need to run a safe command to see what's going on.
    """
    detective_prompt = f"""
    You are a Linux Diagnostic Agent.
    User Query: "{user_query}"
    
    Do you need to run a read-only command to understand the system state before acting?
    - If YES: Output ONLY that command (e.g., 'df -h', 'ls -la', 'free -m', 'ip a').
    - If NO (it's a generic question): Output 'SKIP'.
    
    RULES:
    1. ONLY output safe, read-only commands. No 'rm', 'sudo', or installing.
    2. Keep it simple.
    """
    msgs = [SystemMessage(content=detective_prompt), HumanMessage(content="Analyze this request.")]
    response = llm.invoke(msgs).content.strip()
    
    if "SKIP" in response or "sudo" in response:
        return None
    return response

# -------------------------------------

def get_system_prompt(mode, context_output=""):
    """Generates the personality, now injecting real System Context!"""
    base = f"You are an expert SysAdmin for {distro_name} using {pkg_manager}."
    
    # Inject the "Vision"
    if context_output:
        base += f"\n\nCURRENT SYSTEM STATE (from diagnostic):\n{context_output}\n\nUse this info to tailor your command."

    if mode == "god":
        return base + " OUTPUT ONLY THE COMMAND. NO EXPLANATIONS."
    elif mode == "newbie":
        return base + " Explain briefly. WARN heavily about sudo."
    else: # Pro
        return base + f" Output ONLY the command. Use {pkg_manager}. If dangerous, output 'SAFE_MODE_ERROR'."

def generate_command(user_query, mode, context_output=""):
    msgs = [
        SystemMessage(content=get_system_prompt(mode, context_output)), 
        HumanMessage(content=user_query)
    ]
    return llm.invoke(msgs).content.strip()

def fix_command(bad_command, error_msg, mode):
    fix_prompt = f"The command '{bad_command}' failed: {error_msg}. Fix it for {distro_name}."
    msgs = [SystemMessage(content=get_system_prompt(mode)), HumanMessage(content=fix_prompt)]
    return llm.invoke(msgs).content.strip()

def execute_command(command, silent=False):
    """Runs command. If silent=True, doesn't print output to screen (used for diagnostics)."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        if not silent:
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(f"\n❌ Error:\n{result.stderr}")
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

# --- ENTRY POINT ---

def run():
    parser = argparse.ArgumentParser(description="OmniShell: AI Terminal Assistant")
    parser.add_argument("query", nargs="?", help="Optional: Run a command directly")
    parser.add_argument("--mode", choices=["newbie", "pro", "god"], default="pro", help="Safety level")
    args = parser.parse_args()

    print(f"\n🧠 OmniShell v3.0 (Context Aware) | Mode: \033[1;35m{args.mode.upper()}\033[0m")
    
    if args.query:
        process_request(args.query, args.mode)
        return

    print("Type 'exit' to quit.\n")
    while True:
        try:
            user_input = input("USER > ")
            if user_input.lower() in ["exit", "quit"]: break
            if not user_input.strip(): continue
            process_request(user_input, args.mode)
        except KeyboardInterrupt:
            break

def process_request(user_input, mode):
    print("Thinking...", end="\r")
    
    # 1. PHASE 1: DIAGNOSTICS (The Eyes)
    context_output = ""
    diagnostic_cmd = get_diagnostic_command(user_input)
    
    if diagnostic_cmd:
        print(f"👁️  Checking system: \033[1;30m{diagnostic_cmd}\033[0m")
        success, output = execute_command(diagnostic_cmd, silent=True)
        if success:
            context_output = output[:2000] # Limit context size
            # print(f"DEBUG: Found {len(context_output)} bytes of context.")

    # 2. PHASE 2: GENERATION (The Brain)
    cmd = generate_command(user_input, mode, context_output)
    print(" " * 40, end="\r") # Clear line

    if mode != "god" and "SAFE_MODE_ERROR" in cmd:
        print("🛡️  Blocked dangerous request.")
        return

    if mode == "god":
        print(f"🔥 GOD MODE executing: \033[1;31m{cmd}\033[0m")
        execute_command(cmd)
        return

    while True:
        print(f"🤖 SUGGESTION: \033[1;32m{cmd}\033[0m")
        if mode == "newbie": print("(Type 'why' to learn)")
            
        choice = input("[E]xecute, [X]plain, [S]kip? ").lower()

        if choice in ['x', 'why']:
            expl = llm.invoke([HumanMessage(content=f"Explain '{cmd}' simply. ")]).content
            print(f"\nℹ️  {expl}\n")
            continue
        
        elif choice in ['e', 'y', '']:
            success, output = execute_command(cmd)
            if not success:
                print("🩹 Auto-fixing...")
                cmd = fix_command(cmd, output, mode)
                continue
            break
        
        elif choice == 's':
            break

if __name__ == "__main__":
    run()