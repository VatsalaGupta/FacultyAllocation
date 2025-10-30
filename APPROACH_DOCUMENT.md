# Faculty Allocation System - Approach Document

## Problem Statement

Design and implement a fair faculty allocation system that assigns students to faculty supervisors based on:
- Student CGPA (merit-based ordering)
- Student preferences (1 to N, where N = number of faculty)
- Faculty availability (one student per group per faculty)

## Input Data Structure

### Student Input File (`input_btp_mtp_allocation.csv`)
- **Columns**: Roll, Name, Email, CGPA, Faculty1, Faculty2, ..., FacultyN
- **Values**: Preference numbers (1 = highest preference, N = lowest preference)
- **Dynamic**: Number of students and faculty determined from file structure

### Expected Output Files

1. **Student Allocation File** (`output_btp_mtp_allocation.csv`)
   - Columns: Roll, Name, Email, CGPA, Allocated
   - Shows which faculty each student was assigned to

## Output Files

1. **Student Allocation File** (`output_btp_mtp_allocation.csv`)
   - Columns: Roll, Name, Email, CGPA, Allocated
   - Shows which faculty each student was assigned to

2. **Faculty Statistics File** (`fac_preference_count.csv`)
   - Columns: Fac, Count Pref 1, Count Pref 2, ..., Count Pref N
   - Shows how many students listed each faculty as their Nth preference
   - **Important**: Counts ALL student preferences (not just allocated ones)
   - **Total entries**: S × F (where S = students, F = faculty)
   - Example: 90 students × 18 faculty = 1,620 total preference entries

## Mathematical Foundation

### Key Definitions

Let:
- **S** = Total number of students
- **F** = Total number of faculty
- **G** = Number of groups = ⌈S / F⌉ (ceiling function)
- **P(s, f)** = Preference value of student s for faculty f (1 to F)

### Group Formation Logic

**Group Size Calculation:**
```
Group 1 to (G-1): Each contains exactly F students
Group G: Contains S - (F × (G-1)) students (may be < F)
```

**Student Distribution:**
- Students are sorted in **descending order** by CGPA
- Top F students → Group 1
- Next F students → Group 2
- ...
- Remaining students → Group G

**Example:**
- 88 students, 18 faculty
- G = ⌈88/18⌉ = 5 groups
- Groups 1-4: 18 students each (72 total)
- Group 5: 16 students (88 - 72)

## Allocation Algorithm

### Approach: Greedy Allocation with Preference Optimization

#### Core Strategy

For each group (starting from Group 1):
1. Create a list of available faculty (initially all F faculty)
2. For each student in the group:
   - Find their **best available preference** (lowest preference number)
   - Assign student to that faculty
   - Mark that faculty as unavailable for this group
3. Reset faculty availability for next group

#### Pseudo-code

```python
def allocate_students(sorted_students, faculty_list, group_size):
    allocations = {}
    
    # Divide students into groups
    groups = create_groups(sorted_students, group_size)
    
    for group in groups:
        available_faculty = set(faculty_list)  # All faculty available per group
        
        for student in group:
            # Find best preference among available faculty
            best_pref = INFINITY
            best_faculty = None
            
            for faculty in available_faculty:
                pref_value = student.preference[faculty]
                if pref_value < best_pref:
                    best_pref = pref_value
                    best_faculty = faculty
            
            # Allocate student to best available faculty
            allocations[student.id] = best_faculty
            available_faculty.remove(best_faculty)
    
    return allocations
```

### Why This Approach Works

**Advantages:**
1. **CGPA Priority**: Higher CGPA students get first choice from groups
2. **Fair Distribution**: Each faculty gets one student per group (approximately S/F total)
3. **Preference Optimization**: Within each group, students get their best available preference
4. **Handles Imbalance**: Last group can have fewer students than faculty

