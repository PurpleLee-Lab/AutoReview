from AutoReview_workflow import AutoReview_workflow
import argparse
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('api_key')

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="AutoReview Workflow Runner")
    parser.add_argument('--topic', type=str, default='LLM-based Agent', help='Review topic name')
    parser.add_argument('--min_citations', type=int, default=0, help='Minimum number of citations for retrieved papers')
    parser.add_argument('--max_citations', type=int, default=5, help='Maximum number of citations for retrieved papers')
    parser.add_argument('--max_length', type=int, default=5000, help='Maximum word count of the paper abstract')
    parser.add_argument('--year_range', type=str, default="2020-2025", help='Year range for papers, e.g., "2020-2025"')
    parser.add_argument('--work_dir', type=str, default='./workdir', help='Working directory for saving outputs and logs')
    parser.add_argument('--human_feedback', type=bool, default=False, help='Is human feedback required?')
    parser.add_argument('--max_iter', type=int, default=5, help='max_iter')
    return parser.parse_args()


def build_input_string(args):
    """
    Build a single input string from command line arguments
    for the AutoReview workflow.
    """
    input_str = (
        f"Please write a literature review on the topic: '{args.topic}'. "
        f"Only include papers published between {args.year_range}. "
        f"Consider papers with citation counts between {args.min_citations} and {args.max_citations}. "
        f"Limit the paper abstract length to {args.max_length} words. "
    )
    return input_str

if __name__ == '__main__':
    args = parse_args()

    # Build input string for the workflow
    input_str = build_input_string(args)
    
    review = AutoReview_workflow(input_str, topic = args.topic, api_key = api_key, workdir = args.work_dir, max_iter = args.max_iter)

    # review.run()
    review.run()

