# 🚀 Enterprise AI Task Manager

A professional Internal Task Management System (ITMS) featuring **Hierarchical Access Control (RBAC)**, **Asynchronous Backend**, and **Context-Aware AI Integration** via Google Gemini.

## ✨ Project Highlights

*   **🧠 Context-Aware AI Analysis:** Integrated with Google Gemini 1.5. The system doesn't just analyze task titles; it reads the entire team discussion (comments) to identify blockers and suggest actionable solutions.
*   **🔐 Industrial-Grade Security:**
    *   **Stateless Authentication:** Fully implemented JWT tokens stored in browser `localStorage`.
    *   **Strict RBAC:** Three roles (`Admin`, `Manager`, `Employee`) with scoped data visibility.
    *   **Founder Immunity:** Hardcoded protection for the system's first user to prevent administrative lockouts.
*   **🏗 Clean Architecture:** Strict separation between Domain logic, Infrastructure, and API layers, enabling high testability and easy database migration.
*   **📊 Relational Integrity:** Multi-referenced database schema (PostgreSQL) managing complex relationships between Users, Departments, Tasks, and Comments.

## 🛠 Tech Stack

*   **Backend:** Python 3.12, FastAPI, Pydantic v2 (Strict Typing).
*   **Database:** PostgreSQL 16, SQLAlchemy 2.0 (Async/Await), Alembic (Migrations).
*   **AI:** Google Generative AI (Gemini 1.5 Flash).
*   **Frontend:** Single Page Application (SPA) built with Vanilla JS and Tailwind CSS.
*   **Infrastructure:** Docker & Docker Compose.

---

## 🚀 Quick Start (Local Setup)

### 1. Requirements
Ensure you have **Docker** and **Python 3.12+** installed.

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
# Postgres
POSTGRES_USER=admin
POSTGRES_PASSWORD=secret
POSTGRES_DB=orders
POSTGRES_PORT=5432
POSTGRES_HOST=localhost

# Security
JWT_SECRET_KEY=9a6d7f8b90c1e2d3f4a5b6c7d8e9f0a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Gemini AI
GEMINI_API_KEY=your_google_ai_key_here
3. Launch with Docker
code
Bash
docker-compose up -d
4. Apply Migrations
code
Bash
pip install -r requirements.txt
alembic upgrade head
5. Run Application
code
Bash
python -m src.app
Access the UI at http://localhost:8000.
📂 Architecture Overview
src/domain: Business rules and entities (The "Truth").
src/infrastructure: Database models, repositories, and external AI services.
src/api: FastAPI routes, DTO schemas, and dependency injection.
src/static: Minimalist Frontend interface.
👤 Role Hierarchy
Admin: System management, department creation, and user role overrides.
Manager: View and manage all tasks within their assigned department.
Employee: Execute assigned tasks and view personal workload.