# 🏗️ Material Forecasting Engine

[![CI Quality Check](https://github.com/vijaybkhot/material-forecasting-engine/actions/workflows/ci.yml/badge.svg)](https://github.com/vijaybkhot/material-forecasting-engine/actions/workflows/ci.yml)
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

## 🏗️ System Architecture

The system implements a **complete ETL (Extract, Transform, Load) and Real-Time Inference pipeline** with cloud-native storage and intelligent caching. It decouples heavy ML operations from user-facing applications and leverages AWS S3 for scalable model artifact storage.

````mermaid
graph TD
    %% --- STYLING ---
    classDef actor fill:#f5f5f5,stroke:#333,stroke-width:2px;
    classDef frontend fill:#e1bee7,stroke:#4a148c,stroke-width:2px;
    classDef backend fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px;
    classDef storage fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    classDef cloud fill:#bbdefb,stroke:#0d47a1,stroke-width:2px;
    classDef process fill:#e0e0e0,stroke:#616161,stroke-dasharray: 5 5;

    %% --- EXTERNAL ---
    User((👤 User)):::actor
    FRED[("🏦 FRED API")]:::actor

    %% --- HEROKU RUNTIME ---
    subgraph Heroku ["☁️ Heroku Runtime"]

        %% ONLINE SERVING
        subgraph Online ["⚡ Online Serving"]
            NextJS["⚛️ Next.js Frontend<br>(Vercel/Heroku)"]:::frontend
            FastAPI["⚡ FastAPI Backend<br>(ArtifactManager)"]:::backend
        end

        %% OFFLINE PROCESSING
        subgraph Offline ["🛠️ Offline Data Ops"]
            Ingest["📜 Ingestion Script<br>(ingest_data.py)"]:::process
            Train["🧠 Training Script<br>(train_all_models.py)"]:::process
        end
    end

    %% --- DATA INFRASTRUCTURE ---
    subgraph Infrastructure ["💾 Data Infrastructure"]
        Postgres[("🐘 PostgreSQL<br>(Raw Series Data)")]:::storage
        Redis[("🔴 Redis Cache<br>(1hr TTL)")]:::storage
        S3[("📦 AWS S3 Bucket<br>(Model Artifacts)")]:::cloud
    end

    %% --- FLOWS ---

    %% 1. User Flow
    User ==>|"Browser"| NextJS
    NextJS ==>|"GET /forecast"| FastAPI

    %% 2. Inference Flow (The "Hybrid" Logic)
    FastAPI -->|"1. Check Cache"| Redis
    Redis -.->|"Hit"| FastAPI
    FastAPI -- "2. Miss? Download Model" --> S3
    S3 -.->|"Stream .pkl"| FastAPI

    %% 3. ETL Flow
    FRED -->|"Fetch Data"| Ingest
    Ingest -->|"Upsert"| Postgres

    %% 4. Training Flow
    Train -->|"Read History"| Postgres
    Train -- "Upload Artifacts" --> S3

    linkStyle default stroke:#333,stroke-width:1.5px;
```

## Component Breakdown

### 🛠️ **Offline ETL & Training**

- **Data Ingestion** (`ingest_data.py`): Fetches economic indicators from FRED API, stores in PostgreSQL
- **Model Training** (`train_all_models.py`): Fits SARIMAX models on historical data, saves to disk
- **S3 Upload**: Pushes trained models to AWS S3 for production access

### ⚡ **Real-Time Inference API**

- **FastAPI Backend**: RESTful endpoints with request validation
- **Next.js Frontend**: Interactive dashboard for forecasting
- **Endpoints**:
  - `GET /materials` - Available materials
  - `GET /historical-data/{id}` - Historical prices
  - `GET /forecast?material_id=X&horizon=12` - Predictions

### 💾 **Data Persistence**

- **PostgreSQL**: Stores raw economic time series
- **Redis**: Caches forecasts (1-hour TTL)
- **AWS S3**: Stores trained SARIMAX models and metadata

### 🔮 **Forecast Generation with Caching**

1. Check Redis for cached forecast
2. If cached, return immediately
3. If miss, load model from S3
4. Deserialize SARIMAX object
5. Generate 12-month forecast
6. Cache result for 1 hour
7. Return JSON with `storage_mode: S3`

### 🚀 **CI/CD Pipeline**

- Backend linting & testing (Python)
- Frontend build verification
- Automated Heroku deployment
- S3 pipeline verification

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
````

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
