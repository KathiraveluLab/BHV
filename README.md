# BHV Prototype (Architectural Prototype)
**Proof of Concept for Alaska BHV: Flask + MongoDB + Docker**

This repository serves as a **Proof of Concept (POC)** for the "Beehive-2.0" architecture.

It demonstrates a minimal, monolithic implementation of the Behavioral Health Vault (BHV) designed to solve the installation complexity of the original Beehive project.

## Goal
The primary goal of this prototype is to validate the **"Single Command Installation"** requirement using a containerized **Flask + MongoDB** stack, while also demonstrating secure OAuth authentication and automatic private repository creation.

## Features
*   **Single Command Install**: Fully containerized with Docker Compose.
*   **MongoDB Backend**: Swapped from SQLite to MongoDB for scalable metadata storage.
*   **User Authentication**: OAuth integration (GitHub, Google) + Local Login.
*   **Private Vault**: Automatically creates a private GitHub repository (`bhv-vault-<username>`) for each user.
*   **Minimal Stack**: Flask + Jinja2 + Vanilla CSS (No complex frontend build steps).

## Quick Start

### Option 1: The "Single Command" (Recommended)
This method uses Docker to spin up the entire stack (App + Database) with one command.

1.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```env
    # Docker uses the service name 'mongodb' as the host
    MONGO_URI=mongodb://mongodb:27017/
    
    # OAuth Credentials
    GITHUB_CLIENT_ID=your_github_id
    GITHUB_CLIENT_SECRET=your_github_secret
    GOOGLE_CLIENT_ID=your_google_id
    GOOGLE_CLIENT_SECRET=your_google_secret
    ```

2.  **Run with Docker Compose**:
    ```bash
    docker-compose up --build
    ```

3.  **Open in Browser**:
    Visit `http://localhost:5001`

---

### Option 2: Manual Installation
If you prefer to run locally without Docker:

1.  **Prerequisites**:
    - Python 3.8+
    - MongoDB installed and running locally (default port 27017)

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment**:
    Update `.env` to point to localhost:
    ```env
    MONGO_URI=mongodb://localhost:27017/
    ... (OAuth credentials)
    ```

4.  **Run the App**:
    ```bash
    python prototype.py
    ```

## Roadmap & Status
*   [x] **Core Architecture**: Flask + MongoDB + Docker (Completed)
*   [x] **Authentication**: GitHub & Google OAuth (Completed)
*   [x] **Vault Creation**: Automatic private repo creation via PyGithub (Completed)
*   [ ] **Analytics**: Advanced Research Analytics Module (Planned)
