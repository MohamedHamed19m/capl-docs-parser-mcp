# Vector Documentation Parser

A Python package for extracting structured function information from Vector (CAPL) documentation in Markdown format.

## Overview
This tool parses Vector documentation files (such as CAPL function docs) and extracts detailed function information into structured Python class objects. It automates the process of converting Markdown-based documentation into data that can be further processed, analyzed, or integrated into other systems.

## Features
- **Comprehensive Markdown Parsing**: Extracts function names, multiple syntax forms, descriptions, parameters, return values, code examples, and "Valid for" information.
- **Structured Output**: Stores all extracted data in well-defined Python dataclasses (`FunctionInfo`, `Parameter`).
- **Handles Complex Docs**: Supports multiple syntax forms, preserves code examples, and robustly parses various Markdown section formats.
- **Batch Processing**: Can parse a single file or all Markdown files in a directory.
- **Pretty Printing**: Includes `__str__` methods for easy inspection of parsed data.
- **Error Handling**: Designed to handle malformed or incomplete documentation gracefully.

## Main Components
- **`FunctionInfo` class**: Stores all extracted information for a function, including:
	- Function name
	- Multiple syntax forms
	- Description
	- Parameters (with names and descriptions)
	- Return values
	- Example code
	- "Valid for" information
- **`Parameter` class**: Represents individual parameters with name and description.
- **`VectorDocParser` class**: Handles the actual parsing logic for files and directories.

## Usage

### Parse a single file
```python
parser = VectorDocParser()
func_info = parser.parse_file("path/to/file.md")
```

### Parse all markdown files in a directory
```python
functions = parser.parse_directory("./vector_docs")
```

### Command-line usage
Run the script directly to parse a file or directory:
```bash
python main.py <file_path_or_directory>
```

- To parse a single file: `python main.py path/to/file.md`
- To parse a directory: `python main.py path/to/directory/`

## Requirements
- Python 3.7+
- No external dependencies (uses only the Python standard library)

## Input Format
- Markdown files documenting Vector (CAPL) functions, with sections for syntax, parameters, return values, examples, etc.

## Output
- Structured Python objects containing all extracted information, ready for further processing or integration.

## Project Structure
- `main.py` — Entry point for the parser (CLI and importable)
- `MCP_Server.py` — Hosts the parsing logic as an MCP server.
- `inputs/` — Example input files (Markdown)
- `README.md` — This documentation

## MCP Server

The `MCP_Server.py` file hosts the documentation parsing logic as a `FastMCP` server, allowing the functionality to be accessed as a remote tool.

### Functionality

The server provides tools for searching and parsing Vector CAPL documentation from Markdown files. It uses the `VectorDocParser` from `main.py` to extract structured information.

### Tools

- **`search_capl_function_docs`**: Searches a directory for Markdown files matching a function name, parses them, and returns structured information for the matches.
- **`parse_md_file`**: Parses a single specified Markdown file and returns its structured content.
 
 
📘 Example CAPL Documentation

If you want to explore additional CAPL function documentation examples or test Markdown files,
you can refer to the following public repository:

🔗 Sylphith/capl_docs — AUTOSAR Ethernet IL CAPL Functions
[https://github.com/Sylphith/capl_docs/blob/main/IP/AUTOSARethIL/CAPLfunctionsAREthILOverview.md].

This repo contains real-world CAPL .md documentation files that you can use to test or validate the parser.
---

*This project is maintained by MohamedHamed19m.*
