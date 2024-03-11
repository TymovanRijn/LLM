import os
from openai import OpenAI

client = OpenAI(
    api_key= "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",	
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "Send_Email",
            "description": "Send an email to a user which needs to be specified",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The name of the receiver from the email",
                    },
                    "format": {
                        "type": "string",
                        "enum": ["Receiver", "Body of email"],
                        "description": "The temperature unit to use. Infer this from the users location.",
                    },
                },
                "required": ["Name of receiver", "Body of email"],
            },
        }
    }
]


messages = []
messages.append({"role": "system", "content": "Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous."})
messages.append({"role": "user", "content": "Send an email to Johny"})
chat_response = client.chat.completions.create(
        messages=messages,
        model="gpt-3.5-turbo",
        tools=tools,
    )
assistant_message = chat_response.choices[0].message
messages.append(assistant_message)
print(f"\n{assistant_message}\n")
messages.pop()


# messages.append({"role": "user", "content": "Send it to John"})
# chat_response = client.chat.completions.create(
#         messages=messages,
#         model="gpt-3.5-turbo",
#         tools=tools,
#     )
# assistant_message = chat_response.choices[0].message
# messages.append(assistant_message)
# print("\n---------------------------------------------\n")
# print(assistant_message)