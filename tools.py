import arxiv
import time
import os
from pypdf import PdfReader
import ssl, certifi, urllib.request
from Agents.LitRetrAgent import LitRetrAgent
import json

def save_retrieval_request(enabled: bool, input_text: str) -> str:
    """
    Write the Literature Retrieval (LitRetr) configuration into 'workdir/config.json'.
    Example content:
    {
        "LitRetr": {
            "enabled": true,
            "input": "quantum computing review papers 2024"
        }
    }
    """
    try:
        save_dir = "workdir"
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, "config.json")

        config_data = {
            "LitRetr": {
                "enabled": enabled,
                "input": input_text
            }
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)

        return f"Retrieval request saved successfully: {filepath}"
    except Exception as e:
        return f"Retrieval request save failed: {e}"


# === Markdown Reader Tool ===
def read_review(filepath: str) -> str:
    """
    Reading review papers written by graduate student agents.
    Args:
        filepath: File path.
    Returns:
        Review content (up to MAX_LEN characters) or an error message (Markdown format).
    """
    MAX_LEN = 50000

    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content[:MAX_LEN]
    except Exception as e:
        return f"Markdown reading failed: {e}"
    
def read_comment(filepath: str) -> str:
    """
    Read comment files written in Markdown format.
    Args:
        filepath: Full path to the Markdown comment file.
    Returns:
        Comment content (up to MAX_LEN characters) or an error message.
    """
    MAX_LEN = 50000

    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content[:MAX_LEN]
    except Exception as e:
        return f"Comment reading failed: {e}"



# === PDF Reader Tool ===
def read_literature(filepath: str) -> str:
    """
    Read the papers downloaded by the literature search agent.
    Args:
        filepath: File path.
    Returns:
        Extracted text (up to MAX_LEN characters) or an error message.
    """
    MAX_LEN = 50000

    if not os.path.exists(filepath):
        return f"File not found: {filepath}"

    pdf_text = ""
    try:
        reader = PdfReader(filepath)
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:
                return f"FAILED to extract text at page {page_number}."
            pdf_text += f"--- Page {page_number} ---\n{text}\n"

        return pdf_text[:MAX_LEN]
    except Exception as e:
        return f"PDF reading failed: {e}"


# === Scoring Tool ===
def save_score(score: float) -> str:
    """
    Save a numeric score into '/workdir/score.md'.
    Args:
        score: Numeric score value to record.
    Returns:
        Status message.
    """
    try:
        os.makedirs("/workdir", exist_ok=True)
        filepath = "/workdir/score.md"

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# Score\n\n{score}\n")

        return f"Score {score} saved successfully to {filepath}"
    except Exception as e:
        return f"Score saving failed: {e}"


# === Markdown Saver Tool ===
def save_review(content: str, version: int) -> str:
    """
    Save the review paper as a Markdown (.md) file in workdir/comments.
    """
    try:
        save_dir = os.path.join("workdir", "reviews")
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, f"review(version{version}).md")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")

        return f"Markdown file saved successfully: {filepath}"
    except Exception as e:
        return f"Markdown save failed: {e}"


def save_comment(content: str, version: int) -> str:
    """
    Save comments as a Markdown (.md) file.
    """
    try:
        save_dir = os.path.join("workdir", "comments")
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, f"Comment(version{version}).md")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")

        return f"Comment saved successfully: {filepath}"
    except Exception as e:
        return f"Comment save failed: {e}"


# === Main ArxivSearch Tool Class ===
class ArxivSearch:
    def __init__(self):
        self.sch_engine = arxiv.Client()

    def _process_query(self, query: str) -> str:
        MAX_QUERY_LENGTH = 300
        if len(query) <= MAX_QUERY_LENGTH:
            return query

        words = query.split()
        processed_query = []
        current_length = 0
        for word in words:
            if current_length + len(word) + 1 <= MAX_QUERY_LENGTH:
                processed_query.append(word)
                current_length += len(word) + 1
            else:
                break
        return ' '.join(processed_query)

    def find_papers_by_str(self, query: str, N: int = 5) -> str:
        processed_query = self._process_query(query)
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                search = arxiv.Search(
                    query="abs:" + processed_query,
                    max_results=N,
                    sort_by=arxiv.SortCriterion.Relevance)

                paper_summaries = []
                for r in self.sch_engine.results(search):
                    paperid = r.pdf_url.split("/")[-1]
                    pubdate = str(r.published).split(" ")[0]
                    paper_sum = (
                        f"# {r.title}\n\n"
                        f"**Publication Date:** {pubdate}\n\n"
                        f"**arXiv ID:** {paperid}\n\n"
                        f"**Summary:**\n{r.summary}\n\n---\n"
                    )
                    paper_summaries.append(paper_sum)

                time.sleep(2.0)
                return "\n".join(paper_summaries)

            except Exception:
                retry_count += 1
                if retry_count < max_retries:
                    time.sleep(2 * retry_count)
                    continue
        return None

    def retrieve_full_paper(self, paper_id: str) -> str:
        try:
            paper = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))
            filepath = os.path.join("workdir", "retrieve_result", f"arxiv_{paper_id}.pdf")
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            ctx = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(paper.pdf_url, context=ctx) as response, open(filepath, "wb") as out_file:
                out_file.write(response.read())

            time.sleep(2.0)
            return filepath
        except Exception as e:
            return f"DOWNLOAD FAILED: {e}"


