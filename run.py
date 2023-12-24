from autogen import AssistantAgent, UserProxyAgent, config_list_from_json
import openai
import os
from dotenv import load_dotenv

load_dotenv()
client = openai.Client(api_key=os.environ['OPENAI_API_KEY'])

# Load LLM inference endpoints from an env variable or a file
# See https://microsoft.github.io/autogen/docs/FAQ#set-your-api-endpoints
# and OAI_CONFIG_LIST_sample.json
config_list = config_list_from_json(env_or_file="OAI_CONFIG_LIST", filter_dict={
        "model": ["gpt-4"],
    })
assistant = AssistantAgent("assistant", llm_config={"config_list": config_list})
user_proxy = UserProxyAgent("user_proxy", code_execution_config={"work_dir": "coding"})
user_proxy.initiate_chat(assistant, message="List what model you are. Also, plot a chart of NVDA and TESLA stock price change YTD.")
# This initiates an automated chat between the two agents to solve the task