from AutoReview_workflow import AutoReview_workflow
import argparse
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('api_key')

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="AutoReview Workflow Runner")
    parser.add_argument('--topic', type=str, default='LLM-base Agent', help='Review topic name')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    review = AutoReview_workflow(topic=args.topic, api_key = api_key)
    review.test_Agent()
