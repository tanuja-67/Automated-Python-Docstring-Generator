import streamlit as st
from services.ast_parser import parse_functions
from services.coverage import generate_coverage_report
from services.docstring_generator import generate_docstring
from services.validator import validate_docstring
from services.code_inserter import apply_all_docstrings
from services.exporter import create_consolidated_file
from utils.file_utils import read_uploaded_file

# PAGE CONFIG & INITIALIZATION

st.set_page_config(
    page_title="Python Docstring Generator",
    page_icon="🐍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOM CSS STYLING

st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #4CAF50;
        --secondary-color: #2196F3;
        --accent-color: #FF9800;
        --success-color: #4CAF50;
        --warning-color: #FF9800;
        --error-color: #F44336;
        --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .main-header h1 {
        color: white !important;
        margin: 0;
        font-weight: 700;
    }
    
    .main-header p {
        color: rgba(255, 255, 255, 0.9) !important;
        margin: 0.5rem 0 0 0;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Container borders */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {
        border-radius: 10px;
    }
    
    /* Buttons - Primary */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(102, 126, 234, 0.4);
    }
    
    /* Buttons - Secondary */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button[kind="secondary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(245, 87, 108, 0.4);
    }
    
    /* Success messages */
    .stSuccess {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Warning messages */
    .stWarning {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Error messages */
    .stError {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Info messages */
    .stInfo {
        background-color: #d1ecf1;
        border-left: 4px solid #17a2b8;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Code blocks */
    .stCodeBlock {
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 1rem;
        background-color: rgba(102, 126, 234, 0.05);
    }
    
    /* Containers with borders */
    [data-testid="stVerticalBlock"]:has(> div[data-testid="element-container"]) {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
    }
    
    /* Dividers */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
    }
    
    /* Function header styling */
    h3 {
        color: #667eea;
        font-weight: 700;
    }
    
    /* Footer */
    .footer {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-top: 3rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'files_data' not in st.session_state:
    st.session_state.files_data = {}
if 'current_file_index' not in st.session_state:
    st.session_state.current_file_index = 0
if 'function_decisions' not in st.session_state:
    st.session_state.function_decisions = {}
if 'generated_docstrings' not in st.session_state:
    st.session_state.generated_docstrings = {}

# HEADER & SIDEBAR

# Modern header with gradient background
st.markdown("""
<div class="main-header">
    <h1>🐍 Python Docstring Generator</h1>
    <p>AI-powered docstring generation with human-in-the-loop approval workflow</p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("📁 Files Processed", len(st.session_state.files_data))

with col2:
    total_functions = sum(len(data["functions"]) for data in st.session_state.files_data.values())
    st.metric("🔧 Total Functions", total_functions)

with col3:
    accepted = sum(1 for d in st.session_state.function_decisions.values() if d.get("status") == "accepted")
    st.metric("✅ Approved", accepted)

st.divider()

# NAVBAR - CONFIGURATION OPTIONS

navbar_col1, navbar_col2, navbar_col3, navbar_col4 = st.columns(4)

with navbar_col1:
    style = st.selectbox(
        "📝 Docstring Style",
        ["Google", "NumPy", "reST"],
        help="Choose the docstring format (PEP 257 compliant)"
    )

with navbar_col2:
    export_format = st.selectbox(
        "📋 Export Format",
        ["Markdown", "Text", "Python"],
        help="Choose the format for exporting docstrings"
    )

with navbar_col3:
    st.write("")

with navbar_col4:
    st.write("")  # Empty space for alignment

st.divider()

# SIDEBAR - FILE UPLOAD & SETTINGS

with st.sidebar:
    st.header("📤 File Upload")
    
    # Clear/Reset button at the top
    if st.session_state.files_data:
        if st.button("🔄 Clear All & Start New", use_container_width=True, type="secondary"):
            st.session_state.files_data = {}
            st.session_state.function_decisions = {}
            st.session_state.generated_docstrings = {}
            st.session_state.current_file_index = 0
            st.success("✅ Cleared! Ready for new files")
            st.rerun()
        st.divider()
    
    uploaded_files = st.file_uploader(
        "Upload Python files",
        type=["py"],
        accept_multiple_files=True,
        help="Select one or more Python files to process"
    )
    
    code_input = st.text_area(
        "Or paste Python code",
        height=150,
        help="Alternatively, paste your Python code directly"
    )
    
    if uploaded_files:
        if st.button("📥 Load Files", use_container_width=True, type="primary"):
            # Clear previous data before loading new files
            st.session_state.files_data = {}
            st.session_state.function_decisions = {}
            st.session_state.generated_docstrings = {}
            
            for uploaded_file in uploaded_files:
                code = read_uploaded_file(uploaded_file)
                file_key = uploaded_file.name
                
                functions = parse_functions(code)
                
                st.session_state.files_data[file_key] = {
                    "filename": uploaded_file.name,
                    "code": code,
                    "functions": functions,
                    "report": generate_coverage_report(functions),
                }
            
            st.success(f"✅ Loaded {len(uploaded_files)} file(s)")
            st.rerun()
    
    elif code_input:
        if st.button("📝 Process Code", use_container_width=True, type="primary"):
            try:
                # Clear previous data before processing new code
                st.session_state.files_data = {}
                st.session_state.function_decisions = {}
                st.session_state.generated_docstrings = {}
                
                functions = parse_functions(code_input)
                st.session_state.files_data["pasted_code"] = {
                    "filename": "pasted_code.py",
                    "code": code_input,
                    "functions": functions,
                    "report": generate_coverage_report(functions),
                }
                st.success("✅ Code parsed successfully")
                st.rerun()
            except SyntaxError as e:
                st.error(f"❌ Syntax Error: {e}")

# MAIN CONTENT AREA

if not st.session_state.files_data:
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0;'>👋 Welcome to Python Docstring Generator!</h2>
        <p style='margin: 0.5rem 0; font-size: 1.1rem;'>Generate professional docstrings with AI assistance</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); height: 100%;'>
            <h3 style='color: #667eea; margin-top: 0;'>📋 How to Use</h3>
            <ol style='line-height: 2;'>
                <li><strong>Upload or Paste</strong> Python files in the sidebar</li>
                <li><strong>Select Style</strong> for generated docstrings</li>
                <li><strong>Review</strong> each function with AI-generated docstring</li>
                <li><strong>Accept, Edit, or Reject</strong> docstrings</li>
                <li><strong>Download</strong> updated files and consolidated docstrings</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: white; padding: 1.5rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); height: 100%;'>
            <h3 style='color: #764ba2; margin-top: 0;'>✨ Features</h3>
            <ul style='line-height: 2; list-style: none; padding-left: 0;'>
                <li>📊 Real-time documentation coverage analysis</li>
                <li>🤖 AI-powered docstring generation</li>
                <li>✏️ Edit generated docstrings before accepting</li>
                <li>📄 Export consolidated docstrings file</li>
                <li>✅ PEP 257 validation</li>
                <li>🎨 Multiple docstring styles supported</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.info("👈 **Get Started:** Upload Python files or paste code in the sidebar")


else:
    # File Selection Tabs
    if len(st.session_state.files_data) > 1:
        file_names = list(st.session_state.files_data.keys())
        file_tab = st.selectbox(
            "📂 Select File:",
            file_names,
            key="file_selector"
        )
        current_file = file_tab
    else:
        current_file = list(st.session_state.files_data.keys())[0]
    
    file_data = st.session_state.files_data[current_file]
    functions = file_data["functions"]
    report = file_data["report"]
    code = file_data["code"]
    
    # COVERAGE REPORT SECTION
    
    st.subheader("📊 Documentation Coverage Report")

    current_file_decisions = {
        func_id: decision
        for func_id, decision in st.session_state.function_decisions.items()
        if func_id.startswith(f"{current_file}_")
    }
    approved_docstrings = {
        decision["function"]["name"]: decision["docstring"]
         for decision in current_file_decisions.values()
         if decision.get("status") == "accepted" and decision.get("function")
     }
    accepted_function_keys = {
        (decision["function"].get("class_name"), decision["function"]["name"])
        for decision in current_file_decisions.values()
        if decision.get("status") == "accepted" and decision.get("function")
    }
    report = generate_coverage_report(functions, approved_docstrings=approved_docstrings)
    
    cov_col1, cov_col2, cov_col3, cov_col4, cov_col5 = st.columns(5)
    
    with cov_col1:
        st.metric("Total Functions", report["total"])
    
    with cov_col2:
        st.metric("Already Documented", report["documented_final"])
    
    with cov_col3:
        st.metric("To Review", report["missing_final"])
    
    with cov_col4:
        progress = report["coverage_final"]
        st.metric("Current Coverage", f"{progress}%")
    
    with cov_col5:
        st.metric("Potential Coverage", f"{report['coverage_final']}%")
    
    # Coverage Progress Bar
    if report["total"] > 0:
        st.progress(report["coverage_final"] / 100)
    
    st.divider()
    
    # FUNCTION REVIEW SECTION
    
    st.subheader("✋ Review & Approve Docstrings")
    
    functions_needing_docs = [
        f for f in functions
        if not f["has_docstring"] and (f.get("class_name"), f["name"]) not in accepted_function_keys
    ]
    functions_with_docs = [
        f for f in functions
        if f["has_docstring"] or (f.get("class_name"), f["name"]) in accepted_function_keys
    ]
    
    # Tabs for viewing functions
    tab1, tab2 = st.tabs([
        f"📝 Need Docstrings ({len(functions_needing_docs)})",
        f"✅ Already Documented ({len(functions_with_docs)})"
    ])
    
    with tab1:
        if functions_needing_docs:
            st.write(f"**{len(functions_needing_docs)} functions** need docstrings:")

            gen_col1, gen_col2, gen_col3 = st.columns([0.6, 0.2, 0.2])
            with gen_col1:
                st.caption("Generate docstrings for all functions in this file and review them below.")
            with gen_col2:
                if st.button("⚡ Generate All", use_container_width=True, type="primary"):
                    with st.spinner("Generating docstrings for all functions..."):
                        for idx, func in enumerate(functions_needing_docs):
                            func_id = f"{current_file}_{func['name']}_{idx}"
                            try:
                                doc = generate_docstring(
                                    func["source_code"],
                                    function_name=func["name"],
                                    args=func.get("args"),
                                    style=style
                                )
                                st.session_state.generated_docstrings[func_id] = doc
                            except Exception as e:
                                st.error(f"Error generating docstring for {func['name']}: {e}")
                        st.success("✅ All docstrings generated! Review and accept each one below.")
                        st.rerun()
            
            for idx, func in enumerate(functions_needing_docs):
                func_id = f"{current_file}_{func['name']}_{idx}"
                
                with st.container(border=True):
                    # Function header
                    func_name_display = f"{func['class_name']}.{func['name']}" if func.get('is_method') else func['name']
                    
                    col1, col2 = st.columns([0.85, 0.15])
                    with col1:
                        st.markdown(f"### 🔹 {func_name_display}()")
                        if func.get('args'):
                            st.caption(f"**Parameters:** {', '.join(func['args'])}")
                    
                    # Source code display
                    st.code(func["source_code"], language="python")
                    
                    # Generate docstring if not already done
                    if func_id not in st.session_state.generated_docstrings:
                        if st.button(f"🤖 Generate Docstring", key=f"gen_{func_id}"):
                            with st.spinner("Generating docstring..."):
                                try:
                                    doc = generate_docstring(
                                        func["source_code"],
                                        function_name=func["name"],
                                        args=func.get("args"),
                                        style=style
                                    )
                                    st.session_state.generated_docstrings[func_id] = doc
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error generating docstring: {e}")
                    
                    # Display and interact with docstring
                    if func_id in st.session_state.generated_docstrings:
                        generated_doc = st.session_state.generated_docstrings[func_id]
                        decision = st.session_state.function_decisions.get(func_id)
                        displayed_doc = decision.get("docstring") if decision and decision.get("status") == "accepted" else generated_doc
                        
                        st.markdown("**📝 Generated Docstring:**")
                        st.code(f'"""{displayed_doc}"""', language="python", line_numbers=False)
                        
                        # Check if editing mode
                        if func_id in st.session_state.function_decisions and st.session_state.function_decisions[func_id].get("status") == "editing":
                            st.markdown("**✏️ Edit Docstring:**")
                            edited_doc = st.text_area(
                                "Modify the docstring and it will be shown in the preview:",
                                value=displayed_doc,
                                height=150,
                                key=f"edit_area_{func_id}",
                                label_visibility="collapsed"
                            )
                            
                            # Show preview of edited version
                            st.markdown("**Preview of edited docstring:**")
                            edit_errors = validate_docstring(edited_doc, function_name=func['name'])
                            if edit_errors:
                                st.warning(f"⚠️ {len(edit_errors)} validation issue(s)")
                                for error in edit_errors:
                                    st.caption(error)
                            else:
                                st.success("✅ PEP 257 compliant")
                            st.code(f'"""{edited_doc}"""', language="python", line_numbers=False)
                            
                            # Save or Cancel
                            save_col1, save_col2, save_col3 = st.columns([0.4, 0.3, 0.3])
                            with save_col1:
                                if st.button(
                                    "💾 Save & Accept Edit",
                                    key=f"save_edit_{func_id}",
                                    use_container_width=True,
                                    type="primary"
                                ):
                                    st.session_state.function_decisions[func_id] = {
                                        "status": "accepted",
                                        "docstring": edited_doc,
                                        "function": func
                                    }
                                    st.session_state.generated_docstrings[func_id] = edited_doc
                                    st.success("✅ Changes saved and accepted!")
                                    st.rerun()
                            
                            with save_col2:
                                if st.button("✖️ Cancel Edit", key=f"cancel_edit_{func_id}", use_container_width=True):
                                    if func_id in st.session_state.function_decisions:
                                        del st.session_state.function_decisions[func_id]
                                    st.rerun()
                        
                        # Action buttons (only show if not editing)
                        if not (func_id in st.session_state.function_decisions and st.session_state.function_decisions[func_id].get("status") == "editing"):
                            st.markdown("**Choose an action:**")
                            btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
                            
                            with btn_col1:
                                if st.button("✅ Accept", key=f"accept_{func_id}", use_container_width=True, type="primary"):
                                    st.session_state.function_decisions[func_id] = {
                                        "status": "accepted",
                                        "docstring": displayed_doc,
                                        "function": func
                                    }
                                    st.rerun()
                            
                            with btn_col2:
                                if st.button("✏️ Modify", key=f"edit_{func_id}", use_container_width=True):
                                    st.session_state.function_decisions[func_id] = {
                                        "status": "editing",
                                        "docstring": displayed_doc,
                                        "function": func
                                    }
                                    st.rerun()
                            
                            with btn_col3:
                                if st.button("🔍 Validate", key=f"validate_{func_id}", use_container_width=True):
                                    errors = validate_docstring(displayed_doc, function_name=func['name'])
                                    st.divider()
                                    if errors:
                                        error_count = len(errors)
                                        error_text = "error" if error_count == 1 else "errors"
                                        st.error(f"⚠️ **{error_count} PEP 257 Validation {error_text}:**")
                                        for i, error in enumerate(errors, 1):
                                            st.markdown(f"**{i}. {error}**")
                                    else:
                                        st.success("✅ PEP 257 fully compliant!")
                                    st.divider()
                            
                            with btn_col4:
                                if st.button("❌ Reject", key=f"reject_{func_id}", use_container_width=True):
                                    st.session_state.function_decisions[func_id] = {"status": "rejected"}
                                    st.rerun()
                        
                        # Status indicator
                        if func_id in st.session_state.function_decisions:
                            decision = st.session_state.function_decisions[func_id]
                            if decision.get("status") == "accepted":
                                st.success("✅ **Status: Accepted** - Will be included in download")
                            elif decision.get("status") == "rejected":
                                st.warning("❌ **Status: Rejected** - Skipped")
        else:
            st.success("✅ All functions have docstrings!")
    
    with tab2:
        if functions_with_docs:
            st.write(f"**{len(functions_with_docs)} functions** have docstrings:")
            
            for func in functions_with_docs:
                func_name_display = f"{func['class_name']}.{func['name']}" if func.get('is_method') else func['name']
                func_key = (func.get("class_name"), func["name"])
                
                # Find if this function has an approved docstring
                approved_doc = None
                for decision in current_file_decisions.values():
                    if (decision.get("function", {}).get("class_name") == func.get("class_name") and 
                        decision.get("function", {}).get("name") == func["name"] and
                        decision.get("status") == "accepted"):
                        approved_doc = decision.get("docstring")
                        break
                
                with st.container(border=True):
                    st.markdown(f"### ✅ {func_name_display}()")
                    if func.get('args'):
                        st.caption(f"**Parameters:** {', '.join(func['args'])}")
                    
                    st.code(func["source_code"], language="python")
                    
                    # Show approved docstring first if available (newly accepted)
                    if approved_doc:
                        st.markdown("**✨ Approved Docstring (Generated & Accepted):**")
                        st.code(f'"""{approved_doc}"""', language="python")
                    # Then show existing docstring if different
                    elif func.get('docstring'):
                        st.markdown("**📝 Existing Docstring:**")
                        st.code(f'"""{func["docstring"]}"""', language="python")
        else:
            st.info("No documented functions yet. Generate and accept docstrings to see them here!")
    
    st.divider()
    
    # DOWNLOAD & EXPORT SECTION
   
    
    st.subheader("📥 Download & Export")
    
    # Count accepted docstrings
    accepted_count = sum(1 for d in st.session_state.function_decisions.values() if d.get("status") == "accepted")
    
    if accepted_count > 0:
        st.info(f"✅ **{accepted_count} docstring(s) approved** - Ready to download!")
        
        # Prepare the updated code
        docstrings_to_apply = {}
        for func_id, decision in st.session_state.function_decisions.items():
            if decision.get("status") == "accepted":
                func = decision.get("function")
                if func:
                    func_name = func["name"]
                    if func.get("is_method"):
                        func_key = f"{func['class_name']}.{func_name}"
                    else:
                        func_key = func_name
                    docstrings_to_apply[func_key] = decision["docstring"]

        updated_code = apply_all_docstrings(code, docstrings_to_apply)
        
        # LIVE FILE PREVIEW
        st.markdown("### 📋 Final Code Preview (Before & After)")
        
        with st.expander("👁️ View Before/After Comparison", expanded=True):
            prev_col1, prev_col2 = st.columns(2)
            
            with prev_col1:
                st.markdown("**BEFORE** (Original Code)")
                st.code(code, language="python", line_numbers=True)
            
            with prev_col2:
                st.markdown("**AFTER** (With Docstrings)")
                st.code(updated_code, language="python", line_numbers=True)
        
        # DOWNLOAD BUTTONS
        
        
        st.markdown("### ⬇️ Download Options")
        
        download_col1, download_col2 = st.columns(2)
        
        with download_col1:
            st.markdown("**Updated Python File**")
            try:
                st.download_button(
                    label="📥 Download Updated File",
                    data=updated_code,
                    file_name=file_data["filename"],
                    mime="text/plain",
                    use_container_width=True,
                    type="primary"
                )
            except Exception as e:
                st.error(f"Error: {e}")
        
        with download_col2:
            st.markdown("**Consolidated Docstrings**")
            try:
                # Prepare consolidated docstrings export
                approved_functions = []
                for func_id, decision in st.session_state.function_decisions.items():
                    if decision.get("status") == "accepted":
                        func = decision.get("function")
                        if func:
                            func_copy = func.copy()
                            func_copy["approved_docstring"] = decision["docstring"]
                            func_copy["filename"] = file_data["filename"]
                            approved_functions.append(func_copy)
                
                if approved_functions:
                    export_format_lower = export_format.lower()
                    content, ext = create_consolidated_file(
                        approved_functions,
                        filename="generated_docstrings",
                        format_type=export_format_lower
                    )
                    
                    st.download_button(
                        label=f"📄 Download {export_format}",
                        data=content,
                        file_name=f"generated_docstrings.{ext}",
                        mime="text/plain" if ext != "py" else "text/x-python",
                        use_container_width=True,
                        type="primary"
                    )
            except Exception as e:
                st.error(f"Error preparing export: {e}")
    
    else:
        st.warning("👆 **Accept at least one docstring above** to see the preview and download options")

# FOOTER

st.divider()
st.markdown("""
<div class="footer">
    <h3 style="color: white; margin: 0;">🐍 Python Docstring Generator</h3>
    <p style="margin: 0.5rem 0; font-size: 1rem;">Built with Streamlit & AI</p>
    <p style="margin: 0.5rem 0; opacity: 0.9;">Supports Google, NumPy, and reST docstring styles • PEP 257 Compliant</p>
    <div style="margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid rgba(255,255,255,0.2);">
        <p style="margin: 0; font-size: 0.9rem; opacity: 0.8;">© 2026 • Version 2.0</p>
    </div>
</div>
""", unsafe_allow_html=True)
