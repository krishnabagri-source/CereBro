# 🧠 CereBro — Adaptive AI Learning Platform

> **Learn smarter. Understand deeper. Improve continuously.**

CereBro is an AI-powered adaptive learning platform designed to make education more personalized and effective.

Unlike conventional AI tutors that primarily answer questions, CereBro aims to understand how a student learns, track their conceptual understanding, identify knowledge gaps, and adapt the learning experience accordingly.

Developed for the **Agentic AI Hackathon '26**, CereBro explores the application of intelligent AI systems in personalized education.

## 💡 The Problem

Traditional learning systems often provide standardized learning experiences despite students having different levels of understanding.

A student getting an answer wrong doesn't necessarily mean they lack knowledge of the entire topic. They might have misunderstood one specific concept.

Similarly, getting an answer right doesn't always demonstrate complete conceptual understanding.

**CereBro aims to bridge this gap by making learning adaptive rather than standardized.**

## ✨ Core Features

- **Diagnostic Assessment:** Evaluate the learner's existing knowledge.
- **Adaptive Learning:** Personalize learning based on individual performance.
- **Concept-Level Mastery:** Track understanding at the individual concept level.
- **Knowledge Gap Identification:** Identify topics that require additional attention.
- **Misconception Analysis:** Explore the reasoning behind incorrect answers.
- **Intelligent Questioning:** Target practice questions toward weaker concepts.
- **Spaced Repetition:** Reinforce learning through scheduled revision.
- **Multi-Subject Vision:** Designed with the goal of supporting different subjects and knowledge domains.

## 🔄 Learning Workflow

`Assess → Analyze → Track Mastery → Identify Gaps → Personalize → Practice → Improve`

Each interaction can contribute to a better understanding of the learner's progress.

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript |
| Styling | Tailwind CSS |
| Build Tool | Vite |
| Icons | Lucide React |
| Backend | Python, FastAPI, Uvicorn |
| Additional Server | Node.js, Express, TypeScript |
| Development | npm, concurrently |

## 🏗️ Project Structure

```text
CereBro/
│
├── backend/       # Python backend
├── frontend/      # Frontend application
├── server/        # Express/TypeScript server
├── src/           # Application source
│
├── package.json
├── package-lock.json
├── vite.config.ts
└── README.md
```

## 🚀 Getting Started

### Prerequisites

- Node.js
- npm
- Python 3
- pip

### 1. Clone the repository

```bash
git clone https://github.com/krishnabagri-source/CereBro.git
cd CereBro
```

### 2. Install frontend dependencies

```bash
npm install
```

### 3. Set up the Python backend

Install the Python dependencies specified by the backend's requirements file, if present:

```bash
pip install -r backend/requirements.txt
```

### 4. Configure environment variables

Configure the API keys and environment variables required by the backend and AI integration. Refer to the application's configuration files for the exact variable names.

Never commit secrets or API keys.

### 5. Run CereBro

```bash
npm run dev
```

This starts the frontend and Python backend concurrently.

- Frontend: Vite development server
- Backend: FastAPI server on port 8000

## 🔮 Future Scope

- More advanced learner knowledge modeling.
- Improved reasoning-based misconception detection.
- Dynamic difficulty calibration.
- Expanded subject and domain support.
- Better concept relationship mapping.
- Personalized revision scheduling.
- Learning analytics and progress visualization.

## 👥 Team

Built collaboratively by:

- **Krishna Bagri** — [GitHub](https://github.com/krishnabagri-source)
- **Project Collaborator** — Add teammate's name and GitHub profile.

## 🏆 Hackathon

**Event:** Agentic AI Hackathon '26  
**Organizer:** Product Space  
**Date:** September 21, 2026

## 📌 Repository

[Explore CereBro on GitHub](https://github.com/krishnabagri-source/CereBro)

---

**CereBro — Because understanding matters more than just getting the answer right.** 🧠
