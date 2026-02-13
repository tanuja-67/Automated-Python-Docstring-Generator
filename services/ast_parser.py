import ast
import inspect

def parse_functions(code: str):
    """
    Parse Python code and extract functions and class methods.
    
    Returns list of function info dicts with:
    - name: function name
    - args: list of argument names
    - has_docstring: whether function has a docstring
    - docstring: the existing docstring (if any)
    - source_lines: the function source code
    - line_number: starting line number
    - class_name: (optional) parent class name if this is a method
    - is_method: whether this is a class method
    """
    tree = ast.parse(code)
    functions = []
    lines = code.splitlines()

    def extract_function_info(node, class_name=None, depth=0):
        """Recursively extract function information."""
        if isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
            has_docstring = ast.get_docstring(node) is not None
            docstring = ast.get_docstring(node) or ""
            
            # Get function source lines
            start_line = node.lineno - 1
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else len(lines)
            source_lines = lines[start_line:end_line]
            
            # Calculate indentation from first line
            first_line = source_lines[0]
            indent = len(first_line) - len(first_line.lstrip())
            
            # Dedent source code
            dedented_lines = []
            for line in source_lines:
                if line.strip():
                    dedented_lines.append(line[indent:])
                else:
                    dedented_lines.append('')
            
            source_code = '\n'.join(dedented_lines)
            
            functions.append({
                "name": node.name,
                "args": [arg.arg for arg in node.args.args],
                "has_docstring": has_docstring,
                "docstring": docstring,
                "source_code": source_code,
                "line_number": node.lineno,
                "class_name": class_name,
                "is_method": class_name is not None,
                "node": node,
                "original_indent": indent,
            })

        # Handle nested class methods
        if isinstance(node, ast.ClassDef):
            for item in node.body:
                extract_function_info(item, class_name=node.name, depth=depth+1)

    # First pass: get top-level functions and classes
    for node in tree.body:
        extract_function_info(node)

    return functions
