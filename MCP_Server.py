# mcp_server.py
from pathlib import Path
from typing import Any, Dict, List, Optional
import logging

from fastmcp import FastMCP

# Core components from local modules
from vector_doc_parser import VectorDocParser, FunctionInfo, parse_directory
from minimal_semantic_search import MinimalCAPLSearch

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -------------------------
# MCP server Setup
# -------------------------
mcp = FastMCP("VectorDocExtractorServer")

# -------------------------
# Semantic Search Engine Setup
# -------------------------
search_engine = MinimalCAPLSearch(cache_dir=".cache")
index_built = False

def _build_index_if_needed(docs_path: str = "./inputs", force_rebuild: bool = False) -> Optional[str]:
    """
    Builds the search index from markdown files. Returns an error string on failure.
    """
    global index_built
    
    if index_built and not force_rebuild:
        return None

    # Check if cache is valid and loaded to avoid rebuilding
    if not force_rebuild and search_engine.vectors is not None:
        if not index_built:
            logger.info("✅ Search index was already loaded from cache.")
            index_built = True
        return None

    logger.info(f"🔧 Building search index (force_rebuild={force_rebuild})...")
    try:
        base_path = Path(docs_path).expanduser().resolve()
        if not base_path.is_dir():
            err = f"Documentation directory not found at: {base_path}"
            logger.error(err)
            return err

        parsed_docs = parse_directory(str(base_path))
        if not parsed_docs:
            logger.warning("No documents were parsed. The index will be empty, but this is not a failure.")
        
        search_engine.build_index(parsed_docs, force_rebuild=force_rebuild)
        index_built = True
        logger.info("✅ Search index built successfully.")
        return None

    except Exception as e:
        logger.error(f"❌ Failed to build search index: {e}", exc_info=True)
        index_built = False
        # Return a detailed error message for debugging
        return f"Failed to build search index: {type(e).__name__}: {e}"


# -------------------------
# Utilities
# -------------------------
def function_info_to_dict(fi: FunctionInfo) -> Dict[str, Any]:
    """Convert FunctionInfo dataclass to a JSON-serializable dict."""
    return {
        "function_name": fi.function_name,
        "valid_for": fi.valid_for,
        "syntax_forms": list(fi.syntax_forms),
        "description": fi.description,
        "parameters": [{"name": p.name, "description": p.description} for p in fi.parameters],
        "return_values": list(fi.return_values),
        "example": fi.example,
    }

# -------------------------
# Core Tool: Semantic Search
# -------------------------
@mcp.tool(
    name="semantic_search_capl_docs",
    description="Performs a semantic search on Vector CAPL documentation. Finds relevant functions and documentation snippets based on a natural language query."
)
def semantic_search_capl_docs(
    query: str,
    docs_path: str = "./inputs",
    top_k: int = 5,
    min_score: float = 0.1,
    force_rebuild_index: bool = False
) -> Dict[str, Any]:
    """
    Performs semantic search over CAPL documentation to find functions and snippets
    that are most relevant to the user's query.

    :param query: Natural language search query (e.g., "how to send a CAN message").
    :param docs_path: Directory containing .md files to search and index.
    :param top_k: The number of top matching chunks to return.
    :param min_score: The minimum relevance score for a result to be included.
    :param force_rebuild_index: If True, rebuilds the search index before searching.
    :return: A dictionary with search results, including top functions and relevant chunks.
    """
    build_error = _build_index_if_needed(docs_path, force_rebuild=force_rebuild_index)
    if build_error:
        return {"found": False, "error": build_error}

    if not index_built:
        return {"found": False, "error": "Search index is not available or failed to build (reason unknown)."}

    try:
        # Search for the most relevant chunks of documentation
        results = search_engine.search(query, top_k=top_k, min_score=min_score)

        if not results:
            return {"found": False, "results": [], "message": f"No relevant documentation found for '{query}'."}

        # Also, find the top function names related to the query
        top_functions = search_engine.search_functions(query, top_k=3)

        # Format results for clear output
        formatted_chunks = [
            {
                "function_name": chunk['function_name'],
                "type": chunk['type'],
                "text": chunk['text'],
                "score": score,
            }
            for chunk, score in results
        ]

        return {
            "found": True,
            "query": query,
            "top_functions": top_functions,
            "best_chunks": formatted_chunks,
        }
    except Exception as e:
        logger.error(f"Error during semantic search for query '{query}': {e}", exc_info=True)
        return {"found": False, "error": f"An error occurred during search: {e}"}


# -------------------------
# Helper Tool: Get Full Function Context
# -------------------------
@mcp.tool(
    name="get_capl_function_details",
    description="Retrieves the complete documentation for a specific CAPL function by its name."
)
def get_capl_function_details(function_name: str, docs_path: str = "./inputs") -> Dict[str, Any]:
    """
    Retrieves all available documentation details for a given CAPL function name.

    :param function_name: The exact name of the CAPL function.
    :param docs_path: The directory where the documentation is located.
    :return: A dictionary containing the full documentation for the function.
    """
    build_error = _build_index_if_needed(docs_path)
    if build_error:
        return {"found": False, "error": build_error}

    if not index_built:
        return {"found": False, "error": "Documentation index is not available."}
        
    # Use the search engine's helper to get all data for a function
    context = search_engine.get_function_context(function_name)

    if not context.get('description') and not context.get('syntax_forms'):
        return {"found": False, "message": f"No details found for function: {function_name}"}

    return {"found": True, "function_details": context}


# -------------------------
# Optional helper tool: parse_file (single file)
# -------------------------
@mcp.tool(
    name="parse_md_file",
    description="Parses a single Vector CAPL documentation Markdown file and returns detailed function info as JSON. This is a low-level tool."
)
def parse_md_file(file_path: str) -> Dict[str, Any]:
    """
    Parse a single markdown file and return the FunctionInfo as dict (or error).
    """
    p = Path(file_path).expanduser().resolve()
    if not p.exists() or not p.is_file():
        return {"error": f"File not found: {p}"}

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
    logger.info("Starting MCP server...")
    # Pre-build the index on startup for faster first-time searches
    _build_index_if_needed()
    mcp.run()
