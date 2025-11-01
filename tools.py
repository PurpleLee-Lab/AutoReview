import arxiv
import time
import os
from pypdf import PdfReader
import ssl, certifi, urllib.request
from Agents.LitRetrAgent import LitRetrAgent


# === Markdown Reader Tool ===
def read_md(filepath: str) -> str:
    """
    Read text content from a Markdown (.md) file.
    Args:
        filepath: Full path to the Markdown file.
    Returns:
        File content (up to MAX_LEN characters) or an error message.
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


# === PDF Reader Tool ===
def extract_pdf_text(filepath: str) -> str:
    """
    Extract text content from a PDF file.
    Args:
        filepath: Full path to the PDF file.
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


# === Markdown Saver Tool ===
def save_as_markdown(content: str, version: int) -> str:
    """
    Save given text as a Markdown (.md) file.
    The file is saved to 'review/review(versionX).md'.
    """
    try:
        os.makedirs("review", exist_ok=True)
        filepath = os.path.join("review", f"review(version{version}).md")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")

        return f"Markdown file saved successfully: {filepath}"
    except Exception as e:
        return f"Markdown save failed: {e}"


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
            filepath = f"retrieve_result/arxiv_{paper_id}.pdf"
            os.makedirs("retrieve_result", exist_ok=True)

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

    "extract_pdf_text": {
        "meta": {
            "type": "function",
            "function": {
                "name": "extract_pdf_text",
                "description": "Extract text from a PDF file given its full path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "Full path to the PDF file."}
                    },
                    "required": ["filepath"]
                }
            }
        },
        "func": extract_pdf_text
    },

    "save_as_markdown": {
        "meta": {
            "type": "function",
            "function": {
                "name": "save_as_markdown",
                "description": "Save text content as a Markdown file in 'review/review(versionX).md'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {"type": "string", "description": "Text content to save as Markdown."},
                        "version": {"type": "integer", "description": "Version number for naming the file."}
                    },
                    "required": ["content", "version"]
                }
            }
        },
        "func": save_as_markdown
    },

    "read_md": {
        "meta": {
            "type": "function",
            "function": {
                "name": "read_md",
                "description": "Read text from a Markdown (.md) file given its full path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "Full path to the Markdown file."}
                    },
                    "required": ["filepath"]
                }
            }
        },
        "func": read_md
    }
}


if __name__ == '__main__':
    print(ALL_TOOLS.keys())
