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


## Proposed MVP Scope (Draft)

This section summarizes the currently discussed MVP scope for BHV, based on
community discussions and early prototype work. It is intended as a living
reference and may evolve as the project matures.

### Core MVP (Must-Have)
The initial focus of BHV is on:
- Secure image upload and storage
- Privacy-first access control (user vs admin roles)
- Simple, minimal architecture suitable for community clinics
- Local filesystem storage with metadata indexed in a lightweight database
- Easy local setup and a single-command run where possible

### Optional / Modular Extensions
The following features are considered valuable but optional for the initial MVP:
- Admin dashboards and moderation tools
- Containerized deployment (e.g., Docker)
- Research-oriented modules such as fuzzy color–emotion analysis for
  images without explicit tags or narratives

### Guiding Principles
- Prefer simplicity over feature completeness
- Avoid locking architectural decisions too early
- Keep advanced features modular so they do not block the core system

Community feedback and maintainer guidance will continue to shape this scope.
