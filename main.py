import re
from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path


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


class VectorDocParser:
    """Parser for Vector documentation markdown files"""
    
    def __init__(self):
        self.current_section = None
    
    def parse_file(self, file_path: str) -> Optional[FunctionInfo]:
        """Parse a Vector documentation markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> Optional[FunctionInfo]:
        """Parse markdown content and extract function information"""
        lines = content.split('\n')
        
        func_info = FunctionInfo(function_name="")
        current_section = None
        example_lines = []
        in_code_block = False
        param_buffer = []
        return_buffer = []
        
        for i, line in enumerate(lines):
            # Extract function name from header
            if line.startswith('# ') and not func_info.function_name:
                func_info.function_name = line[2:].strip()
                continue
            
            # Extract "Valid for" information
            if 'Valid for' in line and '[Valid for]' in line:
                # Look for the next line or same line for the actual info
                valid_match = re.search(r'Valid for.*?:\s*([^•]+)', line)
                if valid_match:
                    func_info.valid_for = valid_match.group(1).strip()
                elif i + 1 < len(lines):
                    func_info.valid_for = lines[i + 1].strip()
                continue
            
            # Detect sections
            if line.startswith('## '):
                current_section = line[3:].strip()
                
                # Save buffered parameters when leaving Parameters section
                if param_buffer and current_section != "Parameters":
                    func_info.parameters.extend(param_buffer)
                    param_buffer = []
                
                # Save buffered return values when leaving Return Values section
                if return_buffer and current_section != "Return Values":
                    func_info.return_values.extend(return_buffer)
                    return_buffer = []
                
                continue
            
            # Parse based on current section
            if current_section == "Function Syntax" or current_section == "Method Syntax":
                # Extract function syntax
                if line.strip().startswith('-') and '`' in line:
                    syntax = re.search(r'`([^`]+)`', line)
                    if syntax:
                        func_info.syntax_forms.append(syntax.group(1))
            
            elif current_section == "Description":
                # Collect description text
                if line.strip() and not line.startswith('#') and not line.startswith('['):
                    if func_info.description:
                        func_info.description += " " + line.strip()
                    else:
                        func_info.description = line.strip()
            
            elif current_section == "Parameters":
                # Parse parameters (format: - **name**: description)
                param_match = re.match(r'^\s*-\s*\*\*([^*]+)\*\*:\s*(.+)', line)
                if param_match:
                    param_name = param_match.group(1).strip()
                    param_desc = param_match.group(2).strip()
                    param_buffer.append(Parameter(name=param_name, description=param_desc))
                elif param_buffer and line.strip() and not line.startswith('-'):
                    # Continue previous parameter description
                    param_buffer[-1].description += " " + line.strip()
            
            elif current_section == "Return Values":
                # Parse return values
                ret_match = re.match(r'^\s*-\s*\*\*([^*]+)\*\*:\s*(.+)', line)
                if ret_match:
                    ret_value = ret_match.group(1).strip()
                    ret_desc = ret_match.group(2).strip()
                    return_buffer.append(f"{ret_value}: {ret_desc}")
                elif line.strip().startswith('-'):
                    # Alternative format without bold
                    return_buffer.append(line.strip()[1:].strip())
                elif return_buffer and line.strip() and not line.startswith('-'):
                    # Continue previous return value description
                    return_buffer[-1] += " " + line.strip()
            
            elif current_section == "Example":
                # Detect code blocks
                if line.strip().startswith('```'):
                    in_code_block = not in_code_block
                    if not in_code_block and example_lines:
                        # End of code block
                        func_info.example = '\n'.join(example_lines)
                    continue
                
                if in_code_block:
                    example_lines.append(line)
        
        # Save any remaining buffered data
        if param_buffer:
            func_info.parameters.extend(param_buffer)
        if return_buffer:
            func_info.return_values.extend(return_buffer)
        
        # Return None if no meaningful data was extracted
        if not func_info.function_name or not func_info.syntax_forms:
            return None
        
        return func_info


def parse_directory(directory_path: str) -> List[FunctionInfo]:
    """Parse all markdown files in a directory"""
    parser = VectorDocParser()
    results = []
    
    path = Path(directory_path)
    for md_file in path.glob('**/*.md'):
        try:
            func_info = parser.parse_file(str(md_file))
            if func_info:
                results.append(func_info)
                print(f"✓ Parsed: {md_file.name} -> {func_info.function_name}")
        except Exception as e:
            print(f"✗ Error parsing {md_file.name}: {e}")
    
    return results


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Parse single file: python script.py <file_path>")
        print("  Parse directory:   python script.py <directory_path>")
        sys.exit(1)
    
    target_path = sys.argv[1]
    path = Path(target_path)
    
    if path.is_file():
        # Parse single file
        parser = VectorDocParser()
        func_info = parser.parse_file(str(path))
        if func_info:
            print(func_info)
        else:
            print(f"Failed to parse {path}")
    
    elif path.is_dir():
        # Parse directory
        functions = parse_directory(str(path))
        print(f"\nParsed {len(functions)} functions:")
        for func in functions:
            print("\n" + "="*80)
            print(func)
    
    else:
        print(f"Error: {target_path} is not a valid file or directory")