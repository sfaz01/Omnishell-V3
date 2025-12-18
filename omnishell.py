import os
import sys
import platform
import subprocess
import logging
import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage


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

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ Error: GROQ_API_KEY is missing from .env")
    sys.exit(1)

# --- INTELLIGENCE MODULES ---

def detect_system_info():
    """Auto-detects the OS and Package Manager."""
    try:
        distro_id = distro.id()
        distro_name = distro.name(pretty=True)
        
        # Smart Mapping
        pkg_managers = {
            "arch": "pacman", "cachyos": "pacman", "manjaro": "pacman",
            "ubuntu": "apt", "debian": "apt", "kali": "apt",
            "fedora": "dnf", "centos": "yum", "opensuse": "zypper",
            "alpine": "apk"
        }
        
        pkg_mgr = pkg_managers.get(distro_id, "unknown")
        if "cachyos" in distro_name.lower():
            pkg_mgr = "pacman"
            
        return distro_name, pkg_mgr
    except:
        return "Generic Linux", "unknown"

distro_name, pkg_manager = detect_system_info()

# Initialize Brain
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.1, groq_api_key=api_key)

# The Core Personality
system_prompt_base = f"""
You are an expert SysAdmin for {distro_name} using {pkg_manager}.
Rules:
1. Output ONLY the command (no markdown).
2. Use {pkg_manager} for installs.
3. If dangerous, output 'SAFE_MODE_ERROR'.
4. If the user asks to "EXPLAIN", provide a 1-sentence breakdown of the command instead of the command itself.
"""

def get_ai_response(messages):
    """Generic wrapper to talk to Llama 3."""
    response = llm.invoke(messages)
    return response.content.strip()

def generate_command(user_query):
    """First-pass command generation."""
    msgs = [SystemMessage(content=system_prompt_base), HumanMessage(content=user_query)]
    return get_ai_response(msgs)

def fix_command(bad_command, error_msg):
    """The Self-Healing Loop."""
    fix_prompt = f"""
    The command '{bad_command}' failed with this error:
    {error_msg}
    
    Fix the command to work on {distro_name}.
    Output ONLY the fixed command.
    """
    msgs = [SystemMessage(content=system_prompt_base), HumanMessage(content=fix_prompt)]
    return get_ai_response(msgs)

def get_explanation(command):
    """Explains a command to the user."""
    explain_prompt = f"Explain exactly what this command does in simple terms: '{command}'"
    msgs = [SystemMessage(content="You are a helpful Linux tutor."), HumanMessage(content=explain_prompt)]
    return get_ai_response(msgs)

def execute_command(command):
    """Runs command and returns (Success_Bool, Output/Error)."""
    try:
        # Capture output so we can feed it back if it fails
        result = subprocess.run(
            command, 
            shell=True, 
            text=True, 
            capture_output=True
        )
        
        if result.returncode == 0:
            print(result.stdout)
            return True, result.stdout
        else:
            print(f"\n❌ Error Output:\n{result.stderr}")
            return False, result.stderr

    except Exception as e:
        return False, str(e)


if __name__ == "__main__":
    print(f"\n🧠 OmniShell v2.0 (Self-Healing Enabled)")
    print(f"🖥️  System: {distro_name} | Pkg: {pkg_manager}")
    print("Commands: 'exit' to quit, 'log' to see history.\n")

    while True:
        try:
            user_input = input("USER > ")
            if user_input.lower() in ["exit", "quit"]: break
            if not user_input.strip(): continue

            # 1. Generate Command
            print("Thinking...", end="\r")
            candidate_cmd = generate_command(user_input)
            print(" " * 20, end="\r")

            if "SAFE_MODE_ERROR" in candidate_cmd:
                print("🛡️  Blocked dangerous request.")
                continue

            # 2. User Review Loop
            while True:
                print(f"🤖 SUGGESTION: \033[1;32m{candidate_cmd}\033[0m")
                choice = input("[E]xecute, [X]plain, [S]kip? ").lower()

                if choice == 'x':
                    # Explain Mode
                    explanation = get_explanation(candidate_cmd)
                    print(f"\nℹ️  Analysis: {explanation}\n")
                    continue # Ask again after explaining
                
                elif choice == 'e' or choice == 'y' or choice == '':
                    # Execute Mode
                    logging.info(f"EXECUTING: {candidate_cmd}")
                    success, output = execute_command(candidate_cmd)
                    
                    if success:
                        logging.info("STATUS: SUCCESS")
                        print("✅ Done.")
                        break # Exit review loop
                    else:
                        logging.error(f"FAILED: {output}")
                        # 3. SELF-HEALING TRIGGER
                        print("\n🩹 Command failed. Attempting to auto-fix...")
                        candidate_cmd = fix_command(candidate_cmd, output)
                        print("💡 I have a new suggestion based on the error.")
                        # Loop continues with new candidate_cmd!
                        continue 

                elif choice == 's':
                    print("🚫 Skipped.")
                    break
                
        except KeyboardInterrupt:
            print("\n👋 Bye.")
            break