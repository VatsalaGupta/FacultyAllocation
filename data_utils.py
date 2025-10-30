"""
Data Utilities
Functions for loading, validating, and saving allocation data
"""

import pandas as pd
from typing import List, Tuple, Dict
from allocation_engine import Student


def load_student_data(filepath: str) -> Tuple[List[Student], List[str]]:
    """
    Load student data from CSV file
    
    Args:
        filepath: Path to input CSV file
        
    Returns:
        Tuple of (list of Student objects, list of faculty names)
    """
    # Read CSV file
    df = pd.read_csv(filepath)
    
    # Extract faculty list (columns after CGPA)
    # Expected columns: Roll, Name, Email, CGPA, Faculty1, Faculty2, ...
    basic_columns = ['Roll', 'Name', 'Email', 'CGPA']
    faculty_list = [col for col in df.columns if col not in basic_columns]
    
    # Create Student objects
    students = []
    for _, row in df.iterrows():
        # Extract basic info
        roll = str(row['Roll'])
        name = str(row['Name'])
        email = str(row['Email'])
        cgpa = float(row['CGPA'])
        
        # Extract preferences (faculty_name -> preference_rank)
        preferences = {}
        for faculty in faculty_list:
            pref_rank = int(row[faculty])
            preferences[faculty] = pref_rank
        
        # Create student object
        student = Student(roll, name, email, cgpa, preferences)
        students.append(student)
    
    return students, faculty_list


def validate_data(students: List[Student], faculty_list: List[str]) -> Dict[str, any]:
    """
    Validate input data for consistency
    
    Returns:
        Dictionary with validation results and warnings
    """
    issues = []
    warnings = []
    
    num_students = len(students)
    num_faculty = len(faculty_list)
    
    # Check if we have data
    if num_students == 0:
        issues.append("No students found in input file")
    
    if num_faculty == 0:
        issues.append("No faculty found in input file")
    
    # Check for duplicate roll numbers
    roll_numbers = [s.roll for s in students]
    if len(roll_numbers) != len(set(roll_numbers)):
        issues.append("Duplicate roll numbers found")
    
    # Check preference ranges
    for student in students:
        for faculty, rank in student.preferences.items():
            if rank < 1 or rank > num_faculty:
                warnings.append(
                    f"Student {student.roll} has invalid preference {rank} for {faculty}"
                )
    
    # Check for duplicate preferences in a student
    for student in students:
        pref_values = list(student.preferences.values())
        if len(pref_values) != len(set(pref_values)):
            warnings.append(
                f"Student {student.roll} has duplicate preference ranks"
            )
    
    # Check CGPA ranges
    for student in students:
        if student.cgpa < 0 or student.cgpa > 10:
            warnings.append(
                f"Student {student.roll} has unusual CGPA: {student.cgpa}"
            )
    
    return {
        'valid': len(issues) == 0,
        'issues': issues,
        'warnings': warnings,
        'num_students': num_students,
        'num_faculty': num_faculty
    }


def save_allocation_output(allocation_df: pd.DataFrame, output_filepath: str):
    """
    Save allocation results to CSV file
    
    Args:
        allocation_df: DataFrame with Roll, Name, Email, CGPA, Allocated
        output_filepath: Path to save output CSV
    """
    allocation_df.to_csv(output_filepath, index=False)


def save_statistics_output(statistics_df: pd.DataFrame, output_filepath: str):
    """
    Save faculty statistics to CSV file
    
    Args:
        statistics_df: DataFrame with faculty and preference counts
        output_filepath: Path to save statistics CSV
    """
    statistics_df.to_csv(output_filepath, index=False)


def get_data_preview(filepath: str, num_rows: int = 5) -> pd.DataFrame:
    """
    Get a preview of the input file
    
    Args:
        filepath: Path to CSV file
        num_rows: Number of rows to preview
        
    Returns:
        DataFrame with first num_rows
    """
    df = pd.read_csv(filepath)
    return df.head(num_rows)


def format_statistics_for_display(statistics_df: pd.DataFrame) -> pd.DataFrame:
    """
    Format statistics DataFrame for better display
    Keep 0 values to avoid Arrow serialization issues
    """
    display_df = statistics_df.copy()
    
    # Ensure all count columns are integers
    count_columns = [col for col in display_df.columns if col.startswith('Count Pref')]
    for col in count_columns:
        display_df[col] = display_df[col].astype(int)
    
    return display_df


def generate_summary_report(engine, allocation_df: pd.DataFrame) -> str:
    """
    Generate a text summary report of the allocation
    
    Args:
        engine: AllocationEngine instance
        allocation_df: Allocation results DataFrame
        
    Returns:
        Formatted text report
    """
    metrics = engine.get_allocation_metrics()
    
    report = f"""
    ╔════════════════════════════════════════════════════════════╗
    ║          FACULTY ALLOCATION SUMMARY REPORT                 ║
    ╚════════════════════════════════════════════════════════════╝
    
    📊 BASIC STATISTICS
    ─────────────────────────────────────────────────────────────
    Total Students:              {metrics['total_students']}
    Total Faculty:               {metrics['total_faculty']}
    Number of Groups:            {metrics['num_groups']}
    Students Allocated:          {metrics['allocated_students']}
    
    📈 ALLOCATION QUALITY
    ─────────────────────────────────────────────────────────────
    Average Preference Rank:     {metrics['average_preference_rank']} 
                                 (lower is better, 1 = first choice)
    
    👥 FACULTY DISTRIBUTION
    ─────────────────────────────────────────────────────────────
    Min Students per Faculty:    {metrics['min_students_per_faculty']}
    Max Students per Faculty:    {metrics['max_students_per_faculty']}
    
    ✨ ALLOCATION SUCCESS
    ─────────────────────────────────────────────────────────────
    """
    
    # Count how many got their top 3 preferences
    top_1 = top_2 = top_3 = 0
    for student in engine.students:
        if student.allocated_faculty:
            rank = student.preferences.get(student.allocated_faculty, 999)
            if rank == 1:
                top_1 += 1
            if rank <= 2:
                top_2 += 1
            if rank <= 3:
                top_3 += 1
    
    total = metrics['allocated_students']
    if total > 0:
        report += f"""
    Students got 1st preference:  {top_1} ({top_1*100/total:.1f}%)
    Students got top-2 preference: {top_2} ({top_2*100/total:.1f}%)
    Students got top-3 preference: {top_3} ({top_3*100/total:.1f}%)
    """
    
    return report
