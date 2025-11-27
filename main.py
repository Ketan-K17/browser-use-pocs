from browser_use import Agent, Browser, ChatBrowserUse
from browser_use.llm.azure.chat import ChatAzureOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import asyncio
import sys
import os
from datetime import datetime
load_dotenv()


async def main():
   # Create LangChain PromptTemplate for Royal Sundaram insurance quote task
   insurance_prompt_template = PromptTemplate(
      input_variables=["username", "password"],
      template="""Goal: Fetching Vehicle Premium value.
      1. Log into https://smartzone.reliancegeneral.co.in/Login/IMDLogin . Fill username: {username}, and password: {password}. Also fill the CAPTCHA value based on the image you see above it. Once done, click on the circular 'LOGIN' button. You may retry the captcha by clicking on 'refresh symbol' if you fail.
      2. Once the dashboard loads, hover on the green, round button with a car logo, labelled 'motor'. It is present on the blue dashboard with similar buttons next to it. In the dropdown labelled 'quote', select 'private car'.
      3. Under the menu named 'vehicle details', enter MH02FR1294 as registration number (spaced as MH 02 FR 1294), click on the 'fetch vehicle details' button.
      4. Once details have been automatically filled, enter the following fields down the menu - 
         i. select February under 'select month' dropdown in Manufacturing year and month.
      ii. select 'short term' under 'Period Of Previous Policy'.
      iii. The 'Previous Policy Start Date' is 25/02/2021, and the 'Previous Policy End Date' is 15/04/2021
      iv. select 'yes' for 'Vehicle Ownership Transfer done in previous year policy'.
      v. check on 'NCB Eligibility Criteria' (this opens more elements)
      vi. 'claim on last policy' : no
      vii. 'last year ncb': 35%.
      5. Click 'get coverage details' and wait for the next form to load.
      5. In the menu named 'Cover Details', scroll down and click on 'calculate premium'. Fetch the value that comes up.
      """,
)

   # Populate with dummy values
   task = insurance_prompt_template.format(
      username="Quotation", password="c@40k2kj"
   )

   # llm = AzureChatOpenAI(
   #     azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
   #     api_key=os.getenv("AZURE_OPENAI_CHAT_KEY"),
   #     azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT"),
   #     model=os.getenv("AZURE_OPENAI_CHAT_MODEL"),
   #     api_version=os.getenv("AZURE_API_VERSION"),
   #     temperature=os.getenv("LLM_TEMPERATURE"),
   # )

   #  llm = ChatAzureOpenAI(
   #      model=os.getenv("AZURE_OPENAI_CHAT_MODEL"),
   #      api_key=os.getenv("AZURE_OPENAI_CHAT_KEY"),
   #      azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT"),
   #      azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
   #      api_version=os.getenv("AZURE_API_VERSION", "2024-12-01-preview"),
   #      temperature=0.0,
   #  )

   #  print(llm)

   # llm = ChatOpenAI(
   #     model="gpt-4.1",
   #     api_key=os.getenv("OPENAI_API_KEY"),
   #     temperature=0.0,
   # )
   browser = Browser(
      executable_path="/Users/ketankunkalikar/Library/Caches/ms-playwright/chromium-1194/chrome-mac/Chromium.app/Contents/MacOS/Chromium",
      user_data_dir="./browser_profiles",
      profile_directory="Default",
      keep_alive=True,
   )

   agent = Agent(
      task=task, browser=browser, llm=ChatBrowserUse(), use_vision=True, use_thinking=True
   )
   history = await agent.run()
   print(history.final_result())


if __name__ == "__main__":
    asyncio.run(main())
