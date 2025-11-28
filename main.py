from browser_use import Agent, Browser, ChatBrowserUse
from browser_use.llm.azure.chat import ChatAzureOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import asyncio
import sys
import os
from datetime import datetime
from collections import Counter
from aioconsole import ainput

load_dotenv()


# ============================================================================
# STUCK DETECTION LOGIC
# ============================================================================

def is_agent_stuck(agent: Agent, identifier: str, repeat_threshold: int = 4, step_threshold: int = 4) -> bool:
    """
    Detect if agent is stuck based on action patterns.
    
    Args:
        agent: The browser_use Agent instance
        repeat_threshold: Number of times same action must repeat to be considered stuck
        step_threshold: Number of recent steps to analyze
    
    Returns:
        True if agent appears stuck, False otherwise
    """
    history = agent.history.history
    if len(history) < repeat_threshold:
        return False
    
    # Check 1: Repeated similar actions in recent steps
    recent_actions = []
    for item in history[-step_threshold:]:
        if item.model_output and item.model_output.action:
            for action in item.model_output.action:
                action_data = action.model_dump(exclude_unset=True)
                action_name = next(iter(action_data.keys()), None)
                if action_name:
                    # Create a signature (action_name + key params like index or coordinates)
                    params = action_data.get(action_name, {})
                    if isinstance(params, dict):
                        sig = f"{action_name}:{params.get('index', params.get('coordinate_x', ''))}"
                    else:
                        sig = action_name
                    recent_actions.append(sig)
    
    # If same action signature appears repeat_threshold+ times in last step_threshold steps
    action_counts = Counter(recent_actions)
    for action_sig, count in action_counts.items():
        if count >= repeat_threshold:
            print(f"    [{identifier}] [Stuck Detection] Action '{action_sig}' repeated {count} times")
            return True
    
    # Check 2: Same goal for too many steps
    recent_goals = []
    for item in history[-step_threshold:]:
        if item.model_output and hasattr(item.model_output, 'current_state'):
            current_state = item.model_output.current_state
            if hasattr(current_state, 'next_goal') and current_state.next_goal:
                recent_goals.append(current_state.next_goal)
    
    if len(recent_goals) >= step_threshold and len(set(recent_goals)) == 1:
        print(f"    [{identifier}] [Stuck Detection] Same goal for {step_threshold} consecutive steps")
        return True
    
    return False


async def on_step_end_with_stuck_detection(agent: Agent, identifier: str):
    """
    Callback that runs after each step to check if agent is stuck.
    If stuck, pauses execution and waits for manual intervention.
    """
    if is_agent_stuck(agent, identifier):
        print("\n" + "="*60)
        print(f"⚠️  [{identifier}] AGENT APPEARS STUCK")
        print("="*60)
        print(f"Profile: {identifier} - Browser is open for manual intervention.")
        print("Please fix the issue in the browser window, then press Enter to continue...")
        print("="*60 + "\n")
        
        # Use async input to avoid blocking other agents
        await ainput("Press Enter after fixing the issue to resume agent execution...")
        
        print("\n▶️  Resuming agent execution...\n")


