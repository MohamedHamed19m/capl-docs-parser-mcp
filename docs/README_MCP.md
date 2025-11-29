# CAPL Documentation Search MCP Server

## Overview

This MCP (Model Context Protocol) server provides a powerful interface to search and retrieve information from a local repository of Vector CAPL (Communication Access Programming Language) documentation. It is designed to work with documentation written in Markdown (`.md`) format.

The server indexes the entire documentation and allows for intelligent, natural language queries to find relevant CAPL functions, their syntax, parameters, and usage examples, making it an invaluable tool for developers working with Vector tools like CANoe.

## How it Works

The server operates through a simple yet effective workflow:

1.  **Indexing on Startup**: When the server starts, it automatically scans a specified directory (by default, `./inputs`) for all CAPL documentation files (`.md`).

2.  **Parsing**: Each Markdown file is parsed using a dedicated `VectorDocParser`. This parser understands the typical structure of CAPL documentation and extracts key information into a structured format, including:
    *   Function Name
    *   Syntax Variations
    *   Description
    *   Parameters
    *   Return Values
    *   Code Examples

3.  **Semantic Search Indexing**: The parsed content is then used to build a lightweight semantic search index. This is achieved using a TF-IDF (Term Frequency-Inverse Document Frequency) vectorizer, which allows the server to understand the relevance of documents to a natural language query without relying on heavy deep learning models. The index is cached in the `.cache` directory to ensure fast subsequent startups.

4.  **Exposing Tools**: Once the index is ready, the server exposes a set of tools that can be called by an MCP client to interact with the documentation.

## How to Use

1.  **Place Documentation**: Ensure your CAPL documentation `.md` files are located in the `inputs` directory. The server will recursively scan this folder.

2.  **Start the Server**: Run the server from your terminal:
    ```bash
    python MCP_Server.py
    ```
    The server will log its progress as it builds the index. Once you see the message "Starting MCP server...", it is ready to accept connections.

3.  **Connect with an MCP Client**: Use any MCP-compatible client to connect to the `VectorDocExtractorServer` and call its tools.

## Available Tools

The server provides the following tools:

### 1. `semantic_search_capl_docs`

Finds and ranks relevant CAPL function names based on a natural language query.

**Parameters:**

*   `query` (str): The natural language search query (e.g., "how to send an ethernet packet").
*   `doc_paths` (List[str], optional): A list of paths to the documentation directories. Defaults to `["./inputs"]`.
*   `top_k` (int, optional): The number of top matching functions to return. Defaults to `20`.
*   `force_rebuild_index` (bool, optional): If `True`, the server will delete the cache and rebuild the search index before performing the search. Defaults to `False`.

**Returns:**

A dictionary with a ranked list of relevant function names and their scores.

### 2. `get_capl_function_details`

Retrieves the complete, structured documentation for a single, specific CAPL function.

**Parameters:**

*   `function_name` (str): The **exact** name of the CAPL function you want details for (e.g., `EthGetLinkStatus`).
*   `doc_paths` (List[str], optional): A list of directories where the documentation is located. Defaults to `["./inputs"]`.

**Returns:**

A dictionary containing the full details of the function, including its description, all syntax forms, parameters, return values, and a code example if available.

### 3. `parse_md_file`

A low-level utility tool that parses a single Markdown file and returns its structured content as a JSON object. This is useful for debugging the parser on a specific file.

**Parameters:**

*   `file_path` (str): The absolute or relative path to the `.md` file to parse.

**Returns:**

A dictionary containing the parsed `FunctionInfo` or an error message if parsing fails.

## Best Practices

*   **Use Specific Queries**: For `semantic_search_capl_docs`, more specific queries yield better results. For example, instead of "ethernet", try "get ethernet packet payload".
*   **Search Across Multiple Directories**: To search documentation spread across several directories, provide a list of paths to the `doc_paths` parameter. For instance, to search both the default `inputs` directory and an additional `new_database/CANoeIL` directory for functions controlling message sending in a simulation node:

    ```python
    semantic_search_capl_docs(
        query="control the sending of a certain message of a simulation node",
        doc_paths=["./inputs", "C:\\Users\\user\\Desktop\\test\\0_my_repo\\CAPL-Doc-Extractor\\new_database\\CANoeIL"]
    )
    ```
    This search would likely identify functions like `ILNodeControlMsg`, which is designed to influence message sending for simulation nodes.
*   **Use Exact Function Names**: When using `get_capl_function_details`, ensure the function name is spelled correctly and matches the name in the documentation exactly,
or its better to search for specific name using semantic search then after that ask the ai about function details (syntax or examples) and it will pass the correct name.
*   **Rebuild the Index When Needed**: If you have updated, added, or removed documentation files, you can either restart the server or use the `force_rebuild_index=True` parameter in your search query to ensure the index is up-to-date.
*   **Check the Logs**: The server logs its operations to the console and to `vector_doc_parser.log`. If you encounter unexpected behavior, these logs are the first place to look for clues.
*   **Organize Your Documentation**: Keeping your `.md` files in a well-organized directory structure within `inputs` will not affect the server's functionality but will make your project easier to maintain.
