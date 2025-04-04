# TF Binding Site Scanner

A web-based tool for scanning DNA sequences to identify potential transcription factor binding sites. Users can search for specific transcription factors from the JASPAR database and analyze DNA sequences for potential binding locations.

## Usage
1. **Search for and Select Transcription Factors**
   - Enter a transcription factor name (e.g., "GATA1", "RUNX1")
   - Browse through matching factors from JASPAR database
   - Select a transcription factor to scan for

2. **Analyze DNA Sequences**
   - Input your nucleotide sequence in the text area (plain text or FASTA format)
   - View results showing potential binding sites and scores
  
### Video Demonstration
https://youtu.be/LrVzvFMzhgo

## Tech Stack

### Frontend
- Next.js 14 (React framework)
- TypeScript
- Tailwind CSS
- shadcn/ui components

### Backend
- FastAPI (Python web framework)
- Biopython for sequence analysis
- NumPy for numerical computations

### APIs & Data Sources
- JASPAR API (https://jaspar.elixir.no/api/)
  - Provides transcription factor binding profiles
  - Position frequency matrices (PFMs)

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm (comes with Node.js)
- venv (can be installed via `pip install virtualenv`)

## Project Structure
```bash
├── backend/ # FastAPI backend
├── frontend/ # Next.js frontend
├── setup.py # Installation script
└── run.py # Development server script
```

## Installation & Setup

### Option 1: Using Setup Scripts
```bash
# Run the setup script (this will install all dependencies)
python setup.py
# or
python3 setup.py
# or
py setup.py

# Start both frontend and backend servers
python run.py
```

### Option 2: Manual Setup

#### Backend Setup
```bash
# Install virtualenv if you don't have it
pip install virtualenv

# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install
```

## Running the Application Manually

### Backend
```bash
# From the backend directory, with venv activated:
uvicorn main:app --reload
```

### Frontend
```bash
# From the frontend directory:
npm run dev
```

## Development

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
