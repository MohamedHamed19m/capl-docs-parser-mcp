import re
import logging
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path

# ============================================================ 
# Setup Logging
# ============================================================ 
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for detailed tracing
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler("vector_doc_parser.log", mode='w', encoding='utf-8'),
    ]
)
logger = logging.getLogger("VectorDocParser")

# ============================================================ 
# Data Classes
# ============================================================ 

@dataclass
class Parameter:
    """Represents a function parameter"""
    name: str
    description: str


@dataclass
class FunctionInfo:
    """Represents a parsed Vector function documentation"""
    function_name: str
    syntax_forms: List[str] = field(default_factory=list)
    description: str = ""
    parameters: List[Parameter] = field(default_factory=list)
    return_values: List[str] = field(default_factory=list)
    example: Optional[str] = None
    valid_for: Optional[str] = None
    
    def __str__(self):
        output = [f"Function: {self.function_name}"]
        
        if self.valid_for:
            output.append(f"Valid for: {self.valid_for}")
        
        output.append("\nSyntax:")
        for i, syntax in enumerate(self.syntax_forms, 1):
            output.append(f"  Form {i}: {syntax}")
        
        if self.description:
            output.append(f"\nDescription:\n  {self.description}")
        
        if self.parameters:
            output.append("\nParameters:")
            for param in self.parameters:
                output.append(f"  - {param.name}: {param.description}")
        
        if self.return_values:
            output.append("\nReturn Values:")
            for ret in self.return_values:
                output.append(f"  - {ret}")
        
        if self.example:
            output.append(f"\nExample:\n{self.example}")
        
        return "\n".join(output)


# ============================================================ 
# Main Parser Class
# ============================================================ 

