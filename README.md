# GreenRewards AI

## Problem Statement

Employees and individuals need an easy way to track, verify, and get rewarded for sustainable actions that reduce their carbon footprint.

## Solution Overview

* Users upload proofs (tickets, receipts, photos, bills).
* An AI verifier extracts text/images, classifies the proof, estimates carbon savings, and awards points.
* Dashboards, leaderboards, badges, and recommendations encourage sustainable behavior.

## Architecture

* Frontend: React + Vite
* Backend: FastAPI + SQLAlchemy
* Database: SQLite
* AI Layer: OCR + Sustainability Verification Engine

## AI Workflow

1. Upload proof
2. OCR/Text extraction
3. Sustainability verification
4. Carbon savings estimation
5. Reward allocation
6. Dashboard update

## Features

* Carbon Footprint Tracking
* Carbon Confidence Score
* Green Rewards & Badges
* Sustainability Campaigns
* Walking Challenges
* AI Verification
* Leaderboards
* Dashboard Analytics

## Security

* JWT Authentication
* File Validation
* Upload Verification
* Environment-Based Configuration

## Running Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload
```

## Running Frontend

```bash
cd frontend
npm install
npm run dev
```

## Testing

```powershell
cd backend
pytest -q
```

### Test Status

* Backend Tests: 22 Passed
* Backend Coverage: 79%
* Frontend Tests: Passed

## Future Scope

* Enhanced Sustainability Verification
* Advanced Carbon Analytics
* Improved Accessibility
* Expanded Campaign System
* Production Security Hardening

## Green Rewards AI v2.0

Focused on stability, testing, security review, code quality improvements, and production readiness.
