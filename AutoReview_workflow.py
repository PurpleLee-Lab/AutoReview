from Agents.ProfessorAgent import ProfessorAgent
from Agents.LitRetrAgent import LitRetrAgent
from Agents.GradStuAgent import GradStuAgent
from tools import ALL_TOOLS
import os

class AutoReview_workflow:
    def __init__(self, topic = None, api_key = None, workdir = None):
        self.topic = topic

        self.workdir = workdir

        self.api_key = api_key
        tools_map_GradStu = { "extract_pdf_text"     : ALL_TOOLS["extract_pdf_text"],
                               "save_as_markdown"    : ALL_TOOLS["save_as_markdown"],
                               "read_md"             : ALL_TOOLS["read_md"]
                               }

        tools_map_LitRetr = { "find_papers_by_str"   : ALL_TOOLS["find_papers_by_str"],
                              "retrieve_full_paper"  : ALL_TOOLS["retrieve_full_paper"] }
        
        tools_map_Professor = { "read_md"     : ALL_TOOLS["read_md"] }

        self.GradStu = GradStuAgent(tools = tools_map_GradStu, api_key = self.api_key, workdir = self.workdir)
        self.LitRetr = LitRetrAgent(tools = tools_map_LitRetr, api_key = self.api_key, workdir = self.workdir)
        self.Professor = ProfessorAgent(tools = tools_map_Professor, api_key = self.api_key, workdir = self.workdir)

    # 拟定
    def run(self):
        print(f"{self.topic}, Start Review!")

        # 文献检索 Agent 检索论文
        print("LitRetrAgent: Searching papers...")
        self.LitRetr.run()

        # 研究生撰写初稿综述
        print("GradStuAgent: Writing draft review...")
        self.GradStu.run()

        # 导师评审并提供修改建议
        print("ProfessorAgent: Reviewing draft...")
        self.Professor.run()

    # def perceive_environment(self) -> dict[str, list[str]]:
    #     """感知当前工作环境（自动创建文件夹 + 读取内容）"""
    #     environment_state: dict[str, list[str]] = {}

    #     # 定义目录
    #     retrieve_dir = os.path.join(self.workdir, "retieve_result")
    #     review_dir = os.path.join(self.workdir, "review")
    #     comments_dir = os.path.join(self.workdir, "comments")

    #     # 确保文件夹存在（自动创建）
    #     for d in [retrieve_dir, review_dir, comments_dir]:
    #         os.makedirs(d, exist_ok=True)

    #     # 定义安全读取函数
    #     def safe_listdir(path, only_dirs=False):
    #         items = os.listdir(path)
    #         full_paths = [os.path.join(path, item) for item in items]
    #         if only_dirs:
    #             return [item for item, full in zip(items, full_paths) if os.path.isdir(full)]
    #         else:
    #             return [item for item, full in zip(items, full_paths) if os.path.isfile(full)]

    #     # 收集环境状态
    #     environment_state["Existing literaturetime"] = safe_listdir(retrieve_dir, only_dirs=False)
    #     environment_state["Current score"] = safe_listdir(review_dir, only_dirs=True)
    #     environment_state["Professor's comments"] = safe_listdir(comments_dir, only_dirs=True)

    #     return environment_state


    def test_Agent(self):
        # response = self.GradStu.run("阅读pdf中的论文，并用中文总结，并保存为markdown文件。")
        # print("\n--- Response of GradStu ---")
        # print(response)
        # response = self.LitRetr.run("Find a review paper on agent and download it.")
        # print("\n--- Response of LitRetr ---")
        # print(response)
        # response = self.Professor.run("Review the review paper and provide revision suggestions, and score it between 0-10 points.")
        # print("\n--- Response of Professor ---")
        # print(response)
        env = self.LitRetr.perceive_environment()
        print("LitReir_environment:")
        for key, value in env.items():
            print(f"  {key}: {value}")

        env = self.GradStu.perceive_environment()
        print("GradStu_environment:")
        for key, value in env.items():
            print(f"  {key}: {value}")

        env = self.Professor.perceive_environment()
        print("Professor_environment:")
        for key, value in env.items():
            print(f"  {key}: {value}")


    

if __name__ == '__main__':
    pass
    # print(AutoReview_workflow.perceive_environment())

        
