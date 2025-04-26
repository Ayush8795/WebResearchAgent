from groq import Groq
import os
from dotenv import load_dotenv
import requests
import json
from openai import AzureOpenAI
import tiktoken

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

#gpt creds

gpt_api_key = os.getenv("GPT4V_KEY")
endpoint = os.getenv("GPT4V_ENDPOINT")

version = os.getenv('API_VERSION')

def checkTokenLength(messages):
    text = str(messages)
    tokenizer = tiktoken.get_encoding("cl100k_base")  # Default tokenizer for most OpenAI models
    tokens = tokenizer.encode(text)
    
    return tokens


def _callGPT(prompt, max_tokens = 4096):
    client = AzureOpenAI(azure_endpoint = endpoint, api_key = gpt_api_key, api_version = version)
    messages = [
            {
                "role": "user",
                "content": [
                {
                    "type": "text",
                    "text": prompt
                }
                ]
            }
            ]
    
    output = client.chat.completions.create(
        model = "gpt4onew",
        messages = messages,
        max_tokens = max_tokens
        
      )
    response = output.choices[0].message.content
    return response


def callGPT(prompt, max_tokens = 4096):
    tokens = checkTokenLength(prompt)
    
    if len(tokens) > 127999:
        while len(tokens) > 127999:
            hlf_len = len(prompt) // 2
            prompt = prompt[ : hlf_len]
            tokens = checkTokenLength(prompt)
        
        return _callGPT(prompt, max_tokens)
    
    return _callGPT(prompt, max_tokens)


def callDeepSeek(prompt):
    print("using deepseek")
    response = requests.post(
    
        url="https://openrouter.ai/api/v1/chat/completions",
        
        headers={
            "Authorization": f"Bearer {deepseek_api_key}",
            "Content-Type": "application/json",
        },

        data=json.dumps({
            "model": "deepseek/deepseek-r1:free",
            "messages": [
            {
                "role": "user",
                "content": prompt
            }
            ],
            
        })
    )
    print(response.content)
    return response.json().get("choices")[0].get("message").get("content") if response.status_code == 200 else None


def callLLama(prompt):
    return callGPT(prompt)
    client = Groq(
        api_key = api_key,
    )
    try:
        messages = [
            {"role": "user", "content": prompt},
            {"role": "system", "content": "You are a helpful assistant."}
        ]

        completion = client.chat.completions.create(
            model = "llama-3.3-70b-versatile",
            messages = messages,
            temperature = 1,
            max_tokens = 4096,
            top_p = 1,
            stream = False,
            stop = None,
        )

        return completion.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None
        
#returning GPT call as Llama was throwing Rate Limit error (Free tier model)