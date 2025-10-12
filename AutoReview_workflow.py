import Agents.ProfessorAgent
import Agents.LitRetrAgent
import Agents.ProfessorAgent
from tools import ALL_TOOLS

class AutoReview_workflow:
    def __init__(self):
        tools_map_GradStu = { "tool_1": ALL_TOOLS["tool_1"] }
        tools_map_LitRetr = { "tool_1": ALL_TOOLS["tool_1"] }
        tools_map_Professor = { "tool_1": ALL_TOOLS["tool_1"] }
        self.GradStu = ProfessorAgent()
        self.LitRetr = LitRetrAgent()
        self.Professor = ProfessorAgent()