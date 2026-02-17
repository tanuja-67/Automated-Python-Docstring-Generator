from services.api_manager import generate_with_fallback

def format_docstring_pep257(docstring: str) -> str:
    """
    Format docstring to comply with PEP 257 D209: 
    Multi-line docstring closing quotes should be on a separate line.
    
    Args:
        docstring: Raw docstring from LLM
    
    Returns:
        Properly formatted docstring
    """
    if not docstring.strip():
        return docstring
    
    # Remove leading/trailing whitespace
    docstring = docstring.strip()
    
    # Extract content and quotes
    lines = docstring.splitlines()
    
    if len(lines) <= 1:
        # Single-line docstring, return as-is
        return docstring
    
    # Multi-line docstring: ensure closing quotes are on separate line
    # Find the quote type used
    first_line = lines[0]
    if first_line.startswith('"""'):
        quote_mark = '"""'
    elif first_line.startswith("'''"):
        quote_mark = "'''"
    elif first_line.startswith('r"""'):
        quote_mark = 'r"""'
    elif first_line.startswith("r'''"):
        quote_mark = "r'''"
    else:
        return docstring
    
    # Remove quotes from first and last line
    first_line_content = first_line[len(quote_mark):].rstrip('"""' + "'''")
    
    # Rebuild docstring with closing quotes on separate line
    content_lines = []
    content_lines.append(quote_mark + first_line_content)
    
    # Add middle lines
    for line in lines[1:-1]:
        content_lines.append(line.rstrip('"""' + "'''"))
    
    # Add last line without quotes
    last_line = lines[-1].rstrip('"""' + "'''").rstrip()
    if last_line:
        content_lines.append(last_line)
    
    # Add closing quotes on separate line
    content_lines.append(quote_mark)
    
    return '\n'.join(content_lines)

def generate_docstring(function_code: str, function_name: str = "", args: list = None, style: str = "Google"):
    """
    Generate a docstring for a given function using LLM.
    
    Args:
        function_code: The function source code
        function_name: Optional function name for context
        args: Optional list of argument names
        style: Docstring style (Google, NumPy, or reST)
    
    Returns:
        Generated docstring string
    """
    args_desc = f"with parameters: {', '.join(args)}" if args else ""
    
    style_guide = {
        "Google": """
Use Google style docstring format:
- One line summary (imperative mood)
- Blank line
- Longer description if needed
- Args section with each parameter
- Returns section
- Raises section if applicable
""",
        "NumPy": """
Use NumPy style docstring format:
- One line summary
- Extended summary
- Parameters section with types
- Returns section with types
- Raises section if applicable
""",
        "reST": """
Use reStructuredText format:
- One line summary
- Extended summary
- :param name: description
- :returns: description
- :raises: exception names
"""
    }
    
    prompt = f"""Generate a concise, professional {style} style Python docstring following PEP 257 for this function {args_desc}:

{function_code}

{style_guide.get(style, '')}

Return ONLY the docstring, without code formatting or extra text."""
    
    raw_docstring = generate_with_fallback(prompt)
    # Format docstring to comply with PEP 257 D209
    return format_docstring_pep257(raw_docstring)
