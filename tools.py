import arxiv
import time
import os
from pypdf import PdfReader


# === Base example tool (kept for demo) ===
def tool_1() -> str:
    return "This is a tool"


# === PDF Reader Tool ===
def extract_pdf_text(filepath: str, MAX_LEN: int = 50000) -> str:
    """
    Extract text from a local PDF file.
    Returns up to MAX_LEN characters of extracted text.
    """
    pdf_text = ""
    try:
        reader = PdfReader(filepath)
        for page_number, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text()
            except Exception:
                return f"FAILED to extract text at page {page_number}."

            pdf_text += f"--- Page {page_number} ---\n{text}\n"

        return pdf_text[:MAX_LEN]
    except Exception as e:
        return f"PDF reading failed: {e}"
    finally:
        if os.path.exists(filepath):
            os.remove(filepath)
        time.sleep(1.0)


# === Main ArxivSearch Tool Class ===
class ArxivSearch:
    def __init__(self):
        self.sch_engine = arxiv.Client()

    def _process_query(self, query: str) -> str:
        """Process query string to fit within MAX_QUERY_LENGTH."""
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
        """
        Search for papers on arXiv by a query string.
        Returns formatted paper summaries including title, summary, publication date, and arXiv ID.
        """
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
                        f"Title: {r.title}\n"
                        f"Summary: {r.summary}\n"
                        f"Publication Date: {pubdate}\n"
                        f"arXiv paper ID: {paperid}\n"
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
        """
        Download an arXiv paper by ID to a local PDF file.
        Returns the local file path (to be used by extract_pdf_text).
        """
        try:
            paper = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))
            filepath = f"arxiv_{paper_id}.pdf"
            paper.download_pdf(filename=filepath)
            time.sleep(2.0)
            return filepath
        except Exception as e:
            return f"DOWNLOAD FAILED: {e}"


# === Instantiate the Search Engine ===
arxiv_toolkit = ArxivSearch()


# === Register All Tools ===
ALL_TOOLS = {
    "tool_1": {
        "meta": {
            "type": "function",
            "function": {
                "name": "tool_1",
                "description": "A simple demo tool that returns a string.",
                "parameters": {"type": "object", "properties": {}}
            }
        },
        "func": tool_1
    },

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
                "description": "Extract text from a local PDF file path.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {"type": "string", "description": "Path to the local PDF file."},
                        "MAX_LEN": {"type": "integer", "description": "Maximum number of characters to return (default 50000)."}
                    },
                    "required": ["filepath"]
                }
            }
        },
        "func": extract_pdf_text
    }
}
