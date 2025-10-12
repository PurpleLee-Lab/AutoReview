from Agents.BaseAgent import BaseAgent

class GradStuAgent(BaseAgent):
    def context(self) -> str:
        return ""

    def role_description(self) -> str:
        return """
                You are the Graduate Student Agent responsible for writing a scientific literature review
                under the supervision of a Professor Agent.
              """

    def example_command(self) -> str:
        return ""
