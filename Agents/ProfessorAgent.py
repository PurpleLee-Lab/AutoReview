from Agents.BaseAgent import BaseAgent
import os

class ProfessorAgent(BaseAgent):
    def context(self) -> str:
        return ""

    def role_description(self) -> str:
        return """
                You are the Professor Agent responsible for reviewing and guiding the Graduate Student Agent’s
                literature review writing process.
                Give a brief response.
                """

    def example_command(self) -> str:
        return ""

    def perceive_environment(self) -> dict[str, str]:
        result = {}

        # --- Existing review version ---
        review_dir = os.path.join(self.workdir, "reviews")
        os.makedirs(review_dir, exist_ok=True)

        review_files = [
            os.path.join(self.workdir, "reviews", f)
            for f in os.listdir(review_dir)
            if os.path.isfile(os.path.join(review_dir, f))
        ]
        result["Existing review version"] = ", ".join(review_files)

        # --- Existing comments ---
        comments_dir = os.path.join(self.workdir, "comments")
        os.makedirs(comments_dir, exist_ok=True)

        comment_files = [
            os.path.join(self.workdir, "comments", f)
            for f in os.listdir(comments_dir)
            if os.path.isfile(os.path.join(comments_dir, f))
        ]
        result["Existing comments"] = ", ".join(comment_files)
        # print(result)

        return result
