from Agents.BaseAgent import BaseAgent

class ProfessorAgent(BaseAgent):
    def context(self) -> str:
        return ""

    def role_description(self) -> str:
        return """
                You are the Professor Agent responsible for reviewing and guiding the Graduate Student Agent’s
                literature review writing process.
                """

    def example_command(self) -> str:
        return ""

    