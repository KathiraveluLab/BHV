# BHV: Behavioral Health Vault

BHV is a minimalist, Python-based application designed to record the recovery journey of people with serious mental illnesses. It complements traditional Electronic Health Records (EHRs) by storing patient-provided images and textual narratives.

## 🚀 Quick Start (Single-Command Setup)

To get BHV running locally, simply run:

```bash
python app.py
```

The application will automatically:
1. Initialize the SQLite database.
2. Create a default admin user (Username: `admin`, Password: `password123` or your `ADMIN_PASSWORD` env var).
3. Start the server at `http://localhost:5000`.

## 🛠️ Installation & Development

### Prerequisites
- Python 3.8+

### Step-by-Step Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/KathiraveluLab/BHV.git
   cd BHV
   ```
2. **Setup environment:**
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure Environment:**
   Copy `.env.example` to `.env` and update the variables.

## 📄 License
This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.
