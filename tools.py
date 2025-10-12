import arxiv
import time
import os
from pypdf import PdfReader

# === Base example tool (kept for demo) ===
def tool_1() -> str:
    return "This is a tool"


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

    def find_papers_by_str(self, query: str, N: int = 20) -> str:
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

    def retrieve_full_paper_text(self, paper_id: str, MAX_LEN: int = 50000) -> str:
        """
        Download and extract text from an arXiv paper by ID.
        Returns up to MAX_LEN characters of extracted text.
        """
        pdf_text = ""
        try:
            paper = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))
            paper.download_pdf(filename="downloaded-paper.pdf")
            reader = PdfReader('downloaded-paper.pdf')

            for page_number, page in enumerate(reader.pages, start=1):
                try:
                    text = page.extract_text()
                except Exception:
                    os.remove("downloaded-paper.pdf")
                    time.sleep(2.0)
                    return "EXTRACTION FAILED"

                pdf_text += f"--- Page {page_number} ---\n{text}\n"

            os.remove("downloaded-paper.pdf")
            time.sleep(2.0)
            return pdf_text[:MAX_LEN]
        except Exception:
            return "FAILED TO RETRIEVE PAPER TEXT"


# === Instantiate the Search Engine ===
arxiv_toolkit = ArxivSearch()

# === Register All Tools ===
ALL_TOOLS = {
    "tool_1": {
        "meta": {
            "type": "function",
            "function": {
                "name": "tool_1",
                "description": "A simple tool that returns a string.",
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
                        "N": {"type": "integer", "description": "Number of results to return (default 20)."}
                    },
                    "required": ["query"]
                }
            }
        },
        "func": arxiv_toolkit.find_papers_by_str
    },

    "retrieve_full_paper_text": {
        "meta": {
            "type": "function",
            "function": {
                "name": "retrieve_full_paper_text",
                "description": "Download and extract full text from an arXiv paper given its ID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "paper_id": {"type": "string", "description": "arXiv paper ID, e.g. '2401.12345'."},
                        "MAX_LEN": {"type": "integer", "description": "Maximum number of characters to return (default 50000)."}
                    },
                    "required": ["paper_id"]
                }
            }
        },
        "func": arxiv_toolkit.retrieve_full_paper_text
    }
}
