# ResumeIQ

ResumeIQ is an advanced Resume Intelligence Platform that leverages Machine Learning to automatically categorize resumes, extract technical skills, and semantically match candidates to job descriptions. 

Built with a high-performance Python FastAPI backend and a clean, dependency-free vanilla HTML/JS frontend.

## Features

- **Resume Classification**: Automatically categorizes resumes into 6 distinct industry verticals (AI/ML, Software Development, Data Science, Cloud/DevOps, Cybersecurity, Data Engineering) using a TF-IDF and Logistic Regression model.
- **Skill Extraction**: Parses and extracts core technical skills from unstructured resume text.
- **Semantic Job Matching**: Compares candidate resumes against job descriptions using cosine similarity to generate an alignment score.
- **Real-time Analytics Dashboard**: Features an interactive Confusion Matrix, live usage tracking, and classification metrics.
- **Clean Export**: Dedicated print stylesheets for exporting analyzed data seamlessly to PDF.
- **Responsive UI**: A highly polished, modern user interface built from the ground up without heavy frontend frameworks.

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn
- **Machine Learning**: Scikit-Learn, Pandas, NumPy
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Deployment**: Docker, AWS EC2

## Repository Structure

```text
.
├── backend/
│   └── app/
│       └── main.py          # FastAPI application & API endpoints
├── data/                    # Generated synthetic training data
├── frontend/                # Static HTML, CSS, and JS files
├── models/                  # Saved ML model binaries (Pickle files)
├── scripts/
│   ├── gen_data.py          # Generates synthetic data for the ML model
│   └── gen_pages.py         # Utility script for generating HTML templates
├── Dockerfile               # Production container configuration
└── requirements.txt         # Python dependencies
```

## Running Locally

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Mrvikas06/ResumeIQ.git
   cd ResumeIQ
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Generate training data and train the model:**
   ```bash
   python scripts/gen_data.py
   python -c "import sys; sys.path.insert(0, 'backend'); from models.pipeline import train_classifier; train_classifier()"
   ```

4. **Start the development server:**
   ```bash
   uvicorn backend.app.main:app --reload
   ```

5. **Access the application:**
   Open your browser and navigate to `http://127.0.0.1:8000`.

## Production Deployment (AWS EC2)

ResumeIQ is fully containerized and ready for production deployment on AWS EC2 or any Docker-compatible hosting environment.

1. SSH into your EC2 instance.
2. Clone the repository.
3. Build the Docker image (this step automatically trains the ML model):
   ```bash
   docker build -t resumeiq .
   ```
4. Run the container on port 80:
   ```bash
   docker run -d -p 80:8000 resumeiq
   ```

The platform will now be accessible via your EC2 instance's public IP address or configured domain name.

## License
MIT License
