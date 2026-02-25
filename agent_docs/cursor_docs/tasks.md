# Task Management System — Tasks

Status key: **Done** | **In progress** | **Pending**

---

## Completed

- [x] **Project setup** — Create repo and folder structure.
- [x] **Documentation** — Add `.cursor_docs` with `spec.md`, `decisions.md`, `tasks.md`.
- [x] **System spec** — Define DB schema (Postgres), UI requirements, RTL and primary color (#3A5FCD).
- [x] **Technical decisions** — Log: React, JWT auth, PostgreSQL, mandatory RTL, primary color.

---

## In Progress

- [ ] **Environment** — Finalize `.env` and env loading for frontend and backend.

---

## Pending

### Backend

- [ ] **Database** — Create Postgres DB and run initial migration (users, workspaces, projects, tasks, labels, task_labels, comments).
- [ ] **Auth API** — Implement signup/login endpoints; issue and validate JWT.
- [ ] **Workspaces API** — CRUD workspaces and workspace membership.
- [ ] **Projects API** — CRUD projects within a workspace.
- [ ] **Tasks API** — CRUD tasks; filter by status, due date, labels; ordering.
- [ ] **Labels API** — CRUD labels; attach/detach to tasks.
- [ ] **Comments API** — Add/list/update/delete comments on tasks.

### Frontend

- [ ] **App shell** — React app with RTL support; set `dir` and `lang` from user/locale.
- [ ] **Theme** — Apply primary color `#3A5FCD` and ensure RTL layout (logical CSS, mirrored icons).
- [ ] **Auth screens** — Login/signup (RTL); wire to JWT.
- [ ] **Workspace list & create** — List workspaces, create new; RTL layout.
- [ ] **Project list & create** — Per-workspace projects; drag order if required.
- [ ] **Task list & detail** — List tasks (by status/project), task detail with description, due date, labels, comments.
- [ ] **Task create/edit** — Form with title, description, status, priority, due date, labels; RTL forms.
- [ ] **Labels UI** — Manage labels, assign to tasks; use label color in UI.
- [ ] **Responsive** — Mobile-first; sidebar as drawer on small screens (RTL-aware).
- [ ] **Accessibility** — Keyboard nav, focus, screen reader labels; WCAG 2.1 AA where applicable.

### DevOps / Quality

- [ ] **.env.example** — Document required env vars (DB URL, JWT secret, etc.).
- [ ] **.gitignore** — Ensure `.env` is ignored.
- [ ] **Tests** — Unit/integration for critical API and key frontend flows.
- [ ] **Deployment** — Decide hosting and CI for backend and frontend.

---

*Update this file as tasks are completed or new ones are added.*
