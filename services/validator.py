import ast
import tempfile
import os


def validate_docstring(docstring: str, function_name: str = "temp_func"):
    """
    Validate docstring against PEP 257 conventions using multiple checks.
    
    Args:
        docstring: The docstring to validate
        function_name: Optional function name for context
    
    Returns:
        List of error strings with format "[ErrorCode] Message"
    """
    if not docstring or not docstring.strip():
        return ["[D100] Missing docstring in public function"]
    
    errors = []
    
    # Parse docstring lines
    raw_lines = docstring.splitlines()
    lines = [line.rstrip() for line in raw_lines]
    
    # Trim leading/trailing blank lines for analysis
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    
    if not lines:
        return ["[D100] Missing docstring in public function"]
    
    summary = lines[0].strip()
    
    # D400: First line should end with a period
    if not summary.endswith("."):
        errors.append("[D400] First line should end with a period.")
    
    # D401: First line should be in imperative mood
    non_imperative = [
        "returns", "computes", "calculates", "determines", "gets",
        "retrieves", "identifies", "processes", "handles", "represents",
        "defines", "performs", "executes", "stores", "creates",
        "generates", "initializes", "sets", "updates", "modifies",
        "changes", "converts", "transforms", "formats", "parses",
        "analyzes", "checks", "validates", "verifies", "prints",
        "displays", "shows", "outputs", "reads", "writes",
        "opens", "closes", "saves", "deletes", "removes",
        "sorts", "searches", "finds", "contains", "has",
        "is", "are", "was", "were", "be", "being", "been"
    ]
    first_word = summary.split()[0].lower().rstrip(".,:;!?")
    if first_word in non_imperative:
        # Convert to imperative form
        imperative_map = {
            "calculates": "Calculate", "computes": "Compute", "determines": "Determine",
            "gets": "Get", "retrieves": "Retrieve", "identifies": "Identify",
            "processes": "Process", "handles": "Handle", "represents": "Represent",
            "defines": "Define", "performs": "Perform", "executes": "Execute",
            "stores": "Store", "creates": "Create", "generates": "Generate",
            "initializes": "Initialize", "sets": "Set", "updates": "Update",
            "modifies": "Modify", "changes": "Change", "converts": "Convert",
            "transforms": "Transform", "formats": "Format", "parses": "Parse",
            "analyzes": "Analyze", "checks": "Check", "validates": "Validate",
            "verifies": "Verify", "prints": "Print", "displays": "Display",
            "shows": "Show", "outputs": "Output", "reads": "Read", "writes": "Write",
            "opens": "Open", "closes": "Close", "saves": "Save", "deletes": "Delete",
            "removes": "Remove", "sorts": "Sort", "searches": "Search", "finds": "Find",
            "contains": "Include", "returns": "Return", "is": "Be", "are": "Be",
            "was": "Be", "were": "Be", "being": "Be", "been": "Be",
        }
        imperative = imperative_map.get(first_word, first_word.capitalize())
        errors.append(f"[D401] First line should be in imperative mood; change '{summary.split()[0]}' to '{imperative}'.")
    
    # D402: First line should not be a function signature
    if "(" in summary and ")" in summary:
        errors.append("[D402] First line should not be a function signature.")
    
    # D213: Multi-line docstring summary should be on the first line
    if len(lines) > 1:
        if lines[1].strip():
            # Second line has content - check if this is intentional
            if not summary.endswith(":"):
                errors.append("[D213] Multi-line docstring summary should be on the first line; use a period to end the summary.")
    
    # D209: Multi-line docstring closing quotes should be on a separate line  
    if len(lines) > 2:
        last_line = lines[-1].strip()
        second_last = lines[-2].strip() if len(lines) > 1 else ""
        # If last line has content and isn't just closing quotes
        if last_line and last_line not in ('"""', "'''", 'r"""', "r'''"):
            errors.append("[D209] Multi-line docstring closing quotes should be on a separate line.")
    
    # D301: Use r""" if backslashes in docstring
    if any("\\" in line for line in lines):
        errors.append("[D301] Use r\"\"\" if any backslashes in a docstring.")
    
    # D206: Docstring should be indented with spaces, not tabs  
    if any("\t" in line for line in lines):
        errors.append("[D206] Docstring should be indented with spaces, not tabs.")
    
    # Try to validate with pydocstyle if available
    try:
        pydoc_errors = _validate_with_pydocstyle(docstring, function_name)
        # Add any D-code errors from pydocstyle that we haven't already caught
        for error in pydoc_errors:
            if not any(code in err for code in ["[D400]", "[D401]", "[D402]", "[D213]", "[D209]", "[D301]", "[D206]"] for err in errors):
                if error and error not in errors:
                    errors.append(error)
    except Exception:
        # pydocstyle validation failed, that's ok
        pass
    
    return errors


