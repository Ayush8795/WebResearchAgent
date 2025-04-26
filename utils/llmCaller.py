from groq import Groq
import os
from dotenv import load_dotenv
import requests
import json
from openai import AzureOpenAI

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")

#gpt creds

gpt_api_key = os.getenv("GPT4V_KEY")
endpoint = os.getenv("GPT4V_ENDPOINT")

version = os.getenv('API_VERSION')


def callGPT(prompt, max_tokens = 4096):
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
        


# def messages():
#     query= ["what is light","who discovered it"]
#     sr=''
#     for qr in query:
#         print(stream_chat(qr))
#         time.sleep(5)


messages = callLLama("What is the capital of France?")
print(messages)