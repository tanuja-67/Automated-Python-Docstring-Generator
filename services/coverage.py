def generate_coverage_report(functions, approved_docstrings=None):
    """
    Generate a comprehensive documentation coverage report.
    
    Args:
        functions: List of function dicts from ast_parser
        approved_docstrings: Optional dict of approved docstrings for coverage after processing
    
    Returns:
        Dict with coverage metrics
    """
    approved_docstrings = approved_docstrings or {}
    
    total = len(functions)
    
    # Count initially documented functions
    documented = sum(1 for f in functions if f.get("has_docstring"))
    
    # Count functions with approved docstrings
    approved_count = sum(1 for f in functions if f['name'] in approved_docstrings or f.get('approved_docstring'))
    
    # Final count combines existing + newly approved
    final_documented = sum(1 for f in functions if f.get("has_docstring") or f['name'] in approved_docstrings or f.get('approved_docstring'))
    
    missing_initial = total - documented
    missing_final = total - final_documented
    
    coverage_initial = (documented / total * 100) if total else 0
    coverage_final = (final_documented / total * 100) if total else 0
    improvement = coverage_final - coverage_initial
    
    return {
        "total": total,
        "documented_initial": documented,
        "documented_final": final_documented,
        "newly_approved": approved_count,
        "missing_initial": missing_initial,
        "missing_final": missing_final,
        "coverage_initial": round(coverage_initial, 2),
        "coverage_final": round(coverage_final, 2),
        "improvement": round(improvement, 2),
        "missing_functions": [f["name"] for f in functions if not f["has_docstring"]],
        "already_documented": [f["name"] for f in functions if f["has_docstring"]],
    }
