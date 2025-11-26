from browser_use import Agent, Browser, ChatOpenAI, Tools, ActionResult
from browser_use.llm.azure.chat import ChatAzureOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import asyncio
import sys
import os

load_dotenv()

# Create tools registry
tools = Tools()

@tools.action('Login to Royal Sundaram portal with provided credentials')
async def login_to_portal(username: str, password: str, browser: Browser) -> ActionResult:
    """Navigate to login page, fill credentials, and sign in."""
    # Navigate to login page
    page = await browser.get_current_page()
    await page.goto('https://www.royalsundaram.in/MOPIS/Login.jsp')
    
    # Wait for page to load
    await page.wait_for_load_state('networkidle')
    await asyncio.sleep(2)
    
    # Fill username
    username_field = page.locator('input[name="userId"], input[id="userId"], input[type="text"]').first
    await username_field.fill(username)
    
    # Fill password
    password_field = page.locator('input[name="password"], input[id="password"], input[type="password"]').first
    await password_field.fill(password)
    
    # Click sign in button
    sign_in_button = page.locator('button:has-text("Sign In"), input[value="Sign In"], #btn').first
    await sign_in_button.click()
    
    # Wait for dashboard to load
    await page.wait_for_load_state('networkidle')
    await asyncio.sleep(3)
    
    return ActionResult(
        extracted_content="Successfully logged into Royal Sundaram portal",
        success=True
    )


async def main():
    # Create LangChain PromptTemplate for Royal Sundaram insurance quote task
    insurance_prompt_template = PromptTemplate(
        input_variables=["username", "password"],
        template="""**Objective:** Login to Royal Sundaram portal, fetch vehicle insurance quote, and generate PDF.

**Credentials:** Username: `{username}` | Password: `{password}`

**Important:** Always wait for pages to fully load before interacting. Handle any popups immediately before proceeding to next steps.

**Instructions:**

1. **Login:**
   * Navigate to `https://www.royalsundaram.in/MOPIS/Login.jsp`
   * Enter credentials and click **"Sign In"**
   * Wait for dashboard to fully load

2. **Navigation to Quote Tool:**
   * From dashboard, click **"Rating Calculator"** in side menu
   * Wait for page to load completely
   * Under "Type of Policy", the dropdown should show **"New Business"** selected
   * Below the dropdown, a list of vehicle types will be visible
   * Click on **"Private Car Passenger"** (exact text, check capitalization) from the list
   * Wait for the next page to load (may auto-fill login details)
   * On Policy Motor Dashboard, click **"Private Car"** icon

3. **Enter Vehicle Details:**
   * Enter registration number: **`MH 02 FR 1294`** in "Car Insurance in a few steps" box
   * Click **"Get Started"**
   * Wait for page to load
   * **Popup:** If "Vehicle already has active policy" appears, click **"Proceed"**

4. **Policy Details:**
   * Wait for form to load with auto-filled details
   * Scroll down to find **"Previous Policy Expiry Date"**
   * Set date to **one day before current date** (format: YYYY-MM-DD where current date is 2025-11-25)
   * Click **"Next"**
   * Wait for side menu to appear
   * In "Your personalized plans" side menu, click **"Proceed"**
   * **Handle Popups:**
     * If "Vehicle is Eligible for Smart Save Pro" appears, click **"OK"**
     * If disclaimer about informing insured appears, click **"Yes"**

5. **Freeze Quote:**
   * Wait for quote summary page showing "VPC_Comprehensive" to load
   * Scroll to bottom right of page
   * Click **"Freeze Quote"** button

6. **Customer Details:**
   * Wait for "Customer Details" form to appear
   * Fill form with exact values:
     * **First Name:** `ketan`
     * **Last Name:** `k`
     * **WhatsApp Quote:** Select `No`
     * **Mobile:** `9999999999`
   * Click **"Submit"**
   * Wait for redirect

7. **Download PDF:**
   * On "Quote / Policy Information" page, locate **"Policy Documents"** button/dropdown (top right area)
   * Click and select **"Print Quote"**
   * Verify PDF opens or downloads successfully"""
    )
    
    # Populate with dummy values
    task = insurance_prompt_template.format(
        username="invictus_insurance",
        password="SundaramRoyal&323"
    )
    
    # llm = AzureChatOpenAI(
    #     azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
    #     api_key=os.getenv("AZURE_OPENAI_CHAT_KEY"),
    #     azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT"),
    #     model=os.getenv("AZURE_OPENAI_CHAT_MODEL"),
    #     api_version=os.getenv("AZURE_API_VERSION"),
    #     temperature=os.getenv("LLM_TEMPERATURE"),
    # )

    llm = ChatAzureOpenAI(
        model=os.getenv("AZURE_OPENAI_CHAT_MODEL"),
        api_key=os.getenv("AZURE_OPENAI_CHAT_KEY"),
        azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        api_version=os.getenv("AZURE_API_VERSION", "2024-12-01-preview"),
        temperature=0.0,
    )

    # llm = ChatOpenAI(
    #     model="gpt-4.1",
    #     api_key=os.getenv("OPENAI_API_KEY"),
    #     temperature=0.0,
    # )
    browser = Browser(
        executable_path='/Users/ketankunkalikar/Library/Caches/ms-playwright/chromium-1194/chrome-mac/Chromium.app/Contents/MacOS/Chromium',
        user_data_dir='./browser_profiles',
        profile_directory='Default',
    )
    # note: to get the right browser profile up and running, you need to QUIT chrome, because otherwise the profile will be locked by the browser (the profile used last will open)
    
    agent = Agent(task=task, browser=browser, llm=llm, use_vision=True, use_thinking=True, tools=tools)
    history = await agent.run()
    print(history.final_result())


if __name__ == "__main__":
    asyncio.run(main())

