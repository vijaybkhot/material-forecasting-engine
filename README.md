# 🏗️ Material Forecasting Engine

[![Live Demo](https://img.shields.io/badge/demo-online-green.svg)](https://material-forecasting-engine.vercel.app/)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-24.0-2496ED.svg)](https://www.docker.com/)

> **AI-Powered Risk Analysis for the Construction Industry**

The **Material Forecasting Engine** is a full-stack machine learning application designed to predict future prices of critical construction materials (Lumber, Steel, Concrete). **Construction material prices are volatile and can destroy project margins.** By leveraging historical economic data from the Federal Reserve (FRED) and advanced time-series forecasting models, this tool helps project managers and estimators mitigate financial risk in long-term construction projects.

---

## 🚀 Live Demo

- **Frontend:** [forecasting.vijaykhot.com/](https://forecasting.vijaykhot.com/)
- **API Docs (Swagger):** [constrisk-api.herokuapp.com/docs](https://constrisk-api-96f05a1f5ba2.herokuapp.com/docs)
- **Video Walkthrough:** [![Watch the Demo](https://img.youtube.com/vi/NEc9YYhIxww/0.jpg)](https://www.youtube.com/watch?v=NEc9YYhIxww)

---

## 🧠 System Architecture & Data Flow

The system implements a complete **ETL (Extract, Transform, Load) and Inference pipeline**. It decouples the heavy ML operations from the user-facing application.

```mermaid
graph TD
    %% Theme & Colors
    %%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#ffaa00', 'edgeLabelBackground':'#ffffff', 'tertiaryColor': '#f4f4f4'}}}%%
    classDef client fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c;
    classDef app fill:#e3f2fd,stroke:#1565c0,stroke-width:2px,color:#0d47a1;
    classDef infra fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#bf360c;
    classDef data fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#1b5e20;
    classDef external fill:#f5f5f5,stroke:#616161,stroke-width:2px,stroke-dasharray: 5 5,color:#212121;

    %% --- LEFT TRACK: DATA PIPELINE ---
    subgraph Offline ["🛠️ Offline Data Pipeline"]
        direction TB
        FRED[("🏦 FRED API")]:::external
        Ingest["⚙️ ETL Script"]:::app
        DB[("🐘 PostgreSQL")]:::data

        FRED -->|"1. Fetch Raw Data"| Ingest
        Ingest -->|"2. Clean & Upsert"| DB
    end

    %% --- RIGHT TRACK: USER FLOW ---
    subgraph Online ["⚡ Real-Time Inference"]
        direction TB
        Client["⚛️ Next.js"]:::client
        API["⚡ FastAPI"]:::app
        Cache[("🔴 Redis")]:::infra
        Model["🧠 SARIMAX"]:::app

        Client -->|"4. Request"| API
        API <-->|"5. Cache Hit/Miss"| Cache
        API -->|"6. Predict"| Model
    end

    %% --- THE BRIDGE ---
    DB -.->|"3. Training Data"| Model

    %% Formatting to force parallel layout
    linkStyle default stroke:#333,stroke-width:2px;
```

---

## 🔌 API Reference

The backend is a RESTful API built with **FastAPI**. You can interact with it directly:

| Method | Endpoint     | Description                                 | Try it                                                                                             |
| :----- | :----------- | :------------------------------------------ | :------------------------------------------------------------------------------------------------- |
| `GET`  | `/health`    | Health check for the API service.           | [Link](https://constrisk-api-96f05a1f5ba2.herokuapp.com/health)                                    |
| `GET`  | `/materials` | List all available materials.               | [Link](https://constrisk-api-96f05a1f5ba2.herokuapp.com/materials)                                 |
| `GET`  | `/forecast`  | Generate a 12-month forecast (e.g., Steel). | [Link](https://constrisk-api-96f05a1f5ba2.herokuapp.com/forecast?material_id=PPI_STEEL&horizon=12) |

---

## 💡 Key Features

- **📈 Multi-Model Forecasting:** Automatically trains and selects the best model (SARIMAX, Prophet, Exponential Smoothing) for each material.
- **🔄 Automated Data Pipeline:** Ingests fresh data from FRED API, retrains models, and updates forecasts automatically.
- **📊 Interactive Dashboard:** React-based frontend with dynamic charts to visualize historical trends and future predictions.
- **🐳 MLOps Optimized:** Solves the "Large Artifact" problem using containerized deployments (more on this below).
- **🛡️ Robust Backend:** FastAPI service with PostgreSQL storage and Redis caching for high performance.

---

## 🛠️ Tech Stack

### **Frontend**

- **Framework:** Next.js (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS
- **Visualization:** Recharts

### **Backend**

- **Framework:** FastAPI
- **Database:** PostgreSQL (SQLAlchemy + Alembic)
- **Caching:** Redis
- **Runtime:** Python 3.11

### **Machine Learning**

- **Libraries:** Scikit-learn, Statsmodels, Pandas
- **Data Source:** FRED API (Federal Reserve Economic Data)
- **Models:** SARIMAX, Exponential Smoothing, Linear Regression

### **DevOps & Infrastructure**

- **Containerization:** Docker & Docker Compose
- **Orchestration:** Heroku (Backend) & Vercel (Frontend)
- **CI/CD:** GitHub Actions (Code) + Heroku Container Registry (Artifacts)

---

## 🏗️ Deployment Strategy (DevOps)

To handle the large model artifacts (which exceed GitHub's 100MB limit), I implemented a **Hybrid Deployment Strategy**:

1.  **Code vs. Artifacts Separation:**

    - **GitHub** hosts the source code (lightweight, version controlled).
    - **Heroku Container Registry** hosts the compiled Docker image containing the heavy model artifacts.

2.  **The Build Process:**
    - We build the Docker image _locally_ to bake in the models.
    - This ensures production has the exact artifacts validated in development.

```mermaid
graph LR
    A[Local Dev Environment] -->|Push Code| B[GitHub Repo]
    A -->|Build & Push Image| C[Heroku Container Registry]
    B -->|Trigger Deploy| D[Vercel Frontend]
    C -->|Release Container| E[Heroku Backend API]
    E <--> F[PostgreSQL DB]
    E <--> G[Redis Cache]
```

---

## ⚡ Getting Started Locally

Follow these steps to run the entire stack on your machine.

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+

### Installation

1.  **Clone the repository**

    ```bash
    git clone https://github.com/vijaybkhot/material-forecasting-engine.git
    cd material-forecasting-engine
    ```

2.  **Configure Environment**
    Create a `.env` file from the example template.

    ```bash
    cp .env.example .env
    # (Optional) Open .env and add your FRED_API_KEY
    ```

3.  **Run the Setup Script**
    This single command builds containers, runs migrations, and seeds the database.

    ```bash
    ./setup.sh
    ```

4.  **Access the App**
    - Frontend: `http://localhost:3000`
    - Backend API Docs: `http://localhost:8000/docs`

---

## 📂 Project Structure

```
├── backend/            # FastAPI application
│   ├── app/            # API endpoints, CRUD, schemas
│   ├── alembic/        # Database migrations
│   └── models.py       # SQLAlchemy database models
├── frontend/           # Next.js application
│   ├── src/app/        # App Router pages
│   └── src/components/ # React components (Charts, Dashboard)
├── ml/                 # Machine Learning pipeline
│   ├── data/           # Raw and processed data
│   ├── models/         # Trained model artifacts (.pkl)
│   ├── notebooks/      # Jupyter notebooks for experimentation
│   └── scripts/        # Training and ingestion scripts
├── docs/               # Documentation
└── docker-compose.yml  # Local orchestration
```

---

## 📄 Model Information

For detailed information on the forecasting methodology, data sources, and performance metrics, please see the [Model Card](docs/MODEL_CARD.md).

---

## 👤 Author

**Vijay Khot**

- **Role:** Full Stack Developer & ML Engineer

<p align="left">
<a href="https://vijaykhot.com" target="_blank">
  <img src="https://img.shields.io/badge/Portfolio-vijaykhot.com-blue?style=for-the-badge&logo=google-chrome" alt="Portfolio">
</a>
<a href="https://medium.com/@vijaysinh.khot" target="_blank">
  <img src="https://img.shields.io/badge/Medium-@vijaysinh.khot-black?style=for-the-badge&logo=medium" alt="Medium">
</a>
<a href="https://github.com/vijaybkhot" target="_blank">
  <img src="https://img.shields.io/badge/GitHub-vijaybkhot-181717?style=for-the-badge&logo=github" alt="GitHub">
</a>
<a href="https://www.linkedin.com/in/vijay-khot/" target="_blank">
  <img src="https://img.shields.io/badge/LinkedIn-Vijay%20Khot-0077B5?style=for-the-badge&logo=linkedin" alt="LinkedIn">
</a>
</p>

---

_Built with ❤️ using Python and TypeScript._
