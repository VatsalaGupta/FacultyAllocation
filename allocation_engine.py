"""
Faculty Allocation Engine
Core algorithm for allocating students to faculty based on CGPA and preferences
"""

import math
from typing import List, Dict, Tuple
import pandas as pd


class Student:
    """Represents a student with their details and preferences"""
    
    def __init__(self, roll: str, name: str, email: str, cgpa: float, preferences: Dict[str, int]):
        self.roll = roll
        self.name = name
        self.email = email
        self.cgpa = cgpa
        self.preferences = preferences  # {faculty_name: preference_rank}
        self.allocated_faculty = None
    
    def get_best_available_faculty(self, available_faculty: set) -> Tuple[str, int]:
        """
        Find the best (lowest rank) available faculty for this student
        Returns: (faculty_name, preference_rank)
        """
        best_faculty = None
        best_rank = float('inf')
        
        for faculty in available_faculty:
            rank = self.preferences.get(faculty, float('inf'))
            if rank < best_rank:
                best_rank = rank
                best_faculty = faculty
        
        return best_faculty, best_rank
    
    def __repr__(self):
        return f"Student({self.roll}, CGPA={self.cgpa})"


class AllocationEngine:
    """Main allocation engine implementing the greedy algorithm"""
    
    def __init__(self, students: List[Student], faculty_list: List[str]):
        self.students = students
        self.faculty_list = faculty_list
        self.num_students = len(students)
        self.num_faculty = len(faculty_list)
        self.num_groups = math.ceil(self.num_students / self.num_faculty)
        
    def sort_students_by_merit(self) -> List[Student]:
        """
        Sort students by CGPA (descending), then by Roll (ascending)
        """
        return sorted(
            self.students,
            key=lambda s: (-s.cgpa, s.roll)  # Negative CGPA for descending
        )
    
    def create_groups(self, sorted_students: List[Student]) -> List[List[Student]]:
        """
        Divide sorted students into groups of size = num_faculty
        Last group may have fewer students
        """
        groups = []
        for i in range(0, self.num_students, self.num_faculty):
            group = sorted_students[i:i + self.num_faculty]
            groups.append(group)
        
        return groups
    
    def allocate(self) -> Dict[str, str]:
        """
        Main allocation algorithm
        Returns: Dictionary mapping student roll to allocated faculty
        """
        # Step 1: Sort students by merit
        sorted_students = self.sort_students_by_merit()
        
        # Step 2: Create groups
        groups = self.create_groups(sorted_students)
        
        # Step 3: Allocate faculty for each group
        allocations = {}
        
        for group_idx, group in enumerate(groups):
            # Each group starts with all faculty available
            available_faculty = set(self.faculty_list)
            
            for student in group:
                # Find best available faculty for this student
                best_faculty, best_rank = student.get_best_available_faculty(available_faculty)
                
                if best_faculty:
                    # Allocate student to faculty
                    student.allocated_faculty = best_faculty
                    allocations[student.roll] = best_faculty
                    
                    # Remove faculty from available pool for this group
                    available_faculty.remove(best_faculty)
                else:
                    # Should not happen if data is valid
                    allocations[student.roll] = "UNALLOCATED"
        
        return allocations
    
    def get_allocation_summary(self) -> pd.DataFrame:
        """
        Get summary of allocation results
        Returns: DataFrame with Roll, Name, Email, CGPA, Allocated
        """
        data = []
        for student in self.students:
            data.append({
                'Roll': student.roll,
                'Name': student.name,
                'Email': student.email,
                'CGPA': student.cgpa,
                'Allocated': student.allocated_faculty or 'UNALLOCATED'
            })
        
        return pd.DataFrame(data)
    
    def get_faculty_statistics(self) -> pd.DataFrame:
        """
        Calculate preference statistics for each faculty
        Shows: How many students listed this faculty as their Nth preference
        (Counts ALL student preferences, not just allocated ones)
        Returns: DataFrame with faculty and count of each preference rank
        """
        # Initialize statistics dictionary
        stats = {faculty: {f'Count Pref {i}': 0 for i in range(1, self.num_faculty + 1)} 
                for faculty in self.faculty_list}
        
        # Count ALL preferences (not just allocated)
        for student in self.students:
            # For each faculty, check what preference rank the student gave it
            for faculty in self.faculty_list:
                preference_rank = student.preferences.get(faculty, 0)
                
                if 1 <= preference_rank <= self.num_faculty:
                    stats[faculty][f'Count Pref {preference_rank}'] += 1
        
        # Convert to DataFrame
        data = []
        for faculty in self.faculty_list:
            row = {'Fac': faculty}
            row.update(stats[faculty])
            data.append(row)
        
        return pd.DataFrame(data)
    
    def get_allocation_preference_statistics(self) -> pd.DataFrame:
        """
        Calculate allocation-based preference statistics
        Shows: For students allocated to this faculty, what preference rank did they give it?
        Returns: DataFrame with faculty and count of each preference rank (allocation-based)
        """
        # Initialize statistics dictionary
        stats = {faculty: {f'Count Pref {i}': 0 for i in range(1, self.num_faculty + 1)} 
                for faculty in self.faculty_list}
        
        # Count preferences only for allocated students
        for student in self.students:
            if student.allocated_faculty and student.allocated_faculty in self.faculty_list:
                allocated_fac = student.allocated_faculty
                preference_rank = student.preferences.get(allocated_fac, 0)
                
                if 1 <= preference_rank <= self.num_faculty:
                    stats[allocated_fac][f'Count Pref {preference_rank}'] += 1
        
        # Convert to DataFrame
        data = []
        for faculty in self.faculty_list:
            row = {'Fac': faculty}
            row.update(stats[faculty])
            data.append(row)
        
        return pd.DataFrame(data)
    
    def get_allocation_metrics(self) -> Dict:
        """
        Get metrics about the allocation quality
        """
        allocated_count = sum(1 for s in self.students if s.allocated_faculty)
        
        # Calculate average preference rank achieved
        preference_ranks = []
        for student in self.students:
            if student.allocated_faculty:
                rank = student.preferences.get(student.allocated_faculty, 0)
                if rank > 0:
                    preference_ranks.append(rank)
        
        avg_preference = sum(preference_ranks) / len(preference_ranks) if preference_ranks else 0
        
        # Faculty distribution
        faculty_counts = {}
        for student in self.students:
            if student.allocated_faculty:
                faculty_counts[student.allocated_faculty] = \
                    faculty_counts.get(student.allocated_faculty, 0) + 1
        
        return {
            'total_students': self.num_students,
            'total_faculty': self.num_faculty,
            'num_groups': self.num_groups,
            'allocated_students': allocated_count,
            'average_preference_rank': round(avg_preference, 2),
            'faculty_distribution': faculty_counts,
            'min_students_per_faculty': min(faculty_counts.values()) if faculty_counts else 0,
            'max_students_per_faculty': max(faculty_counts.values()) if faculty_counts else 0
        }


def load_and_allocate(input_filepath: str) -> Tuple[AllocationEngine, pd.DataFrame, pd.DataFrame]:
    """
    Convenience function to load data and perform allocation
    Returns: (engine, allocation_df, statistics_df)
    """
    # Import here to avoid circular dependency
    from data_utils import load_student_data
    
    students, faculty_list = load_student_data(input_filepath)
    
    engine = AllocationEngine(students, faculty_list)
    engine.allocate()
    
    allocation_df = engine.get_allocation_summary()
    statistics_df = engine.get_faculty_statistics()
    
    return engine, allocation_df, statistics_df
