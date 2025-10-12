from Agents.BaseAgent import BaseAgent

class GradStuAgent(BaseAgent):
    def context(self) -> str:
        return ""

    def role_description(self) -> str:
        return "a programmer with an annual salary of one million!"

    def example_command(self) -> str:
        return ""