class VectorDocParser:
    """Parser for Vector documentation markdown files"""
    
    def __init__(self):
        self.current_section = None
    
    def parse_file(self, file_path: str) -> Optional[FunctionInfo]:
        """Parse a Vector documentation markdown file"""
        logger.debug(f"Opening file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to open {file_path}: {e}")
            return None
        
        return self.parse_content(content)
        
    def parse_content(self, content: str) -> Optional[FunctionInfo]:
        """Parse markdown content and extract function information"""
        lines = content.split('\n')
        func_info = FunctionInfo(function_name="")
        
        logger.debug("Starting content parsing...")
        
        current_section = None
        example_lines = []
        in_code_block = False
        in_syntax_code_block = False
        param_buffer = []
        return_buffer = []
        syntax_buffer = []
        
        for i, line in enumerate(lines):
            logger.debug(f"Line {i}: {line.strip()}")
            
            try:
                # Extract function name from header
                if line.startswith('# ') and not func_info.function_name:
                    header = line[2:].strip()
                    # Handle "name: description" format
                    if ': ' in header:
                        func_info.function_name = header.split(':')[0].strip()
                    else:
                        func_info.function_name = header.split('<')[0].strip()
                    logger.debug(f"Found function name: {func_info.function_name}")
                    continue
                
                # Extract "Valid for" information
                if 'Valid for' in line and '[Valid for]' in line:
                    valid_match = re.search(r'Valid for.*?:*([^•]+)', line)
                    if valid_match:
                        func_info.valid_for = valid_match.group(1).strip()
                    elif i + 1 < len(lines):
                        func_info.valid_for = lines[i + 1].strip()
                    logger.debug(f"Valid for: {func_info.valid_for}")
                    continue
                
                # Detect section headers
                if line.startswith('## '):
                    current_section = line[3:].strip()
                    logger.debug(f"Switched section -> {current_section}")
                    
                    # Save buffered data when leaving a section
                    if param_buffer:
                        func_info.parameters.extend(param_buffer)
                        param_buffer = []
                    if return_buffer:
                        func_info.return_values.extend(return_buffer)
                        return_buffer = []
                    if syntax_buffer:
                        func_info.syntax_forms.extend(syntax_buffer)
                        syntax_buffer = []
                    continue
                
                # -------------------------
                # Function Syntax / Method Syntax
                # -------------------------
                if current_section in ["Function Syntax", "Method Syntax", "Selectors"]:
                    # Toggle fenced code block for syntax
                    if line.strip().startswith('```'):
                        in_syntax_code_block = not in_syntax_code_block
                        logger.debug(f"Toggled syntax block: {in_syntax_code_block}")
                        # If we just closed the block, flush nothing here (final flush below)
                        continue

                    # Inside a fenced syntax code block
                    if in_syntax_code_block and line.strip():
                        clean_line = line.strip()
                        if clean_line and not clean_line.startswith('//'):
                            syntax_buffer.append(clean_line)
                            logger.debug(f"Added syntax line (code block): {clean_line}")
                    
                    # Bullet items that include a code span: - `syntax` or - syntax
                    elif line.strip().startswith('-'):
                        # Try to extract from code span first
                        if '`' in line:
                            # Extract all code spans from the line
                            syntax_spans = re.findall(r'`([^`]+)`', line)
                            for syntax_text in syntax_spans:
                                if any(type_hint in syntax_text for type_hint in ['byte', 'word', 'int', 'dword', 'qword', 'char']):
                                    syntax_buffer.append(syntax_text.strip())
                                    logger.debug(f"Added inline code syntax: {syntax_text.strip()}")
                        # If no code span but line looks like syntax (has type hints or angle brackets), extract after dash
                        elif any(type_hint in line for type_hint in ['byte', 'word', 'int', 'dword', 'qword', 'char']) or ('<' in line and '>' in line):
                            clean_line = line.strip('- ').strip()
                            if clean_line.startswith('`'):  # Handle any remaining backticks
                                clean_line = clean_line.strip('`')
                            syntax_buffer.append(clean_line)
                            logger.debug(f"Added bullet point syntax: {clean_line}")

                    # Markdown link style or bracketed text: [syntax](url) or [syntax]
                    else:
                        # find the first [...] occurrence and take its content
                        bracket_match = re.search(r'\[(.*?)\]', line)  # Non-greedy to handle nested []
                        if bracket_match:
                            syntax_text = bracket_match.group(1).strip()
                            # strip surrounding backticks if present inside the brackets
                            syntax_text = syntax_text.strip('`').strip()
                            # avoid picking up simple navigation links that don't look like syntax
                            # a heuristic: syntax likely contains parentheses, a dot, or a space with type hints
                            if syntax_text and ('(' in syntax_text or '.' in syntax_text or 
                                             any(type_hint in syntax_text for type_hint in 
                                                 ['byte', 'word', 'int', 'dword', 'qword', 'char'])):
                                syntax_buffer.append(syntax_text)
                                logger.debug(f"Added bracket/link-style syntax: {syntax_text}")
                            else:
                                logger.debug(f"Ignored bracket content (likely navigation): {syntax_text}")
                
                # -------------------------
                # Description Section
                # -------------------------
                elif current_section == "Description" and line.strip():
                    if not line.startswith('#') and not line.startswith('['):
                        if func_info.description:
                            func_info.description += " " + line.strip()
                        else:
                            func_info.description = line.strip()
                
                # -------------------------
                # Parameters Section
                # -------------------------
                elif current_section == "Parameters":
                    # Handles "- **name**: description" and "- **type name[]** description"
                    param_match = re.match(r'^\s*-\s*\*\*([^*]+)\*\*\s*:?\s*(.*)', line)
                    if param_match:
                        name, desc = param_match.groups()
                        # If the name part contains type info, try to extract just the name
                        # e.g., "byte key[]" -> "key"
                        name_parts = name.strip().split()
                        if len(name_parts) > 1:
                            # Take the last part as the name, e.g., 'key[]' from 'byte key[]'
                            name = name_parts[-1].replace('[]', '')

                        param_buffer.append(Parameter(name.strip(), desc))
                        logger.debug(f"Added parameter: {name.strip()} -> {desc.strip()}")
                    elif line.strip() and param_buffer:
                        param_buffer[-1].description += " " + line.strip()
                
                # -------------------------
                # Return Values Section
                # -------------------------
                elif current_section == "Return Values":
                    # Handles "- **value**: description"
                    ret_match = re.match(r'^\s*-\s*\*\*([^*]+)\*\*\s*:?\s*(.*)', line)
                    if ret_match:
                        val, desc = ret_match.groups()
                        full_desc = f"{val.strip()}: {desc.strip()}"
                        return_buffer.append(full_desc)
                        logger.debug(f"Added return value: {full_desc}")
                    # Handles "- value: description"
                    elif line.strip().startswith('-') and ':' in line:
                        clean_line = line.strip()[1:].strip()
                        return_buffer.append(clean_line)
                        logger.debug(f"Added return value (simple list): {clean_line}")
                    # Handles multi-line descriptions
                    elif line.strip() and return_buffer:
                        return_buffer[-1] += " " + line.strip()
                
                # -------------------------
                # Example Section
                # -------------------------
                elif current_section == "Example":
                    if line.strip().startswith('```'):
                        in_code_block = not in_code_block
                        logger.debug(f"Toggled example block: {in_code_block}")
                        if not in_code_block and example_lines:
                            func_info.example = '\n'.join(example_lines)
                        continue
                    if in_code_block:
                        example_lines.append(line)
            
            except Exception as e:
                logger.exception(f"Error processing line {i}: {line}")
        
        # -------------------------
        # Final cleanup
        # -------------------------
        if param_buffer:
            func_info.parameters.extend(param_buffer)
        if return_buffer:
            func_info.return_values.extend(return_buffer)
        if syntax_buffer:
            func_info.syntax_forms.extend(syntax_buffer)
        
        if not func_info.function_name or not func_info.syntax_forms:
            logger.warning("Incomplete function info — skipping.")
            return None
        
        logger.info(f"Parsed function: {func_info.function_name}")
        return func_info


# ============================================================ 
# Batch Parsing Utility
# ============================================================ 

def parse_directory(directory_path: str) -> List[FunctionInfo]:
    """Parse all markdown files in a directory"""
    parser = VectorDocParser()
    results = []
    
    path = Path(directory_path)
    logger.info(f"Scanning directory: {path}")
    
    for md_file in path.glob('**/*.md'):
        try:
            logger.debug(f"Parsing file: {md_file}")
            func_info = parser.parse_file(str(md_file))
            if func_info:
                results.append(func_info)
                logger.info(f"✓ Parsed: {md_file.name} -> {func_info.function_name}")
            else:
                logger.warning(f"No data extracted from {md_file.name}")
        except Exception as e:
            logger.exception(f"✗ Error parsing {md_file.name}")
    
    return results
