from browser_use import Agent, Browser, ChatBrowserUse
from browser_use.llm.azure.chat import ChatAzureOpenAI
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
import asyncio
import sys
import os
from datetime import datetime
from collections import Counter
load_dotenv()


# ============================================================================
# STUCK DETECTION LOGIC
# ============================================================================

def is_agent_stuck(agent: Agent, repeat_threshold: int = 4, step_threshold: int = 4) -> bool:
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
            print(f"    [Stuck Detection] Action '{action_sig}' repeated {count} times")
            return True
    
    # Check 2: Same goal for too many steps
    recent_goals = []
    for item in history[-step_threshold:]:
        if item.model_output and hasattr(item.model_output, 'current_state'):
            current_state = item.model_output.current_state
            if hasattr(current_state, 'next_goal') and current_state.next_goal:
                recent_goals.append(current_state.next_goal)
    
    if len(recent_goals) >= step_threshold and len(set(recent_goals)) == 1:
        print(f"    [Stuck Detection] Same goal for {step_threshold} consecutive steps: '{recent_goals[0][:50]}...'")
        return True
    
    return False


async def on_step_end_with_stuck_detection(agent: Agent):
    """
    Callback that runs after each step to check if agent is stuck.
    If stuck, pauses execution and waits for manual intervention.
    """
    if is_agent_stuck(agent):
        print("\n" + "="*60)
        print("⚠️  AGENT APPEARS STUCK (repeating actions or no progress)")
        print("="*60)
        print("Browser is open for manual intervention.")
        print("Please fix the issue in the browser window, then press Enter to continue...")
        print("="*60 + "\n")
        
        # Block until user presses Enter
        input("Press Enter after fixing the issue to resume agent execution...")
        
        print("\n▶️  Resuming agent execution...\n")


# Create LangChain PromptTemplate for Royal Sundaram insurance quote task
# Universal variables: username, password, today_date
# Record-specific variables: registration_number, first_name, last_name, whatsapp_number
insurance_prompt_template = PromptTemplate(
   input_variables=["username", "password", "today_date", "registration_number", "first_name", "last_name", "whatsapp_number"],
   template="""1. Navigate to Login to 'https://www.royalsundaram.in/MOPIS/Login.jsp', and then enter username and password, user name is {username} password is {password}, click on sign in after both username and password are entered. 
   2. From dashboard, click 'Rating Calculator' in side menu. Wait for 10 seconds.
   3. Select 'New Business' icon under 'Type of Policy' and choose 'Private Car passenger' in the list of options present below. Wait for 10 seconds.
   4. Click on 'Private Car' icon under the 'click tick done' title. Wait for 10 seconds.
   5. On the 'Car Insurance in a few steps' box, enter vehicle number {registration_number} and click on 'get started', note that there are 4 text boxes for the vehicle number input, add MH to first, 02 to the next one and so on. Once done, wait for 10 seconds.
   6. Click Proceed on the popup that follows, do this for any popups that come up.
   7. On the Policy details page, scroll down to the 'Previous Insurance and Pre Inspection Details', and set yesterday's date under 'Previous Policy Expiry Date' (Today's date is {today_date}). Note that you will need to interact with a date-picker for the same. Verify if your date has been added properly once you've chosen the date, and the date-picker element has vanished. Only Once the date is set, click 'next'. Wait for 10 seconds.
   8. On The side menu that shows up, click on 'proceed'. Say yes to any popups that come up.
   9. On the vpc_comprehensive page, set distance to 'unlimited km', wait for 10 seconds.
   10. click on calculate / recalculate button. Wait for 10 seconds. 
   11. click on the 'Freeze Quote Button, once it turns to blue.
   12. On the side menu that comes up, enter name '{first_name}', last name: '{last_name}', whatsapp number: '{whatsapp_number}', and click on submit. wait for 10 seconds.
   13.⁠click on 'policy documents' dropdown, and choose 'print quote' option. The quote file should now be on a different tab. 
   14. Find the download button at the top right of the window, click on it.'""",
)

# Universal values (shared across all records)
UNIVERSAL_VALUES = {
   "username": "invictus_insurance",
   "password": "SundaramRoyal&323",
   "today_date": datetime.now().strftime("%Y-%m-%d"),
}

# Record-specific values - each dict should contain keys matching the prompt template placeholders
RECORDS = [
   {"registration_number": "MH02FR1294", "first_name": "ketan", "last_name": "k", "whatsapp_number": "9999999999"}
   # {"registration_number": "MH02FR1294", "first_name": "john", "last_name": "d", "whatsapp_number": "8888888888"},
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
   
   # Create isolated browser instance for this task
   # keep_alive=True ensures browser stays open during manual intervention pauses
   browser = Browser(
      executable_path="/Users/ketankunkalikar/Library/Caches/ms-playwright/chromium-1194/chrome-mac/Chromium.app/Contents/MacOS/Chromium",
      user_data_dir=f"./browser_profiles_{profile_id}",
      profile_directory="Default",
      keep_alive=True,  # Keep browser open during stuck detection pauses
   )

   agent = Agent(
      task=task, browser=browser, llm=ChatBrowserUse(), use_vision=True, flash_mode=True
   )
   
   # Run agent with stuck detection callback
   history = await agent.run(on_step_end=on_step_end_with_stuck_detection)
   
   # Use registration_number as identifier if available, otherwise use profile_id
   identifier = record.get("registration_number", f"record_{profile_id}")
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
