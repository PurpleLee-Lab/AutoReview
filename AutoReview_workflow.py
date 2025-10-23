from Agents.ProfessorAgent import ProfessorAgent
from Agents.LitRetrAgent import LitRetrAgent
from Agents.GradStuAgent import GradStuAgent
from tools import ALL_TOOLS

class AutoReview_workflow:
    def __init__(self, topic, api_key):
        self.topic = topic

        self.api_key = api_key
        tools_map_GradStu = { "extract_pdf_text"     : ALL_TOOLS["extract_pdf_text"],
                               "save_as_markdown"    : ALL_TOOLS["save_as_markdown"],
                               "litretr_run"         : ALL_TOOLS["litretr_run"]}

        # tools_map_LitRetr = { "find_papers_by_str"      : ALL_TOOLS["find_papers_by_str"],
        #                       "retrieve_full_paper"     : ALL_TOOLS["retrieve_full_paper"] }
        
        tools_map_Professor = { "read_review_md": ALL_TOOLS["read_review_md"] }

        self.GradStu = GradStuAgent(tools = tools_map_GradStu, api_key = self.api_key)
        # self.LitRetr = LitRetrAgent(tools = tools_map_LitRetr, api_key = self.api_key)
        self.Professor = ProfessorAgent(tools = tools_map_Professor, api_key = self.api_key)

    # 拟定
    def run(self):
        print(f"{self.topic}, Start Review!")

        # 1. 研究生提出文献检索需求
        print("GradStuAgent: Requesting literature search...")
        paper_queries = self.GradStu.generate_search_queries(self.topic)

        # 2. 文献检索 Agent 检索论文
        print("LitRetrAgent: Searching papers...")
        papers = []
        for query in paper_queries:
            search_results = self.LitRetr.find_papers_by_str(query)
            for paper_meta in search_results:
                full_paper = self.LitRetr.retrieve_full_paper(paper_meta['id'])
                papers.append(full_paper)

        print(f"Found {len(papers)} papers.")

        # 3. 研究生撰写初稿综述
        print("GradStuAgent: Writing draft review...")
        draft_review = self.GradStu.write_review(papers, self.topic)

        # 4. 导师评审并提供修改建议
        print("ProfessorAgent: Reviewing draft...")
        feedback = self.Professor.review_and_suggest(draft_review)

        # 5. 研究生根据反馈迭代优化
        print("GradStuAgent: Refining draft based on feedback...")
        final_review = self.GradStu.refine_review(draft_review, feedback)

        print("Review completed!")
        return final_review

    def test_Agent(self):
        response = self.GradStu.run("阅读pdf中的论文，并用中文总结，并保存为markdown文件。")
        print("\n--- Response of GradStu ---")
        print(response)
        # response = self.LitRetr.run("Find a review paper on agent and download it.")
        # print("\n--- Response of LitRetr ---")
        # print(response)
        # response = self.Professor.run("Review the review paper and provide revision suggestions, and score it between 0-10 points.")
        # print("\n--- Response of Professor ---")
        # print(response)
        
