from Agents.ProfessorAgent import ProfessorAgent
from Agents.LitRetrAgent import LitRetrAgent
from Agents.GradStuAgent import GradStuAgent
from tools import ALL_TOOLS

class AutoReview_workflow:
    def __init__(self, topic, api_key):
        self.topic = topic

        self.api_key = api_key
        tools_map_GradStu = { "tool_1": ALL_TOOLS["tool_1"] }
        tools_map_LitRetr = { "tool_1": ALL_TOOLS["tool_1"] }
        tools_map_Professor = { "tool_1": ALL_TOOLS["tool_1"] }
        self.GradStu = GradStuAgent(tools = tools_map_GradStu, api_key = self.api_key)
        self.LitRetr = LitRetrAgent(tools = tools_map_LitRetr, api_key = self.api_key)
        self.Professor = ProfessorAgent(tools = tools_map_Professor, api_key = self.api_key)

    def run(self):
        print(f"{self.topic}, Start Review!")

    def test(self):
        pass
