"""
Guide Assignment System - Streamlit Interface
A web application for matching students with faculty guides.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import sys
from pathlib import Path
import math

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

# --- Mock imports for testing if modules are not found ---
# In a real scenario, these files (allocation_engine.py, data_utils.py)
# must exist in the same directory.

try:
    from allocation_engine import AllocationEngine
    from data_utils import (
        load_student_data, 
        validate_data, 
        save_allocation_output,
        save_statistics_output,
        format_statistics_for_display,
        generate_summary_report
    )
except ImportError:
    st.error("Error: Could not find 'allocation_engine.py' or 'data_utils.py'.")
    st.stop()
# ---------------------------------------------------------


# Page configuration
st.set_page_config(
    page_title="Guide Assignment Tool",
    page_icon="🧑‍🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# New custom CSS with hover effects and darker font
st.markdown("""
    <style>
    :root {
        --theme-color: #2a9d8f;
        --text-muted: #5c6c75;
        --card-background: #ffffff;
        --app-background: #f8f9fa;
        --highlight: #e9c46a;
    }
    .stApp {
        background-color: var(--app-background);
        /* Set to a very dark gray for the font */
        color: #212529; 
    }
    .title-container {
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 12px 0;
    }
    .logo-box {
        width: 56px;
        height: 56px;
        background: var(--theme-color);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1.2rem;
        box-shadow: 0 4px 14px rgba(42,157,143,0.15);
    }
    .header-title {
        font-size: 1.6rem;
        font-weight: 700;
        margin: 0;
    }
    .header-subtitle {
        font-size: 0.95rem;
        color: var(--text-muted);
        margin: 0;
    }
    
    /* --- METRIC CARD HOVER --- */
    .info-widget {
        background: var(--card-background);
        padding: 10px 14px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(15,23,42,0.04);
        margin-bottom: 8px;
        /* Added transition for smooth hover */
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    .info-widget:hover {
        /* Lifts the card up */
        transform: translateY(-3px);
        /* Makes the shadow stronger */
        box-shadow: 0 8px 20px rgba(15,23,42,0.08);
    }
    
    /* --- MAIN BUTTON HOVER --- */
    .action-button-container .stButton>button{
        background: linear-gradient(90deg,var(--theme-color),#2ebfad)!important;
        color: white !important;
        border-radius: 8px;
        padding: 10px 18px;
        box-shadow: 0 6px 18px rgba(42,157,143,0.15);
        /* Added transition for smooth hover */
        transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    .action-button-container .stButton>button:hover {
        /* Lifts the button up */
        transform: translateY(-2px);
        /* Makes the shadow stronger */
        box-shadow: 0 8px 22px rgba(42,157,143,0.25);
    }

    /* --- EXAMPLE BUTTON HOVER --- */
    .example-download-button .stButton>button{
        background: transparent !important;
        color: var(--theme-color) !important;
        border: 1px dashed rgba(42,157,143,0.2) !important;
        /* Added transition for smooth hover */
        transition: background-color 0.2s ease-in-out, color 0.2s ease-in-out;
    }
    .example-download-button .stButton>button:hover {
        /* Fills the button with color */
        background-color: var(--theme-color) !important;
        /* Changes text to white */
        color: white !important;
    }

    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)


def run_app():
    """Main application function"""

    # Initialize session state at the top
    st.session_state.setdefault('has_run', False)
    st.session_state.setdefault('allocator', None)
    st.session_state.setdefault('results_df', None)
    st.session_state.setdefault('stats_df', None)

    # Header
    st.markdown(
        """
        <div class="title-container">
            <div class="logo-box">GA</div>
            <div>
                <div class="header-title">Guide Assignment Tool 🧑‍🏫</div>
                <div class="header-subtitle">Assigning students to faculty guides based on CGPA & preferences</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Sidebar
    with st.sidebar:
        st.header("📖 How to Use")
        st.markdown("""
        1.  **Upload** your CSV file.
        2.  **Verify** the data preview and checks.
        3.  **Execute** the assignment algorithm.
        4.  **Download** the generated results.
        
        ---
        
        ### 📄 File Requirements
        **Columns Needed:**
        -   Roll, Name, Email, CGPA
        -   One column per faculty
        
        **Faculty Columns:**
        -   Must contain preference ranks (1 to N).
        -   `1` is the highest preference.
        -   `N` is the lowest.
        
        ---
        
        ### ⚙️ Logic Overview
        -   Students are sorted by CGPA (descending).
        -   They are split into ⌈Students/Faculty⌉ groups.
        -   Each faculty picks one student per group based on the best available preference.
        """)
    
    # File upload section
    st.header("1. Upload Student Data")
    uploaded_file = st.file_uploader(
        "Select a CSV file containing student preferences",
        type=['csv'],
        help="Upload the input file with student details and faculty preference ranks"
    )
    
    if uploaded_file is not None:
        try:
            # Save uploaded file
            input_file_path = "temp_input_data.csv"
            with open(input_file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Load and validate
            st.header("2. Validate Input")
            
            with st.spinner("Loading and checking data..."):
                students, faculty_list = load_student_data(input_file_path)
                data_check = validate_data(students, faculty_list)
            
            # Display metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                # Use the 'info-widget' class for the metric
                st.markdown(
                    f'<div class="info-widget">Student Count<br><h2>{data_check["num_students"]}</h2></div>', 
                    unsafe_allow_html=True
                )
            with col2:
                st.markdown(
                    f'<div class="info-widget">Faculty Count<br><h2>{data_check["num_faculty"]}</h2></div>', 
                    unsafe_allow_html=True
                )
            with col3:
                num_groups = math.ceil(data_check['num_students'] / data_check['num_faculty']) if data_check['num_faculty'] > 0 else 0
                st.markdown(
                    f'<div class="info-widget">Allocation Groups<br><h2>{num_groups}</h2></div>', 
                    unsafe_allow_html=True
                )
            
            # Validation status
            if data_check['valid']:
                st.success("✅ Data validation passed successfully!")
            else:
                st.error("❌ Data validation failed!")
                for issue in data_check['issues']:
                    st.error(f"  • {issue}")
            
            if data_check['warnings']:
                with st.expander("⚠️ View Warnings"):
                    for warning in data_check['warnings']:
                        st.warning(f"  • {warning}")
            
            # Data preview
            with st.expander("📊 Preview Input Data (First 10 Rows)", expanded=True):
                preview_df = pd.read_csv(input_file_path).head(10)
                st.dataframe(preview_df, use_container_width=True)
            
            with st.expander("👨‍🏫 Detected Faculty List"):
                st.write(", ".join(faculty_list))
            
            # Allocation section
            st.header("3. Process Allocation")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown('<div class="action-button-container">', unsafe_allow_html=True)
                if st.button("🚀 Start Allocation", type="primary", use_container_width=True):
                    if data_check['valid']:
                        with st.spinner("Running assignment algorithm..."):
                            # Create engine and run
                            allocator = AllocationEngine(students, faculty_list)
                            allocator.allocate()
                            
                            # Get results
                            results_df = allocator.get_allocation_summary()
                            stats_df = allocator.get_faculty_statistics()
                            
                            # Store in session state
                            st.session_state.has_run = True
                            st.session_state.allocator = allocator
                            st.session_state.results_df = results_df
                            st.session_state.stats_df = stats_df
                        
                        st.success("✅ Assignment complete!")
                        st.balloons()
                    else:
                        st.error("⚠️ Please correct the data issues before running.")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Display results
            if st.session_state.has_run:
                st.header("4. View Results")
                
                with st.expander("📈 Summary Report", expanded=True):
                    report = generate_summary_report(
                        st.session_state.allocator, 
                        st.session_state.results_df
                    )
                    st.code(report, language=None)
                
                # Tabs
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📋 Allocation List", 
                    "📊 Faculty Preferences",
                    "📈 Charts",
                    "🔍 Data Insights"
                ])
                
                with tab1:
                    st.subheader("Final Student Assignments")
                    st.dataframe(
                        st.session_state.results_df,
                        use_container_width=True,
                        height=400
                    )
                    
                    # Download
                    csv_export_buffer_1 = BytesIO()
                    st.session_state.results_df.to_csv(csv_export_buffer_1, index=False)
                    csv_export_buffer_1.seek(0)
                    
                    st.download_button(
                        label="📥 Download Student Allocations (CSV)",
                        data=csv_export_buffer_1,
                        file_name="student_assignments.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with tab2:
                    st.subheader("Faculty Preference Statistics")
                    st.markdown(f"""
                    This table shows how many students ranked each faculty as their Nth preference.
                    *(Total students: {len(st.session_state.allocator.students)})*
                    """)
                    
                    display_stats = format_statistics_for_display(st.session_state.stats_df)
                    
                    total_prefs = display_stats.iloc[:, 1:].sum().sum()
                    expected_total = len(st.session_state.allocator.students) * st.session_state.allocator.num_faculty
                    st.info(f"✅ Total preferences counted: **{int(total_prefs)}** (Expected: {expected_total})")
                    
                    st.dataframe(
                        display_stats,
                        use_container_width=True,
                        height=400
                    )
                    
                    # Download
                    csv_export_buffer_2 = BytesIO()
                    st.session_state.stats_df.to_csv(csv_export_buffer_2, index=False)
                    csv_export_buffer_2.seek(0)
                    
                    st.download_button(
                        label="📥 Download Faculty Statistics (CSV)",
                        data=csv_export_buffer_2,
                        file_name="faculty_preference_stats.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with tab3:
                    st.subheader("Visualizations")
                    
                    st.markdown("#### Students per Faculty")
                    fac_counts = st.session_state.results_df['Allocated'].value_counts()
                    faculty_count_chart = px.bar(
                        x=fac_counts.index,
                        y=fac_counts.values,
                        labels={'x': 'Faculty', 'y': 'Number of Students'},
                        title='Student Distribution Across Faculty'
                    )
                    faculty_count_chart.update_traces(marker_color='#2a9d8f')
                    st.plotly_chart(faculty_count_chart, use_container_width=True)
                    
                    st.markdown("#### Preference Achievement Distribution")
                    pref_data = [
                        s.preferences.get(s.allocated_faculty, 0) 
                        for s in st.session_state.allocator.students if s.allocated_faculty
                    ]
                    
                    pref_rank_chart = px.histogram(
                        x=pref_data,
                        nbins=data_check['num_faculty'],
                        labels={'x': 'Preference Rank', 'y': 'Number of Students'},
                        title='Distribution of Preference Ranks Achieved'
                    )
                    pref_rank_chart.update_traces(marker_color='#264653')
                    st.plotly_chart(pref_rank_chart, use_container_width=True)
                    
                    st.markdown("#### CGPA Distribution by Faculty")
                    cgpa_box_plot = px.box(
                        st.session_state.results_df,
                        x='Allocated',
                        y='CGPA',
                        title='CGPA Distribution Across Faculty'
                    )
                    st.plotly_chart(cgpa_box_plot, use_container_width=True)
                
                with tab4:
                    st.subheader("Detailed Insights")
                    
                    st.markdown("#### 🏆 Top 10 Students by CGPA")
                    top_students = st.session_state.results_df.nlargest(10, 'CGPA')
                    st.dataframe(top_students, use_container_width=True)
                    
                    st.markdown("#### ⭐ Faculty Preference Analysis")
                    stats_df = st.session_state.stats_df
                    if 'Count Pref 1' in stats_df.columns:
                        top_prefs = stats_df.nlargest(5, 'Count Pref 1')[['Fac', 'Count Pref 1']]
                        st.write("**Most In-Demand Faculty (by 1st preference):**")
                        st.dataframe(top_prefs, use_container_width=True, hide_index=True)
                    
                    st.markdown("#### 🔍 Search Student")
                    search_term = st.text_input("Enter Roll Number or Name:")
                    if search_term:
                        results = st.session_state.results_df[
                            st.session_state.results_df['Roll'].str.contains(search_term, case=False, na=False) |
                            st.session_state.results_df['Name'].str.contains(search_term, case=False, na=False)
                        ]
                        if not results.empty:
                            st.dataframe(results, use_container_width=True)
                        else:
                            st.info("No matching students found.")
        
        except Exception as e:
            st.error(f"❌ A critical error occurred: {str(e)}")
            st.exception(e)
    
    else:
        # Welcome message
        st.info("👆 Please upload a CSV file to begin the assignment process")

        with st.expander("📝 View Example Input Format", expanded=True):
            example_data = {
                'Roll': ['S201', 'S202', 'S203'],
                'Name': ['Amit Kumar', 'Priya Sharma', 'Rohan Verma'],
                'Email': ['amit@test.com', 'priya@test.com', 'rohan@test.com'],
                'CGPA': [9.1, 8.8, 9.3],
                'Guide_A': [1, 3, 1],
                'Guide_B': [2, 1, 3],
                'Guide_C': [3, 2, 2]
            }
            df_example = pd.DataFrame(example_data)
            st.dataframe(df_example, use_container_width=True)

            try:
                csv_bytes = df_example.to_csv(index=False).encode('utf-8')
                st.markdown('<div class="example-download-button">', unsafe_allow_html=True)
                st.download_button(
                    label="📥 Download Example CSV",
                    data=csv_bytes,
                    file_name='example_guide_input.csv',
                    mime='text/csv',
                    use_container_width=False
                )
                st.markdown('</div>', unsafe_allow_html=True)
            except Exception:
                pass
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #888;'>"
        "Guide Assignment System v1.1 | Powered by Streamlit 🎈"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    run_app()