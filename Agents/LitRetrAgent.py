from Agents.BaseAgent import BaseAgent
import os

class LitRetrAgent(BaseAgent):
    def context(self) -> str:
        return """
               """

    def role_description(self) -> str:
        return """
                You are the Literature Retrieval Agent responsible for performing accurate and comprehensive academic literature searches and downloading valuable papers.
               """

    def example_command(self) -> str:
        return ""
    


    def perceive_environment(self) -> dict[str, str]:
        result = {}

        # --- Existing literaturetime ---
        target_dir = os.path.join(self.workdir, "retrieve_result")
        os.makedirs(target_dir, exist_ok=True)

        file_names = [
            os.path.join(self.workdir, "retrieve_result", f)
            for f in os.listdir(target_dir)
            if os.path.isfile(os.path.join(target_dir, f))
        ]
        result["Existing literaturetime"] = ", ".join(file_names)

        # --- Requirements ---
        requirements_dir = os.path.join(self.workdir, "requirements")
        os.makedirs(requirements_dir, exist_ok=True)

        requirement_files = [
            os.path.join(self.workdir, "requirements", f)
            for f in os.listdir(requirements_dir)
            if os.path.isfile(os.path.join(requirements_dir, f))
        ]
        result["requirements"] = ", ".join(requirement_files)

        return result



