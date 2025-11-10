import sys
from pathlib import Path
import logging
from src.vector_doc_parser import VectorDocParser, parse_directory

# Get the logger from the parser module
logger = logging.getLogger("VectorDocParser")

# ============================================================
# CLI Entry Point
# ============================================================

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Parse single file: python main.py <file_path>")
        print("  Parse directory:   python main.py <directory_path>")
        sys.exit(1)
    
    target_path = sys.argv[1]
    path = Path(target_path)
    
    if path.is_file():
        parser = VectorDocParser()
        func_info = parser.parse_file(str(path))
        if func_info:
            print(func_info)
        else:
            logger.error(f"Failed to parse {path}")
    
    elif path.is_dir():
        functions = parse_directory(str(path))
        logger.info(f"Parsed {len(functions)} functions in total.")
        for func in functions:
            print("\n" + "="*80)
            print(func)
    
    else:
        logger.error(f"Invalid path: {target_path}")