def _validate_with_pydocstyle(docstring: str, function_name: str = "temp_func"):
    """
    Validate using pydocstyle tool.
    
    Args:
        docstring: The docstring to validate
        function_name: Function name for context
    
    Returns:
        List of error strings
    """
    try:
        from pydocstyle import config, checker as pydoc_checker
        
        # Create temporary Python file
        temp_code = f'''def {function_name}():
    """{docstring}"""
    pass
'''
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(temp_code)
            temp_file = f.name
        
        try:
            # Check with pydocstyle
            cfg = config.Configuration()
            errors = []
            for error in pydoc_checker.check_file(temp_file, config=cfg):
                if hasattr(error, 'code') and hasattr(error, 'short_desc'):
                    errors.append(f"[{error.code}] {error.short_desc}")
            return errors
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    except Exception:
        # If pydocstyle fails, return empty list (falling back to manual checks)
        return []


def get_error_description(error_code: str) -> str:
    """
    Get a human-readable description for a PEP 257 error code.
    
    Args:
        error_code: The error code (e.g., "D401")
    
    Returns:
        Human-readable description
    """
    error_descriptions = {
        "D100": "Missing docstring in public module",
        "D101": "Missing docstring in public class",
        "D102": "Missing docstring in public method",
        "D103": "Missing docstring in public function",
        "D104": "Missing docstring in public package",
        "D105": "Missing docstring in magic method",
        "D200": "One-line docstring should fit on one line",
        "D201": "Multi-line docstring summary should be on one line",
        "D202": "No blank lines allowed after function docstring",
        "D203": "1 blank line required between class docstring and first method",
        "D204": "1 blank line required between docstring and doctest",
        "D205": "1 blank line required between summary line and description",
        "D206": "Docstring should be indented with spaces, not tabs",
        "D207": "Docstring is under-indented",
        "D208": "Docstring is over-indented",
        "D209": "Multi-line docstring closing quotes should be on a separate line",
        "D210": "No whitespaces around docstring",
        "D211": "No blank lines allowed before docstring",
        "D212": "Multi-line docstring summary should start at the first line",
        "D213": "Multi-line docstring summary should be on the first line",
        "D214": "Section is over-indented",
        "D215": "Section underline is over-indented",
        "D216": "Section underline is not indented",
        "D217": "Section underline without corresponding section",
        "D218": "Unnecessary leading whitespace before inline emphasis",
        "D219": "Unnecessary leading whitespace before inline code emphasis",
        "D220": "Inline code should be formatted with backticks",
        "D300": "Use \"\"\"triple double quotes\"\"\"",
        "D301": "Use r\"\"\" if any backslashes in a docstring",
        "D302": "Use u\"\"\" if any unicode in a docstring",
        "D400": "First line should end with a period",
        "D401": "First line should be in imperative mood",
        "D402": "First line should not be a function signature",
        "D403": "First word of the first argument should be capitalized in the summary",
        "D404": "First word of the docstring should not be 'This'",
        "D405": "Section name should be properly capitalized",
        "D406": "Section name should end with a colon",
        "D407": "Missing exception after Raises section",
        "D408": "Section (Raises) should have a colon after it",
        "D409": "Section has blank lines (Raises)",
        "D410": "Missing blank line after section (Raises)",
        "D411": "Missing blank line before section (Raises)",
        "D412": "No blank lines allowed between inline sections",
        "D413": "Missing blank line after last section (Parameters)",
        "D414": "Section has duplicate (Parameters)",
        "D415": "Short summary should end with period or semicolon",
        "D416": "Name in section is not properly formatted",
        "D417": "Missing argument description in the docstring",
        "D418": "Function decorated with @property should not have a docstring",
    }
    return error_descriptions.get(error_code, f"PEP 257 violation: {error_code}")


