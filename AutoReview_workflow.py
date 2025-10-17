from Agents.ProfessorAgent import ProfessorAgent
from Agents.LitRetrAgent import LitRetrAgent
from Agents.GradStuAgent import GradStuAgent
from tools import ALL_TOOLS

class AutoReview_workflow:
    def __init__(self, topic, api_key):
        self.topic = topic

        self.api_key = api_key
        tools_map_GradStu = { "retrieve_full_paper"     : ALL_TOOLS["retrieve_full_paper"] }

        tools_map_LitRetr = { "find_papers_by_str"      : ALL_TOOLS["find_papers_by_str"],
                              "retrieve_full_paper"     : ALL_TOOLS["retrieve_full_paper"] }
        
        tools_map_Professor = { "tool_1": ALL_TOOLS["tool_1"] }

        self.GradStu = GradStuAgent(tools = tools_map_GradStu, api_key = self.api_key)
        self.LitRetr = LitRetrAgent(tools = tools_map_LitRetr, api_key = self.api_key)
        self.Professor = ProfessorAgent(tools = tools_map_Professor, api_key = self.api_key)

    def run(self):
        print(f"{self.topic}, Start Review!")

    def test_Agent(self):
        # response = self.GradStu.run("What tools do you have?")
        # print("\n--- Response of GradStu ---")
        # print(response)
        response = self.LitRetr.run("Find a review paper on agent.")
        print("\n--- Response of LitRetr ---")
        print(response)
        # response = self.Professor.run("What tools do you have?")
        # print("\n--- Response of Professor ---")
        # print(response)
        
