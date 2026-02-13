from services.api_manager import generate_with_fallback

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
    
    return generate_with_fallback(prompt)
