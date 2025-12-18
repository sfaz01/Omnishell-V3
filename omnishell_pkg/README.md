# 🐚 OmniShell

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Linux%20(Arch%2FCachyOS%2FDebian)-red?style=for-the-badge&logo=linux&logoColor=white)
![AI](https://img.shields.io/badge/AI-Groq%20Llama3-purple?style=for-the-badge&logo=openai&logoColor=white)
![Framework](https://img.shields.io/badge/Built%20With-LangChain-green?style=for-the-badge)

**OmniShell** is an intelligent, self-healing terminal assistant designed for Linux power users. It leverages the speed of Groq (Llama 3) to translate natural language(human language) into system specific commands which automatically detects your linux distribution (CachyOS, Arch, Ubuntu) and package manager and writes commands based on the information the user provides as a prompt.

## ✨ Features

* **🧠 Distro-Agnostic Intelligence:** Automatically detects if you are on CachyOS (pacman), Ubuntu (apt), or Fedora (dnf) and adapts commands accordingly.
* **🛡️ Safe Mode:** It analyzes commands that are being generated for potential system risks before suggesting them.
* **🩹 Self-Healing Loop:** If a command fails, OmniShell captures the error output, and after analyzingit suggests a fix automatically.
* **🌐 Web Interface:** Includes a Streamlit-based web dashboard for cloud deployment.
* **🗣️ Explanation Mode:** Don't just run code...understand it. OmniShell can explain complex one-liners in plain English.

## 🚀 Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/Omnishell.git](https://github.com/YOUR_USERNAME/Omnishell.git)
    cd Omnishell
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Linux/Mac
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up credentials:**
    Create a `.env` file in the root directory:
    ```bash
    GROQ_API_KEY=your_gsk_key_here
    ```

## 💻 Usage

### CLI Mode (Terminal)
Run the interactive shell directly in your terminal:
```bash
python omnishell.py