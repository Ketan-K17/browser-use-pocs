from browser_use import Agent, Browser, ChatOpenAI, Tools, ActionResult
from browser_use.llm.azure.chat import ChatAzureOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import asyncio
import sys
import os

load_dotenv()


async def main():
    llm = ChatAzureOpenAI(
      model=os.getenv("AZURE_OPENAI_CHAT_MODEL"),
      api_key=os.getenv("AZURE_OPENAI_CHAT_KEY"),
      azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT"),
      azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
      api_version=os.getenv("AZURE_API_VERSION", "2024-12-01-preview"),
      temperature=0.0,
   )
    browser = Browser()
    await browser.start()

    # 1. Actor: Precise navigation and element interactions
    page = await browser.new_page("https://github.com/login")
    email_input = await page.must_get_element_by_prompt("username", llm=llm)
    await email_input.fill("your-username", clear=True)

    # 2. Agent: AI-driven complex tasks
    agent = Agent(browser=browser, llm=llm)
    await agent.run("Complete login and navigate to my repositories")

    await browser.stop()

if __name__ == "__main__":
    asyncio.run(main())