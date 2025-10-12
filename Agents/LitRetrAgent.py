from Agents.BaseAgent import BaseAgent

class LitRetrAgent(BaseAgent):
    def context(self) -> str:
        return ""

    def role_description(self) -> str:
        return """
                You are the Literature Retrieval Agent responsible for performing accurate and comprehensive
                academic literature searches.
               """

    def example_command(self) -> str:
        return ""