# === Instantiate the Search Engine ===
arxiv_toolkit = ArxivSearch()


# === Register All Tools ===
ALL_TOOLS = {
    "find_papers_by_str": {
        "meta": {
            "type": "function",
            "function": {
                "name": "find_papers_by_str",
                "description": "Search for related papers on arXiv given a query string.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Research topic or keywords to search for."},
                        "N": {"type": "integer", "description": "Number of results to return (default 5)."}
                    },
                    "required": ["query"]
                }
            }
        },
        "func": arxiv_toolkit.find_papers_by_str
    },

    "retrieve_full_paper": {
        "meta": {
            "type": "function",
            "function": {
                "name": "retrieve_full_paper",
                "description": "Download an arXiv paper by ID and return the local PDF file path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "paper_id": {"type": "string", "description": "arXiv paper ID, e.g. '2401.12345'."}
                    },
                    "required": ["paper_id"]
                }
            }
        },
        "func": arxiv_toolkit.retrieve_full_paper
    },

    "read_literature": {
        "meta": {
            "type": "function",
            "function": {
                "name": "read_literature",
                "description": "Extract text from a literature PDF file given its full path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "Full path to the PDF file."}
                    },
                    "required": ["filepath"]
                }
            }
        },
        "func": read_literature
    },

    "save_review": {
        "meta": {
            "type": "function",
            "function": {
                "name": "save_review",
                "description": "Save a review as a Markdown file in 'workdir/reviews/review(versionX).md'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Review content to save."},
                        "version": {"type": "integer", "description": "Version number for naming the file."}
                    },
                    "required": ["content", "version"]
                }
            }
        },
        "func": save_review
    },

    "read_review": {
        "meta": {
            "type": "function",
            "function": {
                "name": "read_review",
                "description": "Read content from a Markdown (.md) review file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "Full path to the Markdown file."}
                    },
                    "required": ["filepath"]
                }
            }
        },
        "func": read_review
    },

    "save_score": {
        "meta": {
            "type": "function",
            "function": {
                "name": "save_score",
                "description": "Save a numeric score into '/workdir/score.md'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "score": {
                            "type": "number",
                            "description": "Numeric score value to write into score.md"
                        }
                    },
                    "required": ["score"]
                }
            }
        },
        "func": save_score
    },

    "save_retrieval_request": {
        "meta": {
            "type": "function",
            "function": {
                "name": "save_retrieval_request",
                "description": "Save LitRetr agent configuration (enabled flag and retrieval request) into '/workdir/config.json'. "
                "When there are no relevant papers available or when a new literature retrieval is needed, you should call this tool and set 'enabled' to True. You should carefully consider whether set 'enabled' to True. "
                "You just need to wait for the LitRetr agent to complete its work.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "enabled": {
                            "type": "boolean",
                            "description": "Whether to enable the Literature Retrieval agent."
                        },
                        "input_text": {
                            "type": "string",
                            "description": "Input string to be passed to 'LitRetr.run()'."
                        }
                    },
                    "required": ["enabled", "input_text"]
                }
            }
        },
        "func": save_retrieval_request
    },
        "read_comment": {
        "meta": {
            "type": "function",
            "function": {
                "name": "read_comment",
                "description": "Read content from a Markdown (.md) comment file.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "Full path to the Markdown comment file."}
                    },
                    "required": ["filepath"]
                }
            }
        },
        "func": read_comment
    },
        "save_comment": {
        "meta": {
            "type": "function",
            "function": {
                "name": "save_comment",
                "description": "Save comments as a Markdown file in 'workdir/comments/Comment(versionX).md'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Comment content to save."},
                        "version": {"type": "integer", "description": "Version number for naming the file."}
                    },
                    "required": ["content", "version"]
                }
            }
        },
        "func": save_comment
    },



}


if __name__ == '__main__':
    print(ALL_TOOLS.keys())
