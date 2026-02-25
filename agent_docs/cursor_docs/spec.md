# Task Management System — System Specification

## Overview

A full-stack Task Management System with first-class Hebrew and RTL (right-to-left) support. The system allows users to create, organize, and track tasks with support for workspaces, labels, due dates, and collaboration.

---

## Design & UI Requirements

### Brand & Theme

- **Primary color:** `#3A5FCD`
- **Secondary color:** To be defined (suggest: `#5A7FED` for hover/active)
- **Background:** Light and dark theme support; default light: `#F8F9FA`, dark: `#1A1D23`
- **Text:** High contrast for accessibility; RTL-aware line height and letter-spacing

### RTL Support (Mandatory)

- **RTL support is mandatory for all user-facing screens.**
- Layout must flip correctly: navigation on the right, content flow right-to-left.
- All text alignment follows direction (RTL for Hebrew, LTR for English when applicable).
- Icons that imply direction (e.g. arrows, chevrons) must mirror in RTL.
- Use CSS `dir="rtl"` and logical properties (`margin-inline-start`, `padding-inline-end`, etc.) throughout.
- Form labels, placeholders, and error messages must respect document/UI direction.
- Date and number formatting must follow locale (e.g. Hebrew locale for RTL users).

### Responsiveness

- Mobile-first; breakpoints: 320px, 768px, 1024px, 1280px.
- Touch-friendly targets (min 44px) for mobile.
- Sidebar collapses to drawer on small screens in RTL-aware manner.

### Accessibility

- WCAG 2.1 AA target: contrast, focus indicators, keyboard navigation, screen reader labels.
- `lang` and `dir` set on `<html>` and updated when switching locale.

---

## Database Schema (PostgreSQL)

### Tables

#### `users`

| Column           | Type         | Constraints                    | Description                |
|------------------|--------------|--------------------------------|----------------------------|
| id               | UUID         | PRIMARY KEY, DEFAULT gen_random_uuid() | User ID            |
| email            | VARCHAR(255) | NOT NULL, UNIQUE               | Login email                |
| password_hash    | VARCHAR(255) | NOT NULL                       | Bcrypt/Argon2 hash         |
| display_name     | VARCHAR(100) |                                | Display name               |
| locale           | VARCHAR(10)  | DEFAULT 'he'                   | e.g. 'he', 'en'            |
| rtl              | BOOLEAN      | DEFAULT true                   | Prefer RTL UI              |
| created_at       | TIMESTAMPTZ  | DEFAULT NOW()                  |                            |
| updated_at       | TIMESTAMPTZ  | DEFAULT NOW()                  |                            |

#### `workspaces`

| Column     | Type         | Constraints                    | Description        |
|------------|--------------|--------------------------------|--------------------|
| id         | UUID         | PRIMARY KEY, DEFAULT gen_random_uuid() | Workspace ID |
| owner_id   | UUID         | NOT NULL, REFERENCES users(id) ON DELETE CASCADE | |
| name       | VARCHAR(150) | NOT NULL                       | Workspace name     |
| created_at | TIMESTAMPTZ  | DEFAULT NOW()                  |                    |
| updated_at | TIMESTAMPTZ  | DEFAULT NOW()                  |                    |

#### `workspace_members`

| Column       | Type   | Constraints                                    | Description     |
|--------------|--------|------------------------------------------------|-----------------|
| workspace_id | UUID   | NOT NULL, REFERENCES workspaces(id) ON DELETE CASCADE | |
| user_id      | UUID   | NOT NULL, REFERENCES users(id) ON DELETE CASCADE | |
| role         | VARCHAR(20) | NOT NULL, CHECK (role IN ('owner','admin','member')) | |
| PRIMARY KEY  | (workspace_id, user_id)                         |                 |

#### `projects`

