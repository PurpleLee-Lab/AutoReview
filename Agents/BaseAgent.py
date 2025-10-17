import json
from openai import OpenAI

class BaseAgent:
    def __init__(self, tools, api_key):
        self.tools_meta_map = tools
        self.tools_meta = [v["meta"] for v in tools.values()]
        self.tool_func_map = {k: v["func"] for k, v in tools.items()}

        # 历史对话缓存 [(role, content), ...]
        self.history = []
        self.max_hist_len = 15

        base_url = "https://api.deepseek.com"
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def _build_prompt(self, user_input: str) -> list:
        """构建对话上下文（包含角色说明、历史记录、当前输入）"""
        context_text = self.context()
        role_desc_text = self.role_description()
        example_cmd_text = self.example_command()

        # 基础系统提示
        system_msg = {
            "role": "system",
            "content": (
                f"You are {role_desc_text}\n\n"
                f"Always act and respond consistently with this role, "
                f"even when the user asks about your identity.\n\n"
                f"### Context:\n{context_text}\n\n"
                f"### Example Command:\n{example_cmd_text}\n\n"
            ),
        }

        # 保留最近 max_hist_len 轮历史记录（裁剪旧的）
        trimmed_history = self.history[-self.max_hist_len:]

        # 组装消息序列
        messages = [system_msg] + [
            {"role": role, "content": content} for role, content in trimmed_history
        ]
        messages.append({"role": "user", "content": user_input})

        return messages

    def run(self, user_input: str) -> str:
        """执行对话推理 + 工具调用 + 记忆更新"""
        # 构建 prompt（含历史）
        messages = self._build_prompt(user_input)

        # 向模型请求响应
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

        # 将用户输入加入历史
        self.history.append(("user", user_input))

        # 工具调用情况
        if tool_calls:
            tool_call = tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)
            tool_func = self.tool_func_map.get(tool_name)

            # 调用工具
            tool_result = (
                tool_func(**tool_args) if tool_func else f"Unknown tool: {tool_name}"
            )

            # 模型获取工具执行结果后的跟进
            follow_up = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages
                + [
                    {"role": "assistant", "tool_calls": [tool_call]},
                    {"role": "tool", "tool_call_id": tool_call.id, "content": tool_result},
                ],
                stream=False,
            )
            final_content = follow_up.choices[0].message.content

            # 将AI回复加入历史
            self.history.append(("assistant", final_content))
            # 控制历史长度
            self.history = self.history[-self.max_hist_len:]

            return final_content

        # 没有工具调用时，直接使用AI回复
        self.history.append(("assistant", content))
        self.history = self.history[-self.max_hist_len:]
        return content

    # 以下需在子类实现
    def context(self) -> str:
        raise NotImplementedError("Subclasses should implement this method.")

    def role_description(self) -> str:
        raise NotImplementedError("Subclasses should implement this method.")

    def example_command(self) -> str:
        raise NotImplementedError("Subclasses should implement this method.")
