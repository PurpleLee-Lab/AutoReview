import json
from openai import OpenAI

class BaseAgent:
    def __init__(self, tools, api_key):
        self.tools_meta_map = tools
        self.tools_meta = [v["meta"] for v in tools.values()]
        self.tool_func_map = {k: v["func"] for k, v in tools.items()}
        base_url = "https://api.deepseek.com"
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def run(self, user_input: str) -> str:
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ],
            tools=self.tools_meta,
            tool_choice="auto",
            stream=False
        )

        ai_message = response.choices[0].message
        content = ai_message.content
        tool_calls = ai_message.tool_calls

        if tool_calls:
            tool_call = tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            tool_func = self.tool_func_map.get(tool_name)

            tool_result = tool_func(**tool_args) if tool_func else f"Unknown tool: {tool_name}"

            follow_up = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input},
                    {"role": "assistant", "tool_calls": [tool_call]},
                    {"role": "tool", "tool_call_id": tool_call.id, "content": tool_result},
                ],
                stream=False
            )
            return follow_up.choices[0].message.content

        return content