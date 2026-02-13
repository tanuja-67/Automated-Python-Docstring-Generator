from datetime import datetime

def export_docstrings(functions: list, style: str = "markdown"):
    """
    Export approved docstrings into a consolidated format.
    
    Args:
        functions: List of function dicts (from ast_parser) with 'approved_docstring' field
        style: Export format - 'markdown', 'text', or 'python'
    
    Returns:
        Formatted string with all docstrings
    """
    approved_functions = [f for f in functions if f.get('approved_docstring')]
    
    if not approved_functions:
        return "No approved docstrings to export."
    
    if style == "markdown":
        return _export_markdown(approved_functions)
    elif style == "text":
        return _export_text(approved_functions)
    elif style == "python":
        return _export_python(approved_functions)
    else:
        return _export_markdown(approved_functions)


def _export_markdown(functions: list) -> str:
    """Export as Markdown format."""
    output = []
    output.append(f"# Generated Python Docstrings")
    output.append(f"\n**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    current_file = None
    
    for func in functions:
        if func.get('filename') != current_file:
            current_file = func.get('filename', 'Unknown')
            output.append(f"\n## File: `{current_file}`\n")
        
        # Function header
        if func.get('is_method'):
            output.append(f"### Method: `{func['class_name']}.{func['name']}()`\n")
        else:
            output.append(f"### Function: `{func['name']}()`\n")
        
        # Parameters
        if func.get('args'):
            output.append(f"**Parameters:** {', '.join(func['args'])}\n")
        
        # Docstring
        output.append("**Docstring:**\n")
        output.append("```python")
        output.append(f'"""{func["approved_docstring"]}"""')
        output.append("```\n")
    
    return "\n".join(output)


def _export_text(functions: list) -> str:
    """Export as plain text format."""
    output = []
    output.append("=" * 70)
    output.append("PYTHON DOCSTRINGS EXPORT")
    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("=" * 70)
    output.append("")
    
    current_file = None
    
    for func in functions:
        if func.get('filename') != current_file:
            current_file = func.get('filename', 'Unknown')
            output.append("")
            output.append(f"FILE: {current_file}")
            output.append("-" * 70)
        
        # Function header
        if func.get('is_method'):
            output.append(f"\nMETHOD: {func['class_name']}.{func['name']}()")
        else:
            output.append(f"\nFUNCTION: {func['name']}()")
        
        # Parameters
        if func.get('args'):
            output.append(f"Parameters: {', '.join(func['args'])}")
        
        # Docstring
        output.append(f"\nDocstring:\n{func['approved_docstring']}\n")
    
    return "\n".join(output)


def _export_python(functions: list) -> str:
    """Export as Python comments format."""
    output = []
    output.append(f"# Python Docstrings Export")
    output.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("")
    
    current_file = None
    
    for func in functions:
        if func.get('filename') != current_file:
            current_file = func.get('filename', 'Unknown')
            output.append(f"\n# ============================================")
            output.append(f"# FILE: {current_file}")
            output.append(f"# ============================================")
        
        # Function header
        output.append("")
        if func.get('is_method'):
            output.append(f"# Method: {func['class_name']}.{func['name']}()")
        else:
            output.append(f"# Function: {func['name']}()")
        
        # Parameters
        if func.get('args'):
            output.append(f"# Parameters: {', '.join(func['args'])}")
        
        # Docstring as comment
        output.append("# Docstring:")
        for line in func['approved_docstring'].splitlines():
            output.append(f"# {line}")
    
    return "\n".join(output)


def create_consolidated_file(functions: list, filename: str = "generated_docstrings", format_type: str = "markdown"):
    """
    Create a consolidated docstrings file.
    
    Args:
        functions: List of function dicts with approved docstrings
        filename: Base filename (without extension)
        format_type: Format type (markdown, text, python)
    
    Returns:
        Tuple of (content, file_extension)
    """
    content = export_docstrings(functions, style=format_type)
    
    extensions = {
        "markdown": "md",
        "text": "txt",
        "python": "py"
    }
    
    ext = extensions.get(format_type, "txt")
    
    return content, ext
