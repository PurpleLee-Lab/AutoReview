from Agents.BaseAgent import BaseAgent

class GradStuAgent(BaseAgent):
    def context(self) -> str:
        return ""

    def role_description(self) -> str:
        return "a superman! I can do anything!"

    def example_command(self) -> str:
        return ""
