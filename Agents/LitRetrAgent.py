from Agents.BaseAgent import BaseAgent

class LitRetrAgent(BaseAgent):
    def __init__(self, tools):
        self.tools_meta_map = tools
        self.tools_meta = [v["meta"] for v in tools.values()]
        self.tool_func_map = {k: v["func"] for k, v in tools.items()}