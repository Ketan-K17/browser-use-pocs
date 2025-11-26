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

   # browser = Browser(
   #    executable_path='/Users/ketankunkalikar/Library/Caches/ms-playwright/chromium-1194/chrome-mac/Chromium.app/Contents/MacOS/Chromium',
   #    user_data_dir='./browser_profiles',
   #    profile_directory='Default',
   # )
   browser = Browser()
   await browser.start()

   # 1. Actor: Precise navigation and element interactions
   page = await browser.new_page("https://www.royalsundaram.in/MOPIS/Login.jsp")
   username_input = await page.must_get_element_by_prompt("Get the User Name input field", llm=llm)
   await username_input.fill("invictus_insurance")

   await browser.stop()


if __name__ == "__main__":
    asyncio.run(main())

