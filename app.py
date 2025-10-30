"""
Faculty Allocation System - Streamlit UI
Interactive web application for student-faculty allocation
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from allocation_engine import AllocationEngine
from data_utils import (
    load_student_data, 
    validate_data, 
    save_allocation_output,
    save_statistics_output,
    format_statistics_for_display,
    generate_summary_report
)


# Page configuration
st.set_page_config(
    page_title="Faculty Allocation System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    """Main application"""
    
    # Header
    st.markdown('<div class="main-header">🎓 Faculty Allocation System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Intelligent student-faculty allocation based on CGPA and preferences</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📋 Instructions")
        st.markdown("""
        1. **Upload CSV File** with student preferences
        2. **Review** the data preview and validation
        3. **Run Allocation** algorithm
        4. **Download** results and statistics
        
        ---
        
        ### 📄 File Format
        **Required Columns:**
        - Roll, Name, Email, CGPA
        - Faculty columns (dynamic)
        
        **Faculty Columns:**
        - Values are preference ranks (1 to N)
        - 1 = highest preference
        - N = lowest preference
        
        ---
        
        ### 🧮 Algorithm
        - Students sorted by CGPA
        - Grouped into ⌈S/F⌉ groups
        - Each faculty gets 1 student per group
        - Based on best available preference
        """)
    
    # Initialize session state
    if 'allocation_done' not in st.session_state:
        st.session_state.allocation_done = False
    if 'engine' not in st.session_state:
        st.session_state.engine = None
    if 'allocation_df' not in st.session_state:
        st.session_state.allocation_df = None
    if 'statistics_df' not in st.session_state:
        st.session_state.statistics_df = None
    
    # File upload
    st.header("1️⃣ Upload Input File")
    uploaded_file = st.file_uploader(
        "Choose a CSV file with student preferences",
        type=['csv'],
        help="Upload the input file containing student details and faculty preferences"
    )
    
    if uploaded_file is not None:
        try:
            # Save uploaded file temporarily
            temp_path = "temp_input.csv"
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Load and validate data
            st.header("2️⃣ Data Preview & Validation")
            
            with st.spinner("Loading and validating data..."):
                students, faculty_list = load_student_data(temp_path)
                validation = validate_data(students, faculty_list)
            
            # Display validation results
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("👥 Total Students", validation['num_students'])
            with col2:
                st.metric("👨‍🏫 Total Faculty", validation['num_faculty'])
            with col3:
                import math
                num_groups = math.ceil(validation['num_students'] / validation['num_faculty']) if validation['num_faculty'] > 0 else 0
                st.metric("📦 Number of Groups", num_groups)
            
            # Show validation status
            if validation['valid']:
                st.success("✅ Data validation passed!")
            else:
                st.error("❌ Data validation failed!")
                for issue in validation['issues']:
                    st.error(f"  • {issue}")
            
            # Show warnings if any
            if validation['warnings']:
                with st.expander("⚠️ Warnings (click to expand)"):
                    for warning in validation['warnings']:
                        st.warning(f"  • {warning}")
            
            # Display data preview
            with st.expander("📊 Data Preview (first 10 rows)", expanded=True):
                preview_df = pd.read_csv(temp_path).head(10)
                st.dataframe(preview_df, use_container_width=True)
            
            # Faculty list
            with st.expander("👨‍🏫 Faculty List"):
                st.write(", ".join(faculty_list))
            
            # Allocation section
            st.header("3️⃣ Run Allocation")
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Run Allocation Algorithm", type="primary", use_container_width=True):
                    if validation['valid']:
                        with st.spinner("Running allocation algorithm..."):
                            # Create engine and run allocation
                            engine = AllocationEngine(students, faculty_list)
                            engine.allocate()
                            
                            # Get results
                            allocation_df = engine.get_allocation_summary()
                            statistics_df = engine.get_faculty_statistics()
                            
                            # Store in session state
                            st.session_state.allocation_done = True
                            st.session_state.engine = engine
                            st.session_state.allocation_df = allocation_df
                            st.session_state.statistics_df = statistics_df
                        
                        st.success("✅ Allocation completed successfully!")
                        st.balloons()
                    else:
                        st.error("⚠️ Please fix data validation issues before running allocation.")
            
            # Display results if allocation is done
            if st.session_state.allocation_done:
                st.header("4️⃣ Allocation Results")
                
                # Summary report
                with st.expander("📈 Summary Report", expanded=True):
                    report = generate_summary_report(
                        st.session_state.engine, 
                        st.session_state.allocation_df
                    )
                    st.code(report, language=None)
                
                # Tabs for different views
                tab1, tab2, tab3, tab4 = st.tabs([
                    "📋 Student Allocations", 
                    "📊 Faculty Statistics",
                    "📈 Visualizations",
                    "🔍 Analysis"
                ])
                
                with tab1:
                    st.subheader("Student Allocation Results")
                    st.dataframe(
                        st.session_state.allocation_df,
                        use_container_width=True,
                        height=400
                    )
                    
                    # Download button for allocation
                    csv_buffer = BytesIO()
                    st.session_state.allocation_df.to_csv(csv_buffer, index=False)
                    csv_buffer.seek(0)
                    
                    st.download_button(
                        label="📥 Download Student Allocations CSV",
                        data=csv_buffer,
                        file_name="output_btp_mtp_allocation.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with tab2:
                    st.subheader("Faculty Statistics (Preference Distribution)")
                    st.markdown("""
                    **Shows:** How many students listed each faculty as their Nth preference  
                    *(Each student ranks all {num_faculty} faculty)*
                    """.format(num_faculty=st.session_state.engine.num_faculty))
                    
                    display_stats = format_statistics_for_display(st.session_state.statistics_df)
                    
                    # Calculate and show totals
                    total_prefs = display_stats.iloc[:, 1:].sum().sum()
                    expected_total = len(st.session_state.engine.students) * st.session_state.engine.num_faculty
                    st.info(f"✅ Total preference entries: **{int(total_prefs)}** (Expected: {expected_total})")
                    
                    st.dataframe(
                        display_stats,
                        use_container_width=True,
                        height=400
                    )
                    
                    # Download button for statistics
                    csv_buffer2 = BytesIO()
                    st.session_state.statistics_df.to_csv(csv_buffer2, index=False)
                    csv_buffer2.seek(0)
                    
                    st.download_button(
                        label="📥 Download Faculty Statistics CSV",
                        data=csv_buffer2,
                        file_name="fac_preference_count.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with tab3:
                    st.subheader("Data Visualizations")
                    
                    # Faculty distribution bar chart
                    st.markdown("#### Students per Faculty")
                    fac_counts = st.session_state.allocation_df['Allocated'].value_counts()
                    fig1 = px.bar(
                        x=fac_counts.index,
                        y=fac_counts.values,
                        labels={'x': 'Faculty', 'y': 'Number of Students'},
                        title='Student Distribution Across Faculty'
                    )
                    fig1.update_traces(marker_color='#1f77b4')
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    # Preference distribution
                    st.markdown("#### Preference Achievement Distribution")
                    pref_data = []
                    for student in st.session_state.engine.students:
                        if student.allocated_faculty:
                            rank = student.preferences.get(student.allocated_faculty, 0)
                            pref_data.append(rank)
                    
                    fig2 = px.histogram(
                        x=pref_data,
                        nbins=validation['num_faculty'],
                        labels={'x': 'Preference Rank', 'y': 'Number of Students'},
                        title='Distribution of Preference Ranks Achieved'
                    )
                    fig2.update_traces(marker_color='#2ca02c')
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    # CGPA distribution by faculty
                    st.markdown("#### CGPA Distribution by Faculty")
                    fig3 = px.box(
                        st.session_state.allocation_df,
                        x='Allocated',
                        y='CGPA',
                        title='CGPA Distribution Across Faculty'
                    )
                    st.plotly_chart(fig3, use_container_width=True)
                
                with tab4:
                    st.subheader("Detailed Analysis")
                    
                    # Top students
                    st.markdown("#### 🏆 Top 10 Students by CGPA")
                    top_students = st.session_state.allocation_df.nlargest(10, 'CGPA')
                    st.dataframe(top_students, use_container_width=True)
                    
                    # Faculty with most first preferences
                    st.markdown("#### ⭐ Faculty Preference Analysis")
                    stats_df = st.session_state.statistics_df
                    if 'Count Pref 1' in stats_df.columns:
                        top_prefs = stats_df.nlargest(5, 'Count Pref 1')[['Fac', 'Count Pref 1']]
                        st.write("**Most Preferred Faculty (by 1st preference count):**")
                        st.dataframe(top_prefs, use_container_width=True, hide_index=True)
                    
                    # Search functionality
                    st.markdown("#### 🔍 Search Student Allocation")
                    search_term = st.text_input("Enter Roll Number or Name to search:")
                    if search_term:
                        results = st.session_state.allocation_df[
                            st.session_state.allocation_df['Roll'].str.contains(search_term, case=False, na=False) |
                            st.session_state.allocation_df['Name'].str.contains(search_term, case=False, na=False)
                        ]
                        if not results.empty:
                            st.dataframe(results, use_container_width=True)
                        else:
                            st.info("No results found.")
        
        except Exception as e:
            st.error(f"❌ Error processing file: {str(e)}")
            st.exception(e)
    
    else:
        # Show welcome message
        st.info("👆 Please upload a CSV file to begin")
        
        # Show example
        with st.expander("📝 Example Input Format"):
            example_data = {
                'Roll': ['1601CB01', '1601CB03', '1601CB04'],
                'Name': ['Student A', 'Student B', 'Student C'],
                'Email': ['a@email.com', 'b@email.com', 'c@email.com'],
                'CGPA': [8.5, 9.2, 7.8],
                'Faculty1': [2, 1, 3],
                'Faculty2': [1, 2, 1],
                'Faculty3': [3, 3, 2]
            }
            st.dataframe(pd.DataFrame(example_data), use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "Faculty Allocation System v1.0 | Built with Streamlit 🎈"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
