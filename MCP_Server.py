# mcp_server.py
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

# Adjust this import to where your parser lives.
# Example: if your parser is in main.py, use `from main import VectorDocParser, FunctionInfo, Parameter`
from main import VectorDocParser, FunctionInfo, Parameter


# -------------------------
# MCP server
# -------------------------
mcp = FastMCP("VectorDocExtractorServer")


# -------------------------
# Utilities
# -------------------------
def function_info_to_dict(fi: FunctionInfo) -> Dict[str, Any]:
    """Convert FunctionInfo dataclass to a JSON-serializable dict."""
    return {
        "function_name": fi.function_name,
        "valid_for": fi.valid_for,
        # If you split function vs method syntax in your FunctionInfo, adapt below
        "syntax_forms": list(fi.syntax_forms),
        "description": fi.description,
        "parameters": [{"name": p.name, "description": p.description} for p in fi.parameters],
        "return_values": list(fi.return_values),
        "example": fi.example,
    }


def _file_contains_function(md_path: Path, function_name: str) -> bool:
    """Case-insensitive quick check whether a file text contains the function name."""
    try:
        text = md_path.read_text(encoding="utf-8", errors="ignore")
        return function_name.lower() in text.lower()
    except Exception as e:
        return False


def _resolve_and_validate_docs_path(docs_path: str, allowed_root: Optional[str] = None) -> Path:
    """
    Resolve docs_path and optionally ensure it's inside an allowed_root.
    If allowed_root is None, no additional restriction is applied.
    """
    path = Path(docs_path).expanduser().resolve()
    if allowed_root:
        root = Path(allowed_root).expanduser().resolve()
        try:
            path.relative_to(root)
        except Exception:
            raise ValueError(f"docs_path {path} is outside allowed root {root}")
    return path


# -------------------------
# Core tool: search_capl_function_docs
# -------------------------
@mcp.tool(
    name="search_capl_function_docs",
    description="Parses Vector CAPL documentation Markdown files in the inputs/ directory and returns detailed function info (syntax, parameters, return values, and examples) as JSON."
)
def search_capl_function_docs(
    function_name: str,
    docs_path: str = "./inputs",
    max_results: int = 10,
    allowed_root: Optional[str] = None,
    parse_all_matches: bool = False
) -> Dict[str, Any]:
    """
    Locate and extract CAPL function documentation details from Vector markdown files.

    This tool searches recursively through a documentation directory for markdown files
    whose names or contents reference the given `function_name`. When a match is found,
    it parses the markdown content into structured components such as syntax forms,
    parameters, return values, description, and example code blocks.


    :param function_name: Name (or snippet) of the function to search for (case-insensitive).
    :param docs_path: Directory containing .md files to search.
    :param max_results: Maximum number of files to return (search only).
    :param allowed_root: Optional absolute path that docs_path must be inside for safety.
    :param parse_all_matches: If True parse all found files; otherwise parse up to max_results.
    :return: Dict with search & parse results.
    """
    try:
        base = _resolve_and_validate_docs_path(docs_path, allowed_root=allowed_root)
    except Exception as e:
        msg = f"docs_path validation failed: {e}"
        return {"found": False, "error": msg}

    if not base.exists() or not base.is_dir():
        msg = f"docs_path does not exist or is not a directory: {base}"
        return {"found": False, "error": msg}

    # Search for candidate files quickly with a text scan
    candidates: List[Path] = []
    for md_file in base.glob("**/*.md"):
        if _file_contains_function(md_file, function_name):
            candidates.append(md_file)
            if len(candidates) >= max_results:
                break

    if not candidates:
        return {"found": False, "files": [], "message": f"No match found for '{function_name}'"}

    parser = VectorDocParser()
    parsed_results: List[Dict[str, Any]] = []
    unparsed_files: List[str] = []

    to_parse = candidates if parse_all_matches else candidates[:max_results]

    for p in to_parse:
        try:
            fi = parser.parse_file(str(p))
            if fi:
                parsed_results.append({"file": str(p), "parsed": function_info_to_dict(fi)})
            else:
                # Some files may not parse (e.g., selectors, indexes). Keep a note.
                unparsed_files.append(str(p))
        except Exception as e:
            unparsed_files.append(str(p))

    response: Dict[str, Any] = {
        "found": True,
        "query": function_name,
        "base_path": str(base),
        "files": [str(p) for p in candidates],
        "parsed_count": len(parsed_results),
        "parsed": parsed_results,
        "unparsed_files": unparsed_files,
    }

    return response


# -------------------------
# Optional helper tool: parse_file (single file)
# -------------------------
@mcp.tool(    name="parse_md_file",
    description="Parses a single Vector CAPL documentation Markdown file and returns detailed function info (syntax, parameters, return values, and examples) as JSON."
)
def parse_md_file(file_path: str) -> Dict[str, Any]:
    """
    Parse a single markdown file and return the FunctionInfo as dict (or error).
    """
    p = Path(file_path).expanduser().resolve()
    if not p.exists() or not p.is_file():
        msg = f"File not found: {p}"
        return {"error": msg}

    parser = VectorDocParser()
    try:
        fi = parser.parse_file(str(p))
        if fi:
            return {"file": str(p), "parsed": function_info_to_dict(fi)}
        else:
            return {"file": str(p), "parsed": None, "message": "No structured info extracted"}
    except Exception as e:
        return {"file": str(p), "error": str(e)}


# -------------------------
# Run MCP server
# -------------------------
if __name__ == "__main__":
    print("Starting MCP server...")
    mcp.run()
