# BHV: Behavioral Health Vault

The goal of this project is to provide a digitization approach to record the journey of recovery of people with serious mental illnesses and other social determinants. BHV (pronounced Beehive or Behave) aims to complement traditional Electronic Health Records (EHRs) by storing patient-provided images (photographs and scanned drawings) along with associated textual narratives, which may be provided by the patient or recorded by a social worker during an interview.

BHV is a minimal, Python-based application that enables healthcare networks to store and retrieve patient-provided images.

It provides them access to upload, view, and edit their own images and narratives.

It also provides admin-level access for system administrators to view the entire ecosystem, upload images on behalf of users, along with the narrative, edit images on behalf of users, and delete images or narrations on behalf of users or as a moderation action.

The system should be secure. But the signup process should be pretty straightforward. Email-based signups are ok.

Log-ins should be straightforward. A simple username and password should be sufficient.

The system should avoid unnecessary bloat to enable easy installation in healthcare networks.

The front-end should be kept minimal to allow the entire system to be run from a single command (rather than expecting the front-end, backend, and database to be run separately).

The storage of the images could be in a file system with an index to retrieve them easily. The index itself could be in a database to allow easy queries.



\## Setup \& Installation



\### Prerequisites

\- Python 3.8+



\### Quick Start



1\. Clone the repository

```bash

&#x20;  git clone https://github.com/KathiraveluLab/BHV.git

&#x20;  cd BHV

```



2\. Install dependencies

```bash

&#x20;  pip install -r requirements.txt

```



3\. Run the application

```bash

&#x20;  uvicorn app.main:app --reload

```



4\. Open http://localhost:8000 in your browser



\### API Endpoints

\- `GET /` - Root endpoint

\- `GET /health` - Health check

\- `GET /docs` - Interactive API documentation (Swagger UI)

