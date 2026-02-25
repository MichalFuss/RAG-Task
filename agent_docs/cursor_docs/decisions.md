# Technical Decisions Log

Record of technical decisions for the Task Management System (Hebrew/RTL). Format: **Date | Decision | Rationale.**

---

## 2025-02-21

### Frontend: React

- **Decision:** Use **React** for the frontend application.
- **Rationale:** Strong ecosystem, component model fits task/workspace UI, good i18n and RTL libraries (e.g. react-i18next, logical CSS with RTL), and team familiarity. Enables reusable components for lists, forms, and modals that must all respect RTL.

---

### Authentication: JWT

- **Decision:** Use **JWT (JSON Web Tokens)** for authentication.
- **Rationale:** Stateless auth fits REST APIs and scaling; works well with mobile or SPA. Access token (short-lived) + optional refresh token stored securely. No server-side session store required for basic auth. Decision to use HTTP-only cookie vs `localStorage` for refresh token to be confirmed in security review.

---

### Database: PostgreSQL

- **Decision:** Use **PostgreSQL** as the primary database.
- **Rationale:** ACID, JSON support if needed later, strong indexing, and good tooling. Schema supports users, workspaces, projects, tasks, labels, and comments with foreign keys and cascades. UUID primary keys for all main entities to avoid sequential ID leakage and ease distribution.

---

### RTL and Locale: Mandatory RTL for All Screens

- **Decision:** **RTL support is mandatory for all user-facing screens.**
- **Rationale:** Hebrew (and other RTL languages) require consistent RTL layout and text flow. Making it mandatory from day one avoids partial support and rework. Implementation via `dir="rtl"`, logical CSS properties, and RTL-aware components.

---

### Design: Primary Color #3A5FCD

- **Decision:** Set **primary brand color to `#3A5FCD`.**
- **Rationale:** Provides a clear, consistent accent for buttons, links, and selected states. Chosen for readability and contrast on light backgrounds; to be checked against WCAG AA in both light and dark themes.

---

### Documentation: .cursor_docs

- **Decision:** Keep project documentation in a **`.cursor_docs`** folder with `spec.md`, `decisions.md`, and `tasks.md`.
- **Rationale:** Single place for specs, decision history, and task tracking; easy to find and update; works well with Cursor and other tools that read markdown.

---

*Next decisions (e.g. state management, API style REST vs GraphQL, deployment) to be added here as made.*