**Trade-offs:**
- Not globally optimal (doesn't use Hungarian algorithm or perfect matching)
- Simpler and more transparent than complex optimization
- Students with lower CGPA in later groups may get less preferred choices
- But this is fair since allocation is merit-based

## Edge Cases to Handle

### 1. **Equal CGPA**
- **Issue**: Multiple students with same CGPA
- **Solution**: Secondary sort by Roll number (lexicographic)

### 2. **Last Group Undersized**
- **Issue**: Last group has fewer students than faculty
- **Solution**: Some faculty will not receive students from last group (natural consequence)

### 3. **Preference Ties**
- **Issue**: Multiple available faculty have same preference value
- **Solution**: Choose first match encountered (deterministic based on faculty column order)

### 4. **Data Validation**
- Missing CGPA values → Skip student or assign default
- Invalid preference values → Validate range [1, F]
- Duplicate preferences → Flag as data error

## Implementation Architecture

### Module Breakdown

#### 1. **Data Input Module**
```python
def load_student_data(filepath):
    # Read CSV
    # Extract student count, faculty count
    # Parse preferences into structured format
    # Return: student_list, faculty_list
```

#### 2. **Sorting Module**
```python
def sort_students_by_merit(students):
    # Sort by CGPA (descending)
    # Secondary sort by Roll (ascending)
    # Return: sorted_student_list
```

#### 3. **Grouping Module**
```python
def create_groups(sorted_students, faculty_count):
    # Calculate group size = faculty_count
    # Calculate number of groups = ceil(len(students) / faculty_count)
    # Split students into groups
    # Return: list_of_groups
```

#### 4. **Allocation Engine**
```python
def allocate_faculty(groups, faculty_list):
    # For each group:
    #   Reset available faculty
    #   For each student in group:
    #     Find best available preference
    #     Assign and mark faculty as used
    # Return: allocation_dict {student_id: faculty}
```

#### 5. **Statistics Module**
```python
def calculate_preference_stats(students, faculty_list):
    # For each faculty:
    #   Count how many students listed it as pref 1, 2, ..., N
    #   This counts ALL preferences, not just allocated ones
    # Return: stats_dict {faculty: [count_pref_1, ..., count_pref_N]}
```

#### 6. **Output Module**
```python
def write_allocation_file(students, allocations, output_path):
    # Write: Roll, Name, Email, CGPA, Allocated

def write_statistics_file(stats, output_path):
    # Write: Fac, Count Pref 1, ..., Count Pref N
```

### Streamlit UI Design

#### UI Components

1. **File Upload**
   - Upload input CSV file
   - Display preview of first few rows
   - Show detected: # of students, # of faculty

2. **Validation Panel**
   - Check for data integrity
   - Display warnings/errors
   - Show CGPA distribution

3. **Allocation Button**
   - Trigger allocation algorithm
   - Show progress bar

4. **Results Display Tabs**
   - **Student Allocations**: Shows Roll, Name, Email, CGPA, Allocated Faculty
   - **Faculty Statistics**: Shows how many students listed each faculty as their Nth preference
   - **Visualizations**: Charts for faculty distribution, preference achievement, CGPA distribution
   - **Analysis**: Top students, search functionality, detailed statistics

5. **Download Buttons**
   - Download student allocation CSV
   - Download faculty statistics CSV

6. **Visualizations**
   - Bar chart: Faculty vs. student count
   - Histogram: Preference distribution
   - Box plot: CGPA by faculty

## Testing Strategy

### Unit Tests
1. Test group formation with various S and F values
2. Test sorting with duplicate CGPAs
3. Test allocation with small datasets
4. Test edge case: S < F, S = F, S >> F

### Integration Tests
1. End-to-end test with sample data
2. Verify output file formats
3. Verify statistics calculations

### Validation Tests
1. Ensure no student is assigned twice
2. Ensure no faculty gets more than G students
3. Ensure all students are allocated
4. Verify preference counts match allocations

## Complexity Analysis

### Time Complexity
- Sorting: **O(S log S)**
- Grouping: **O(S)**
- Allocation: **O(S × F)** per student to find best preference
- Total: **O(S log S + S × F)**

For typical values (S=100, F=20): ~2,100 operations → Very fast

### Space Complexity
- Student data: **O(S × F)**
- Allocation results: **O(S)**
- Statistics: **O(F²)**
- Total: **O(S × F + F²)**

## Future Enhancements

1. **Constraint-based Allocation**
   - Faculty capacity limits (min/max students)
   - Student-faculty compatibility rules

2. **Optimization Algorithms**
   - Hungarian algorithm for global optimal matching
   - Genetic algorithms for constraint satisfaction

3. **Interactive Reallocation**
   - Allow manual swaps
   - Show impact of changes on preference scores

4. **Multi-criteria Scoring**
   - Weight CGPA vs. preferences
   - Faculty research area matching

## Conclusion

This greedy approach balances:
- **Simplicity**: Easy to understand and implement
- **Fairness**: Merit-based with preference consideration
- **Efficiency**: Fast execution even for large datasets
- **Transparency**: Clear rules that can be explained to stakeholders

The algorithm ensures that higher-merit students get better preference matches while maintaining equitable faculty workload distribution.

---

**Ready for Implementation**: This document provides the foundation for building the system. Next steps involve translating these concepts into Python code with Streamlit UI.
