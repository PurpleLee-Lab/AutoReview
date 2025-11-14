from Agents.ProfessorAgent import ProfessorAgent
from Agents.LitRetrAgent import LitRetrAgent
from Agents.GradStuAgent import GradStuAgent
from tools import ALL_TOOLS
import os
import time
import json

class AutoReview_workflow:
    def __init__(self, input_str, topic = None, api_key = None, workdir = None, max_iter = None):
        self.topic = topic

        self.input = input_str

        self.workdir = workdir

        self.max_iter = max_iter

        self.api_key = api_key
        tools_map_GradStu = { "read_literature"          : ALL_TOOLS["read_literature"],
                               "save_review"             : ALL_TOOLS["save_review"],
                               "read_comment"            : ALL_TOOLS["read_comment"],
                               "save_retrieval_request"  : ALL_TOOLS["save_retrieval_request"],
                               }

        tools_map_LitRetr = { "find_papers_by_str"   : ALL_TOOLS["find_papers_by_str"],
                              "retrieve_full_paper"  : ALL_TOOLS["retrieve_full_paper"] }
        
        tools_map_Professor = { "save_review"            : ALL_TOOLS["save_review"],
                               "save_comment"    : ALL_TOOLS["save_comment"],
                               "save_score"          : ALL_TOOLS["save_score"] }

        self.GradStu = GradStuAgent(tools = tools_map_GradStu, api_key = self.api_key, workdir = self.workdir, topic = self.topic)
        self.LitRetr = LitRetrAgent(tools = tools_map_LitRetr, api_key = self.api_key, workdir = self.workdir, topic = self.topic)
        self.Professor = ProfessorAgent(tools = tools_map_Professor, api_key = self.api_key, workdir = self.workdir, topic = self.topic)

    # 拟定
    def run(self):
        print(f"{self.topic}, Start Review!\n")

        # self.GradStu.run(self.input)

        # 读取配置文件
        with open("workdir/config.json", "r", encoding="utf-8") as f:
            config = json.load(f)

        for i in range(1, self.max_iter + 1):
            litretr_enabled = config.get("LitRetr", {}).get("enabled", False)
            litretr_input = config.get("LitRetr", {}).get("input", "")
            print(f"===== Iteration {i} =====")

            print("GradStuAgent: Writing draft review...")
            self.GradStu.run()

            if litretr_enabled:
                print("LitRetrAgent: Searching papers...")
                self.LitRetr.run(litretr_input)
                config["LitRetr"]["enabled"] = False
            else:
                print("LitRetrAgent: Skipped (disabled in config).")

            print("ProfessorAgent: Reviewing draft...")
            self.Professor.run()

            score = self.read_score()
            print(f"[Iteration {i}] Current Score: {score}")

            if score > 90:
                print("🎯 Score > 90, Review Complete!")
                break

            time.sleep(1)

        else:
            print("Reached maximum iterations, stopping process.")


    def read_score(self):
        score_file = "workdir/score.md"
        """从score.md文件读取分数"""
        if not os.path.exists(score_file):
            return 0  # 如果文件不存在，默认分数为0
        try:
            with open(score_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return float(content)
        except ValueError:
            return 0  # 防止非数字内容导致异常


    def test_Agent(self):
        response = self.GradStu.run("What tools do you have available?")
        print("\n--- Response of GradStu ---")
        print(response)
        response = self.LitRetr.run("What tools do you have available?")
        print("\n--- Response of LitRetr ---")
        print(response)
        response = self.Professor.run("What tools do you have available?")
        print("\n--- Response of Professor ---")
        print(response)
        # env = self.LitRetr.perceive_environment()
        # print("LitReir_environment:")
        # for key, value in env.items():
        #     print(f"  {key}: {value}")

        # env = self.GradStu.perceive_environment()
        # print("GradStu_environment:")
        # for key, value in env.items():
        #     print(f"  {key}: {value}")

        # env = self.Professor.perceive_environment()
        # print("Professor_environment:")
        # for key, value in env.items():
        #     print(f"  {key}: {value}")


    

if __name__ == '__main__':
    pass
    # print(AutoReview_workflow.perceive_environment())

        
