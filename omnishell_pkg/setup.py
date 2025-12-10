from setuptools import setup, find_packages

setup(
    name="omnishell",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "langchain-groq",
        "langchain-core",
        "python-dotenv",
        "distro"
    ],
    entry_points={
        'console_scripts': [
            # This maps the command 'omni' to the main function in main.py
            'omni=omnishell.main:run', 
        ],
    },
    author="Your Name",
    description="A distro-agnostic AI terminal assistant for Linux",
)