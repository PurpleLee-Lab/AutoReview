from Agents.BaseAgent import BaseAgent
import os

class GradStuAgent(BaseAgent):
    def context(self) -> str:
        return """
                Your workflow includes:
                1. Accept the research topic and key questions provided by the user.
                2. Call the Literature Retrieval Agent to fetch the most relevant papers for this topic.
                3. Read the retrieved abstracts and extract the main ideas, methods, and research trends.
                4. Write a comprehensive draft of the literature review that includes:
                - Introduction
                - Related Work / Current Progress
                - Comparative Analysis and Emerging Trends
                - Discussion and Future Directions
                5. Submit the draft to the Advisor Agent for feedback.
                6. Refine and improve the draft iteratively based on the advisor’s comments.

                Writing guidelines:
                - Maintain a formal academic tone.
                - Ensure logical structure and coherence across sections.
                - Avoid subjective or conversational expressions.
                - Use consistent citation formatting (e.g., “[Author, Year]”).
                - Go beyond summarization—include critical analysis and synthesis of findings.

                If the retrieved literature is insufficient or off-topic, proactively request additional or more specific papers from the Literature Retrieval Agent.
               """

    def role_description(self) -> str:
        return """
                You are the Graduate Research Agent responsible for writing an academic literature review.  
                Your mission is to coordinate with other agents to produce a high-quality, well-structured review.
              """

    def example_command(self) -> str:
        return ""
    
    def perceive_environment(self) -> dict[str, str]:
        result = {}

        # --- Existing literaturetime ---
        retrieve_dir = os.path.join(self.workdir, "retrieve_result")
        os.makedirs(retrieve_dir, exist_ok=True)
        
        retrieve_files = [
            os.path.join(self.workdir, "retrieve_result", f)
            for f in os.listdir(retrieve_dir)
            if os.path.isfile(os.path.join(retrieve_dir, f))
        ]
        result["Existing literaturetime"] = ", ".join(retrieve_files)

        # --- Existing review version ---
        review_dir = os.path.join(self.workdir, "review")
        os.makedirs(review_dir, exist_ok=True)

        review_files = [
            os.path.join(self.workdir, "review", f)
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

        # --- Score ---
        score_path = os.path.join(self.workdir, "score.md")
        if os.path.isfile(score_path):
            with open(score_path, "r", encoding="utf-8") as f:
                score_content = f.read().strip()
        else:
            score_content = ""  # 文件不存在则为空

        result["score"] = score_content

        return result


    
