import json
from openai import OpenAI

class BaseAgent:
    def __init__(self, tools, api_key):
        self.tools_meta_map = tools
        self.tools_meta = [v["meta"] for v in tools.values()]
        self.tool_func_map = {k: v["func"] for k, v in tools.items()}
        base_url = "https://api.deepseek.com"
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def _build_prompt(self, user_input: str) -> list:
        context_text = self.context()
        role_desc_text = self.role_description()
        example_cmd_text = self.example_command()

        messages = [
            {
                "role": "system",
                "content": (
                    f"You are {role_desc_text}\n\n"
                    f"Always act and respond consistently with this role, "
                    f"even when the user asks about your identity.\n\n"
                    f"### Context:\n{context_text}\n\n"
                    f"### Example Command:\n{example_cmd_text}\n\n"
                    # f"Your task: interpret the user's request and take appropriate action."
                ),
            },
            {"role": "user", "content": user_input},
        ]
        return messages

    # ========== 核心调用逻辑 ==========
    def run(self, user_input: str) -> str:
        messages = self._build_prompt(user_input)

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=self.tools_meta,
            tool_choice="auto",
            stream=False,
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

            # 再次调用模型生成最终回复
            follow_up = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages
                + [
                    {"role": "assistant", "tool_calls": [tool_call]},
                    {"role": "tool", "tool_call_id": tool_call.id, "content": tool_result},
                ],
                stream=False,
            )
            return follow_up.choices[0].message.content

        return content

    def context(self) -> str:
        raise NotImplementedError("Subclasses should implement this method.")

    def role_description(self) -> str:
        raise NotImplementedError("Subclasses should implement this method.")

    def example_command(self) -> str:
        raise NotImplementedError("Subclasses should implement this method.")
