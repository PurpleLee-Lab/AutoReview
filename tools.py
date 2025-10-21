import arxiv
import time
import os
from pypdf import PdfReader
import ssl, certifi, urllib.request


# === Markdown Reader Tool ===
def read_review_md(filename: str = None) -> str:
    """
    Read text from a Markdown (.md) file under the fixed 'review' folder.
    - If filename is None, return all Markdown file names under the folder.
    - If filename is given, read and return up to MAX_LEN characters of its content.
    """
    folder = "review"   # 固定文件夹名
    MAX_LEN = 50000     # 最大读取长度

    # 检查文件夹是否存在
    if not os.path.exists(folder):
        return f"Folder '{folder}' not found."

    # 若未指定文件名，则列出所有 Markdown 文件
    if filename is None:
        files = [f for f in os.listdir(folder) if f.lower().endswith(".md")]
        if not files:
            return f"No Markdown (.md) files found in '{folder}'."
        return "Available Markdown files:\n" + "\n".join(files)

    # 拼接路径
    filepath = os.path.join(folder, filename)

    if not os.path.exists(filepath):
        return f"File '{filename}' not found in folder '{folder}'."

    # 读取文件内容
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content[:MAX_LEN]
    except Exception as e:
        return f"Markdown reading failed: {e}"

# === PDF Reader Tool ===
def extract_pdf_text(filename: str = None) -> str:
    """
    Extract text from a PDF file under a fixed folder.
    - If filename is None, return all PDF file names under the folder.
    - If filename is given, read and return up to MAX_LEN characters of its text.
    """
    folder = "retrieve_result"  # 固定文件夹名
    MAX_LEN = 50000             # 固定最大长度

    # 如果文件夹不存在
    if not os.path.exists(folder):
        return f"Folder '{folder}' not found."

    # 若未指定文件名，则返回该文件夹下所有 PDF 文件
    if filename is None:
        files = [f for f in os.listdir(folder) if f.lower().endswith(".pdf")]
        if not files:
            return f"No PDF files found in '{folder}'."
        return "Available PDF files:\n" + "\n".join(files)

    # 拼接文件路径
    filepath = os.path.join(folder, filename)

    if not os.path.exists(filepath):
        return f"File '{filename}' not found in folder '{folder}'."

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
    Save given text content as a Markdown (.md) file.
    File is saved to 'review/review(versionX).md' (folder created automatically).
    Example:
        version=1 -> review/review(version1).md
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
        """
        Download an arXiv paper by ID to a local PDF file with verified SSL context.
        """
        try:
            paper = next(arxiv.Client().results(arxiv.Search(id_list=[paper_id])))
            filepath = f"retrieve_result/arxiv_{paper_id}.pdf"
            os.makedirs("retrieve_result", exist_ok=True)

            # 创建安全的 HTTPS 证书上下文
            ctx = ssl.create_default_context(cafile=certifi.where())

            # 使用 urlopen 下载（替代 urlretrieve）
            with urllib.request.urlopen(paper.pdf_url, context=ctx) as response, open(filepath, "wb") as out_file:
                out_file.write(response.read())

            time.sleep(2.0)
            return filepath
        except Exception as e:
            return f"DOWNLOAD FAILED: {e}"


# === Instantiate the Search Engine ===
arxiv_toolkit = ArxivSearch()


if __name__ == '__main__':
    result = arxiv_toolkit.find_papers_by_str("federated learning")
    save_msg = save_as_markdown(result)
    print(save_msg)


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
                "description": (
                    "Read text from a PDF file in the fixed folder 'retrieve_result'. "
                    "If filename is None, list all PDF files in that folder."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": ["string", "null"],
                            "description": "Name of the PDF file to read. If None, list all available PDFs."
                        }
                    },
                    "required": []
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
                        "content": {
                            "type": "string",
                            "description": "Text content to save as Markdown."
                        },
                        "version": {
                            "type": "integer",
                            "description": "Version number used to name the file, e.g., version=1 -> 'review(version1).md'."
                        }
                    },
                    "required": ["content", "version"]
                }
            }
        },
        "func": save_as_markdown
    },

    "read_review_md": {
        "meta": {
            "type": "function",
            "function": {
                "name": "read_review_md",
                "description": (
                    "Read text from a Markdown (.md) file in the fixed folder 'review'. "
                    "If filename is None, list all Markdown files in that folder."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filename": {
                            "type": ["string", "null"],
                            "description": "Name of the Markdown file to read. If None, list all available .md files."
                        }
                    },
                    "required": []
                }
            }
        },
        "func": read_review_md
    }

}
