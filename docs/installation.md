# Installation Guide

## Prerequisites
- Python 3.7 or higher
- pip (Python package installer)
- Git

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/KathiraveluLab/BHV.git
cd BHV
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run Tests
```bash
pytest
```

## Development Setup

For development, install additional dependencies:
```bash
pip install -r requirements.txt
```

## Troubleshooting

If you encounter issues:
1. Ensure Python 3.7+ is installed: `python --version`
2. Ensure pip is updated: `pip install --upgrade pip`
3. Check virtual environment is activated (you should see `(venv)` in terminal)

## Next Steps

- Read the [Contributing Guidelines](../CONTRIBUTING.md)
- Check open issues on GitHub
- Join the discussions