# Create LangChain PromptTemplate for Royal Sundaram insurance quote task
# Universal variables: username, password, today_date
# Record-specific variables: registration_number, first_name, last_name, whatsapp_number
insurance_prompt_template = PromptTemplate(
   input_variables=["username", "password", "registration_number"],
   template="""Goal: Fetching Vehicle Premium value.
     1. Log into https://smartzone.reliancegeneral.co.in/Login/IMDLogin . Fill username: {username}, and password: {password}. Also fill the CAPTCHA value based on the image you see above it. Once done, click on the circular 'LOGIN' button. You may retry the captcha by clicking on 'refresh symbol' if you fail.
     2. Once the dashboard loads, hover on the green, round button with a car logo, labelled 'motor'. It is present on the blue dashboard with similar buttons next to it. In the dropdown labelled 'quote', select 'private car'.
     3. Under the menu named 'vehicle details', enter {registration_number} as registration number (spaced as MH 02 FR 1294), click on the 'fetch vehicle details' button.
     4. Once details have been automatically filled, enter the following fields down the menu -
        i. select February under 'select month' dropdown in Manufacturing year and month.
     ii. select 'short term' under 'Period Of Previous Policy'.
     iii. The 'Previous Policy Start Date' is 25/02/2021, and the 'Previous Policy End Date' is 15/04/2021
     iv. select 'yes' for 'Vehicle Ownership Transfer done in previous year policy'.
     v. check on 'NCB Eligibility Criteria' (this opens more elements)
     vi. 'claim on last policy' : no
     vii. 'last year ncb': 35%.
     5. Click 'get coverage details' and wait for the next form to load.
     5. In the menu named 'Cover Details', scroll down and click on 'calculate premium'. Fetch the value that comes up.""",
)

# Universal values (shared across all records)
UNIVERSAL_VALUES = {
   "username": "Quotation",
   "password": "c@40k2kj",
   "today_date": datetime.now().strftime("%Y-%m-%d"),
}

# Record-specific values - each dict should contain keys matching the prompt template placeholders
RECORDS = [
   {"registration_number": "MH02FR1294", "first_name": "ketan", "last_name": "k", "whatsapp_number": "9999999999", "cred": os.getenv("BU_API_KEY1")},
   {"registration_number": "MH02FR1294", "first_name": "john", "last_name": "d", "whatsapp_number": "8888888888", "cred": os.getenv("BU_API_KEY2")},
   # Add more records as needed
]


async def fetch_quote(record: dict, profile_id: int, prompt_template: PromptTemplate):
   """
   Fetch insurance quote for a single record.
   
   Args:
       record: Dictionary containing record-specific values (must match prompt template placeholders)
       profile_id: Unique ID for browser profile isolation
       prompt_template: The PromptTemplate to use for generating the task
   
   Returns:
       Tuple of (record identifier, result)
   """
   # Merge universal values with record-specific values
   all_values = {**UNIVERSAL_VALUES, **record}
   
   # Format the task using the prompt template
   task = prompt_template.format(**all_values)

   identifier = f"{record.get('first_name', 'unknown')}_{record.get('registration_number', f'record_{profile_id}')}"
   
   # Create isolated browser instance for this task
   # keep_alive=True ensures browser stays open during manual intervention pauses
   browser = Browser(
      executable_path="/Users/ketankunkalikar/Library/Caches/ms-playwright/chromium-1194/chrome-mac/Chromium.app/Contents/MacOS/Chromium",
      user_data_dir=f"./browser_profiles_{profile_id}",
      profile_directory="Default",
      keep_alive=True,  # Keep browser open during stuck detection pauses
   )

   agent = Agent(
      task=task, browser=browser, llm=ChatBrowserUse(api_key=record.get("cred")), use_vision=True, use_thinking=True
   )

   # Create a closure that includes the identifier
   async def on_step_end_callback(agent: Agent):
      await on_step_end_with_stuck_detection(agent, identifier)
   
   # Run agent with stuck detection callback
   history = await agent.run(on_step_end=on_step_end_callback)
   
   return identifier, history.final_result()


async def main():
   # Create tasks for all records
   tasks = [
      fetch_quote(record, profile_id, insurance_prompt_template)
      for profile_id, record in enumerate(RECORDS)
   ]
   
   # Run all tasks concurrently
   results = await asyncio.gather(*tasks, return_exceptions=True)
   
   # Print results
   print("\n" + "="*50)
   print("RESULTS")
   print("="*50)
   for identifier, result in results:
      if isinstance(result, Exception):
         print(f"\n{identifier}: ERROR - {result}")
      else:
         print(f"\n{identifier}: {result}")


if __name__ == "__main__":
   asyncio.run(main())
