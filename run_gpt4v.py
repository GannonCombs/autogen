import requests
import json
import os
import openai

from typing import Any, Callable, Dict, List, Optional, Tuple, Type, Union

import autogen
# from autogen import AssistantAgent, Agent, UserProxyAgent, ConversableAgent
from termcolor import colored
import random

from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent

from dotenv import load_dotenv

load_dotenv()
client = openai.Client(api_key=os.environ['OPENAI_API_KEY'])

config_list_4v = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4-vision-preview"],
    },
)


config_list_gpt4 = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        "model": ["gpt-4", "gpt-4-0314", "gpt4", "gpt-4-32k", "gpt-4-32k-0314", "gpt-4-32k-v0314"],
    },
)

gpt4_llm_config = {"config_list": config_list_gpt4, "cache_seed": 42}
[config.pop("api_type", None) for config in config_list_4v]

print("GPT-4 Vision Config:", config_list_4v)
print("GPT-4 Config:", config_list_gpt4)


image_agent = MultimodalConversableAgent(
    name="image-explainer",
    max_consecutive_auto_reply=10,
    llm_config={"config_list": config_list_4v, "temperature": 0.5, "max_tokens": 300}
)

user_proxy = autogen.UserProxyAgent(
    name="User_proxy",
    system_message="A human admin.",
    human_input_mode="NEVER", # Try between ALWAYS or NEVER
    max_consecutive_auto_reply=0
)

# Ask the question with an image
user_proxy.initiate_chat(image_agent, 
                         message="""List what model you are. Also, what's the breed of this dog? 
<img https://th.bing.com/th/id/R.422068ce8af4e15b0634fe2540adea7a?rik=y4OcXBE%2fqutDOw&pid=ImgRaw&r=0>.""")

user_proxy.send(message="""What is this breed? 
<img https://th.bing.com/th/id/OIP.29Mi2kJmcHHyQVGe_0NG7QHaEo?pid=ImgDet&rs=1>

Among the breeds, which one barks less?""", 
                recipient=image_agent)