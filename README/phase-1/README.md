# Verify AI — Phase One

> **AI-powered verification platform — foundational frontend and authentication layer.**

Verify AI is a software project being developed in multiple phases, with each phase establishing a specific part of the overall application architecture.

**Phase One** focuses on establishing the frontend foundation and authentication-related user flow using a modern React and TypeScript stack.

---

## 🚀 Phase One Overview

Phase One establishes the initial application structure required for users to interact with Verify AI.

The current frontend includes:

* User Login
* User Registration
* Protected application routes
* Dashboard page
* API communication layer
* Axios configuration
* React + TypeScript application structure
* Vite-based development environment

The project is structured so that additional functionality can be added in later phases without rebuilding the application foundation.

---

## 🛠️ Technology Stack

| Technology     | Purpose                                |
| -------------- | -------------------------------------- |
| **React**      | Frontend UI framework                  |
| **TypeScript** | Type-safe JavaScript development       |
| **Vite**       | Frontend development and build tooling |
| **Axios**      | HTTP/API communication                 |
| **Zod**        | Data/schema validation dependency      |
| **CSS**        | Application styling                    |

---

## 🏗️ Project Structure

```text
VerifyAI/
│
├── src/
│   ├── api/
│   │   └── axios.ts
│   │
│   ├── assets/
│   │   ├── hero.png
│   │   ├── react.svg
│   │   └── vite.svg
│   │
│   ├── components/
│   │   └── ProtectedRoute.tsx
│   │
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Login.tsx
│   │   └── Register.tsx
│   │
│   ├── services/
│   │   └── api.ts
│   │
│   ├── App.css
│   ├── App.tsx
│   ├── index.css
│   └── main.tsx
│
├── public/
│   ├── favicon.svg
│   └── icons.svg
│
└── README.md
```

The Phase One source structure separates pages, reusable components, API configuration, services, assets, and application-level files.

---

## 🔐 Authentication Flow

The frontend contains dedicated Login and Registration pages together with a protected-route component.

The intended high-level flow is:

```text
                ┌───────────────┐
                │     User      │
                └───────┬───────┘
                        │
             ┌──────────▼──────────┐
             │   Login / Register  │
             └──────────┬──────────┘
                        │
                        ▼
                 API Communication
                        │
                        ▼
                Authentication
                        │
              ┌─────────┴─────────┐
              │                   │
          Authenticated       Not Authenticated
              │                   │
              ▼                   ▼
         Dashboard          Login / Register
```

`ProtectedRoute.tsx` provides the frontend structure for restricting access to protected application pages, while `Login.tsx`, `Register.tsx`, and `Dashboard.tsx` represent the primary authentication/application pages.

---

## 🔌 API Architecture

Phase One separates API communication from the UI.

### Axios Configuration

```text
src/api/axios.ts
```

This file provides the centralized Axios/API configuration layer.

### API Services

```text
src/services/api.ts
```

The service layer provides a dedicated place for communicating with the application's backend instead of placing API logic directly inside UI components.

This separation makes the application easier to maintain as the number of API endpoints grows.

---

## 🧩 Frontend Architecture

The application follows a basic separation-of-concerns structure:

```text
React Application
│
├── Pages
│   ├── Login
│   ├── Register
│   └── Dashboard
│
├── Components
│   └── ProtectedRoute
│
├── API Layer
│   └── Axios Configuration
│
├── Service Layer
│   └── API Services
│
└── Assets / Styling
```

This structure creates a foundation for expanding Verify AI into a larger application.

---

## ▶️ Running the Frontend

### 1. Clone the repository

```bash
git clone <repository-url>
cd VerifyAI
```

### 2. Install dependencies

```bash
npm install
```

### 3. Start the development server

```bash
npm run dev
```

Vite will start the development environment and provide the local application URL.

---

## 📦 Build for Production

To create a production build:

```bash
npm run build
```

To preview the production build locally:

```bash
npm run preview
```

---

## 📌 Phase One Deliverables

### Frontend Foundation

* React application initialized
* TypeScript integration
* Vite development environment
* Application styling structure
* Static assets organized

### Authentication UI

* Login page
* Registration page
* Dashboard page
* Protected route component

### API Foundation

* Centralized Axios configuration
* Dedicated API service layer

---

## 🔮 Future Development

Verify AI is being developed incrementally.

Future phases can build on the Phase One foundation by adding additional backend functionality, AI capabilities, verification workflows, data management, user features, and other application modules.

---

## 📚 Learning Objectives

Phase One also serves as a practical foundation for understanding:

* React component architecture
* TypeScript in frontend development
* Client-side routing and protected routes
* API communication
* Axios
* Service-layer architecture
* Frontend project organization
* Authentication flow design
* Separation of concerns

---

## 📈 Development Status

**Current Phase:** Phase One
**Status:** Foundation / Authentication Layer

```text
Phase One
████████████████████  Complete
```

---

## 👩‍💻 Project

**Verify AI**

Built as a phased software-development project with an emphasis on learning, clean architecture, maintainability, and incremental feature development.

---

## 📄 License

License information will be added as the project progresses.