| Column       | Type         | Constraints                    | Description     |
|--------------|--------------|--------------------------------|-----------------|
| id           | UUID         | PRIMARY KEY, DEFAULT gen_random_uuid() |      |
| workspace_id | UUID         | NOT NULL, REFERENCES workspaces(id) ON DELETE CASCADE | |
| name         | VARCHAR(150) | NOT NULL                       |                 |
| position     | INTEGER      | DEFAULT 0                      | Order in list   |
| created_at   | TIMESTAMPTZ  | DEFAULT NOW()                  |                 |
| updated_at   | TIMESTAMPTZ  | DEFAULT NOW()                  |                 |

#### `tasks`

| Column       | Type         | Constraints                    | Description     |
|--------------|--------------|--------------------------------|-----------------|
| id           | UUID         | PRIMARY KEY, DEFAULT gen_random_uuid() |      |
| project_id   | UUID         | NOT NULL, REFERENCES projects(id) ON DELETE CASCADE | |
| title        | VARCHAR(500) | NOT NULL                       |                 |
| description  | TEXT         |                                |                 |
| status       | VARCHAR(20)  | NOT NULL, DEFAULT 'todo'       | todo, in_progress, done |
| priority     | VARCHAR(20)  | DEFAULT 'medium'               | low, medium, high, urgent |
| due_date     | DATE         |                                |                 |
| position     | INTEGER      | DEFAULT 0                      | Order in list   |
| created_by   | UUID         | REFERENCES users(id)           |                 |
| created_at   | TIMESTAMPTZ  | DEFAULT NOW()                  |                 |
| updated_at   | TIMESTAMPTZ  | DEFAULT NOW()                  |                 |

#### `labels`

| Column       | Type         | Constraints                    | Description     |
|--------------|--------------|--------------------------------|-----------------|
| id           | UUID         | PRIMARY KEY, DEFAULT gen_random_uuid() |      |
| workspace_id | UUID         | NOT NULL, REFERENCES workspaces(id) ON DELETE CASCADE | |
| name         | VARCHAR(80)  | NOT NULL                       |                 |
| color        | VARCHAR(7)   | DEFAULT '#3A5FCD'              | Hex color       |
| created_at   | TIMESTAMPTZ  | DEFAULT NOW()                  |                 |

#### `task_labels`

| Column   | Type | Constraints                                    | Description |
|----------|------|------------------------------------------------|-------------|
| task_id  | UUID | NOT NULL, REFERENCES tasks(id) ON DELETE CASCADE |            |
| label_id | UUID | NOT NULL, REFERENCES labels(id) ON DELETE CASCADE |            |
| PRIMARY KEY | (task_id, label_id)                           |             |

#### `comments`

| Column     | Type         | Constraints                    | Description     |
|------------|--------------|--------------------------------|-----------------|
| id         | UUID         | PRIMARY KEY, DEFAULT gen_random_uuid() |      |
| task_id    | UUID         | NOT NULL, REFERENCES tasks(id) ON DELETE CASCADE | |
| user_id    | UUID         | NOT NULL, REFERENCES users(id) |                 |
| body       | TEXT         | NOT NULL                       |                 |
| created_at | TIMESTAMPTZ  | DEFAULT NOW()                  |                 |
| updated_at | TIMESTAMPTZ  | DEFAULT NOW()                  |                 |

### Indexes (recommended)

- `tasks(project_id)`, `tasks(status)`, `tasks(due_date)`
- `task_labels(task_id)`, `task_labels(label_id)`
- `workspace_members(user_id)`, `workspace_members(workspace_id)`
- `comments(task_id)`

---

## API Conventions (High Level)

- REST or GraphQL; all responses JSON.
- Authentication: Bearer JWT in `Authorization` header.
- Locale/RTL can be sent in `Accept-Language` or request body for user prefs.
- Pagination: `limit` + `offset` or cursor-based for task lists.
- Errors: consistent shape e.g. `{ "error": { "code": "...", "message": "..." } }`.

---

## Out of Scope (Current Spec)

- Real-time presence/typing.
- File attachments (future phase).
- Email/push notifications (future phase).

---

*Document version: 1.0 | Last updated: 2025-02-21*
