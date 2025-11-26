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
      template="""1. Navigate to Login to 'https://www.royalsundaram.in/MOPIS/Login.jsp', and then enter username and password, user name is {username} password is {password}, click on sign in after both username and password are entered
      2. From dashboard, click 'Rating Calculator' in side menu
      3. Select 'New Business' icon under 'Type of Policy' and choose 'Private Car passenger' in the list of options present below
      4. Click on 'Private Car' icon under the 'click tick done' title
      5. On the 'Car Insurance in a few steps' box, enter vehicle number MH02FR1294 and click on 'get started', note that there are 4 text boxes for the vehicle number input, add MH to first, 02 to the next one and so on
      6. Click Proceed on the popup that follows, do this for any popups that come up.
      7. On the Policy details page, scroll down to the 'Previous Insurance and Pre Inspection Details', and set yesterday's date under 'Previous Policy Expiry Date' (Today's date is {today_date}). Once the date is set, click 'next'.
      8. On The side menu that shows up, click on 'proceed'. Say yes to any popups that come up.
      9. On the vpc_comprehensive page, set distance to 'unlimited km', click on calculate / recalculate button, and then Click on the 'Freeze Quote Button, once it turns to blue.
      10. On the side menu that comes up, enter name 'ketan', last name: 'k', whatsapp number: '9999999999', and click on submit.
      11.⁠click on 'policy documents' dropdown, and choose 'print quote' option. The quote file should now be on a different tab. Download the quote and save it to a file called 'quote.pdf'""",
)

   # Populate with dummy values
   task = insurance_prompt_template.format(
      username="invictus_insurance", password="SundaramRoyal&323", today_date=datetime.now().strftime("%Y-%m-%d")
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
