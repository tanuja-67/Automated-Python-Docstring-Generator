import ast

def insert_docstring(code: str, function_name: str, new_docstring: str, class_name: str = None):
    """
    Insert or replace a docstring in the given code.
    
    Args:
        code: Original Python code
        function_name: Name of the function
        new_docstring: New docstring to insert
        class_name: Optional class name if this is a method
    
    Returns:
        Updated code with inserted docstring
    """
    tree = ast.parse(code)
    lines = code.splitlines(keepends=True)
    
    # Find the target function
    target_func = None
    target_class = None
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and class_name and node.name == class_name:
            target_class = node
            for item in node.body:
                if isinstance(item, ast.FunctionDef) and item.name == function_name:
                    target_func = item
                    break
        elif isinstance(node, ast.FunctionDef) and node.name == function_name and not class_name:
            target_func = node
            break
    
    if not target_func:
        return code
    
    # Get the indentation of the function
    func_line = target_func.lineno - 1
    func_indent = len(lines[func_line]) - len(lines[func_line].lstrip())
    indent_str = ' ' * (func_indent + 4)
    
    # Format the docstring
    docstring_lines = new_docstring.strip().splitlines()
    formatted_docstring = '\n'.join(docstring_lines)
    
    # Create docstring with proper quotes
    if '"""' in formatted_docstring:
        quote = "'''"
    else:
        quote = '"""'
    
    docstring_block = f'{indent_str}{quote}{formatted_docstring}{quote}\n'
    
    # Find where to insert the docstring (after the def line)
    def_line = target_func.lineno - 1
    
    # Check if there's already a docstring
    first_stmt = target_func.body[0] if target_func.body else None
    has_docstring = isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, ast.Constant) and isinstance(first_stmt.value.value, str)
    
    if has_docstring:
        # Replace existing docstring
        old_docstring_end = first_stmt.end_lineno
        insert_pos = old_docstring_end
        # Remove old docstring lines
        del lines[first_stmt.lineno - 1:old_docstring_end]
        # Insert new docstring
        lines.insert(def_line + 1, docstring_block)
    else:
        # Insert new docstring after the def line
        insert_pos = def_line + 1
        lines.insert(insert_pos, docstring_block)
    
    return ''.join(lines)


def apply_all_docstrings(code: str, docstrings: dict):
    """
    Apply multiple docstrings to a code string.
    
    Args:
        code: Original Python code
        docstrings: Dict with keys like "function_name" or "ClassName.method_name"
                   and values as the docstrings to insert
    
    Returns:
        Updated code with all docstrings inserted
    """
    result = code
    
    for func_identifier, docstring in docstrings.items():
        if '.' in func_identifier:
            class_name, function_name = func_identifier.rsplit('.', 1)
            result = insert_docstring(result, function_name, docstring, class_name=class_name)
        else:
            result = insert_docstring(result, func_identifier, docstring)
    
    return result
