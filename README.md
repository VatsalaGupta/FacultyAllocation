# Faculty Allocation System

An intelligent student-faculty allocation system based on CGPA and student preferences.

## Features

- 🎯 **Merit-based Allocation**: Students sorted by CGPA for fair distribution
- 📊 **Preference Optimization**: Considers student preferences for faculty
- 📈 **Statistical Analysis**: Detailed reports and visualizations
- 🌐 **Interactive UI**: User-friendly Streamlit web interface
- 📥 **Export Results**: Download allocation results and statistics as CSV
- 🐳 **Docker Support**: Easy deployment with Docker

## Quick Start with Docker

### Prerequisites
- Docker installed on your system ([Get Docker](https://docs.docker.com/get-docker/))

### Run with Docker

1. **Build the Docker image:**
   ```bash
   docker build -t faculty-allocation .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8501:8501 faculty-allocation
   ```

3. **Access the application:**
   Open your browser and navigate to `http://localhost:8501`

### Docker Compose (Alternative)

Create a `docker-compose.yml` file:
```yaml
version: '3.8'
services:
  faculty-allocation:
    build: .
    ports:
      - "8501:8501"
    restart: unless-stopped
```

Then run:
```bash
docker-compose up
```

## Local Installation (Without Docker)

### Prerequisites
- Python 3.8 or higher

### Installation Steps

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Faculty_Allotment
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running Locally

1. **Start the Streamlit application:**
   ```bash
   streamlit run app.py
   ```

2. **Access the application:**
   Open your browser and navigate to `http://localhost:8501`

### Using the Application

1. **Upload your input CSV file** with the following format:
   - Columns: `Roll`, `Name`, `Email`, `CGPA`, followed by faculty name columns
   - Faculty columns contain preference ranks (1 = highest, N = lowest)

2. **Review the data** and validation results

3. **Click "Run Allocation"** to execute the algorithm

4. **Explore results** in multiple tabs:
   - Student Allocations
   - Faculty Statistics
   - Visualizations
   - Detailed Analysis

5. **Download results:**
   - Student allocation CSV
   - Faculty statistics CSV

## Algorithm Overview

### Allocation Process

1. **Sort Students**: By CGPA (descending), then by Roll number
2. **Create Groups**: Divide into ⌈S/F⌉ groups where S = students, F = faculty
3. **Allocate**: Each faculty gets 1 student per group based on best available preference
4. **Fair Distribution**: Ensures approximately equal distribution across faculty

### Example

- 88 students, 18 faculty
- Creates 5 groups (⌈88/18⌉ = 5)
- Groups 1-4: 18 students each
- Group 5: 16 students
- Each faculty receives ~5 students

## File Structure

```
Faculty_Allotment/
├── app.py                           # Streamlit UI application
├── allocation_engine.py             # Core allocation algorithm
├── data_utils.py                    # Data processing utilities
├── requirements.txt                 # Python dependencies
├── APPROACH_DOCUMENT.md             # Detailed approach documentation
├── input_btp_mtp_allocation.csv     # Sample input file
├── output_btp_mtp_allocation.csv    # Sample output file
└── fac_preference_count.csv         # Sample statistics file
```

## Input File Format

Example CSV structure:

| Roll      | Name       | Email            | CGPA | Faculty1 | Faculty2 | ... |
|-----------|------------|------------------|------|----------|----------|-----|
| 1601CB01  | Student A  | a@email.com      | 8.5  | 2        | 1        | ... |
| 1601CB02  | Student B  | b@email.com      | 9.2  | 1        | 3        | ... |

- Preference values: 1 (highest) to N (lowest)
- N = number of faculty

## Output Files

### 1. Student Allocation (`output_btp_mtp_allocation.csv`)

| Roll      | Name       | Email            | CGPA | Allocated |
|-----------|------------|------------------|------|-----------|
| 1601CB01  | Student A  | a@email.com      | 8.5  | MA        |

### 2. Faculty Statistics (`fac_preference_count.csv`)

| Fac | Count Pref 1 | Count Pref 2 | ... |
|-----|--------------|--------------|-----|
| MA  | 5            | 3            | ... |
| RS  | 2            | 4            | ... |

**What it shows:** How many students listed each faculty as their 1st, 2nd, ... Nth preference.

**Total entries:** N students × M faculty preferences

## Technical Details

- **Language**: Python 3.8+
- **Framework**: Streamlit
- **Data Processing**: Pandas
- **Visualization**: Plotly
- **Algorithm Complexity**: O(S log S + S × F)
- **Containerization**: Docker

## Development

### Project Structure

```
Faculty_Allotment/
├── app.py                           # Streamlit UI application
├── allocation_engine.py             # Core allocation algorithm
├── data_utils.py                    # Data processing utilities
├── requirements.txt                 # Python dependencies
├── Dockerfile                       # Docker configuration
├── .gitignore                       # Git ignore rules
├── APPROACH_DOCUMENT.md             # Detailed approach documentation
├── README.md                        # This file
├── input_btp_mtp_allocation.csv     # Sample input file
├── output_btp_mtp_allocation.csv    # Sample output file
└── fac_preference_count.csv         # Sample statistics file
```

### Running Tests

Create test data and verify the allocation:
```bash
python -c "from allocation_engine import *; from data_utils import *; \
students, faculty = load_student_data('input_btp_mtp_allocation.csv'); \
engine = AllocationEngine(students, faculty); engine.allocate(); \
print('Allocation successful!')"
```

## Docker Commands Reference

### Build
```bash
# Build the image
docker build -t faculty-allocation .

# Build with no cache
docker build --no-cache -t faculty-allocation .
```

### Run
```bash
# Run in foreground
docker run -p 8501:8501 faculty-allocation

# Run in background (detached)
docker run -d -p 8501:8501 --name faculty-app faculty-allocation

# Run with volume mount (for persistent data)
docker run -p 8501:8501 -v $(pwd)/data:/app/data faculty-allocation
```

### Manage
```bash
# Stop container
docker stop faculty-app

# Start container
docker start faculty-app

# Remove container
docker rm faculty-app

# View logs
docker logs faculty-app

# View running containers
docker ps
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Troubleshooting

### Docker Issues

**Port already in use:**
```bash
# Use a different port
docker run -p 8502:8501 faculty-allocation
```

**Permission denied:**
```bash
# On Linux/Mac, use sudo
sudo docker run -p 8501:8501 faculty-allocation
```

### Application Issues

**CSV upload fails:**
- Ensure CSV format matches the required structure
- Check for proper column names and data types

**Allocation errors:**
- Verify preference values are integers from 1 to N
- Ensure no duplicate roll numbers
- Check CGPA values are valid numbers

## License

MIT License - Feel free to use and modify.

## Support

For issues or questions, please check the `APPROACH_DOCUMENT.md` for detailed documentation or open an issue on GitHub.
