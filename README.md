# Browser Automation PoC

A CLI tool that automates browser tasks using natural language prompts, powered by Browser-Use and Azure OpenAI.

## Setup

### 1. Install Dependencies

```bash
source mumbai_hacks_venv/bin/activate
pip install -r requirements.txt
uvx browser-use install
```

### 2. Configure Environment Variables

Create a `.env` file with your Azure OpenAI credentials:

```
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## Usage

```bash
python main.py "Your task description here"
```

### Examples

```bash
python main.py "Find the top post on Hacker News"
python main.py "Search for the latest AI news on Google"
python main.py "Go to github.com and find the trending Python repositories"
```

If no task is provided, it defaults to "Find the top post on Hacker News".

