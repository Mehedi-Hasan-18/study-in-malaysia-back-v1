# PROJECT_ARCHITECTURE.md

## Malaysia University Admission Portal — System Architecture

This document describes how the system is structured, how requests flow through it, and why each major decision was made. Read this before touching the build spec or database schema — those describe *what* to build, this describes *how the pieces fit together*.

---

## 1. High-level overview

The portal is a decoupled system: a Django REST API backend serves a React/Next.js frontend. There is no server-rendered Django templating in the student-facing product — Django's only UI surface is the built-in Admin panel, used internally by staff to manage universities, programs, fees, and applications.

```
┌─────────────────┐        HTTPS/JSON         ┌──────────────────────┐
│  Next.js/React    │ ────────────────────────▶ │  Django REST API      │
│  (student-facing)  │ ◀──────────────────────── │  /api/v1/             │
└─────────────────┘                             └──────────────────────┘
                                                          │
                        ┌─────────────────────────────────┼─────────────────────────────┐
                        ▼                                 ▼                             ▼
                ┌───────────────┐               ┌──────────────────┐         ┌───────────────────┐
                │  PostgreSQL     │               │  Firebase Auth     │         │  Cloudinary          │
                │  (system of      │               │  (Google Login,    │         │  (all images + PDFs) │
                │   record)        │               │   ID token verify)  │         │                     │
                └───────────────┘               └──────────────────┘         └───────────────────┘
                        ▲
                        │
                ┌───────────────┐
                │  Django Admin   │
                │  (staff only)    │
                └───────────────┘
```

**Why this split:** Firebase owns identity (nobody wants to build password reset flows from scratch), Postgres owns structured relational data (universities, programs, applications — all deeply relational), and Cloudinary owns binary files (so the Django app server never touches file bytes directly, keeping it stateless and easy to horizontally scale).

---

## 2. Request lifecycle

Every authenticated request follows this path:

```
1. Frontend attaches Firebase ID token → Authorization: Bearer <token>
2. Request hits Django → custom DRF authentication class intercepts it
3. Auth class calls firebase_admin.auth.verify_id_token(token)
4. On success: look up or create local `app_user` row by firebase_uid
5. request.user is set → view executes with a real DB-backed user
6. View talks to Postgres via Django ORM, and/or Cloudinary via common/cloudinary_utils.py
7. Response serialized by DRF serializer → consistent {"data": ..., "meta": ...} JSON
```

Public endpoints (`GET /universities/`, `GET /programs/`, `GET /faq/`, etc.) skip steps 2–4 entirely — no token required, no `request.user` lookup, so browsing the catalog stays fast and cache-friendly.

**Why verify on every request instead of issuing our own session token:** Firebase ID tokens are short-lived (1 hour) and self-contained, so Django never needs to store server-side sessions. The tradeoff is a token verification call on every authenticated request — acceptable here since `firebase_admin` caches Google's public signing keys locally and verification is a local JWT check, not a network round-trip per request.

---

## 3. Module boundaries

Each Django app owns exactly one concern and only reaches into another app's models via defined foreign keys — never by importing another app's internal logic directly.

| App | Owns | Depends on |
|---|---|---|
| `common` | Country/State/City, Cloudinary upload helper | — |
| `accounts` | User, StudentProfile, Firebase auth class | common |
| `universities` | University, Gallery | common |
| `faculties` | Faculty | universities |
| `programs` | Program, ProgramRequirement | faculties, universities |
| `intakes` | Intake | universities, programs |
| `tuition` | TuitionFee | programs, universities |
| `scholarships` | Scholarship, ScholarshipApplication | universities, accounts |
| `applications` | Application | accounts, programs, intakes |
| `documents` | ApplicationDocument | applications |
| `wishlist` | WishlistUniversity, WishlistScholarship | accounts, universities, scholarships |
| `dashboard` | Read-only aggregation views only — no models of its own | applications, accounts |
| `news` | News, Blog | — |
| `notifications` | Notification | accounts |

**Why split this granularly instead of one big `core` app:** Each app maps 1:1 to a section of the API spec and a phase in the build spec. This means a change to how Scholarships work never risks breaking Applications, and a new engineer (or a coding agent) can be pointed at exactly one app folder and understand its full scope without reading the rest of the codebase.

---

## 4. The Cloudinary layer

All file storage — profile photos, passports, certificates, university logos/galleries, tuition fee PDFs, scholarship brochures, application documents — goes through one shared module: `common/cloudinary_utils.py`. No view or model calls the Cloudinary SDK directly.

```
View/Serializer
      │
      ▼
common/cloudinary_utils.py
      │  upload_file(file, folder, resource_type)
      │  delete_file(public_id, resource_type)
      ▼
Cloudinary API
```

**Why centralize this:** Every file field across 6+ models follows the exact same pattern (upload → store `public_id` + `secure_url` → delete on record removal). Centralizing it means that pattern is written once, tested once, and any future change (e.g. switching upload presets, adding virus scanning, changing folder naming) happens in one file instead of six.

**Folder structure inside Cloudinary mirrors the DB relationships**, so a support engineer can find a file in the Cloudinary media library just by knowing the record's IDs:
```
universities/{university_id}/logo/
universities/{university_id}/gallery/
fees/{university_id}/{program_id}/
scholarships/{scholarship_id}/brochure/
profiles/{user_id}/photo|passport|certificate/
applications/{application_id}/{document_type}/
```

**Resource type matters:** images use `resource_type="image"`, PDFs use `resource_type="raw"`. Cloudinary treats these differently for delivery URLs and transformations (e.g. generating a JPG thumbnail of page 1 of a PDF only works if it was uploaded correctly as `raw` with the right flags) — this distinction is stored explicitly on every file-owning model, not inferred at read time.

---

## 5. Authentication & authorization model

```
Public (no token)          Authenticated (valid Firebase token)        Admin (Django staff)
──────────────────         ─────────────────────────────────           ─────────────────────
GET /universities/         GET/PUT /profile/                           POST/PUT/DELETE
GET /programs/             POST /profile/photo/                        /universities/
GET /scholarships/         POST /applications/                         /programs/
GET /faq/, /news/          POST /scholarships/{id}/apply|save/         /scholarships/
GET /fees/{id}/download/   GET /wishlist/*, /notifications/            /fees/
                           GET /dashboard/*                            Application status
                                                                        transitions
```

Three tiers, enforced at two different layers:
- **Public vs authenticated** — enforced per-view via DRF permission classes (`AllowAny` vs a custom `IsFirebaseAuthenticated`).
- **Authenticated vs admin** — enforced via Django's built-in `is_staff` flag. Admin-only write endpoints (creating/editing Universities, Programs, etc.) check `request.user.is_staff` in addition to being authenticated; the same checks gate access to `/admin/`.

**Why not a custom roles/permissions table:** At this stage there's exactly one elevated role (staff/admin) and one regular role (student). Django's built-in `is_staff` flag already does this correctly and is battle-tested — a custom RBAC table would be premature complexity until the product needs finer-grained roles (e.g. "university partner" accounts that can only edit their own university's data).

---

## 6. Data flow: student application journey

This is the most complex flow in the system and worth tracing end-to-end:

```
1. Student browses Programs (public, no auth)
2. Student logs in via Firebase Google login → StudentProfile created/fetched
3. Student completes profile (phone, country, uploads a photo → Cloudinary)
4. Student creates Application (status="draft") tied to a Program + Intake
5. Student uploads ApplicationDocuments (passport, transcript, certificate, personal statement,
   etc. → Cloudinary, folder scoped to this specific application — these are per-application,
   not stored on the profile)
6. Student calls POST /applications/{id}/submit/ → status="submitted", submitted_at=now()
7. Staff reviews in Django Admin → uses an admin action to transition status:
   submitted → under_review → approved/rejected, or → more_docs_needed
8. Each status transition creates a Notification row for that student
9. Student polls GET /applications/{id}/status/ or sees it in /dashboard/recent-applications/
10. Frontend surfaces the Notification via GET /notifications/
```

**Why status transitions live in Django Admin actions rather than a public API `PATCH /applications/{id}/status/`:** Status changes are staff decisions with real consequences (an approval might trigger downstream processes like offer letter generation in the future). Keeping them as explicit, logged Admin actions creates an audit trail via Django's admin log automatically, versus a generic PATCH endpoint that any authenticated staff token could hit without that trail.

---

## 7. Read-heavy vs write-heavy paths

The catalog (Universities, Programs, Scholarships, FAQ, News) is read-heavy and public — most traffic. Applications/Documents/Notifications are write-heavy but low-volume (one student, a handful of writes per session).

**Design implication:** list endpoints for the catalog (`/universities/`, `/programs/`, `/scholarships/`) are the ones that need pagination, filtering, search, and eventually caching (e.g. a CDN or Django cache layer in front of `/universities/?featured=true` since that result barely changes hour to hour). The write-heavy application endpoints don't need this — they're inherently scoped to `request.user` and return small result sets.

If traffic grows, the catalog read paths are the first candidate for a read replica or a cache layer (Redis) — the schema doesn't need to change for this, only the view layer would gain a cache-check step before hitting Postgres.

---

## 8. Environment & configuration

```
config/settings.py reads from environment variables:

DATABASE_URL              → Postgres connection string
FIREBASE_CREDENTIALS_JSON → service account JSON for firebase_admin.initialize_app()
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
DJANGO_SECRET_KEY
DJANGO_DEBUG                (false in production)
ALLOWED_HOSTS
CORS_ALLOWED_ORIGINS       → the Next.js frontend's domain(s)
```

No secrets are hardcoded in `settings.py` — all of the above are read via `os.environ` (or `django-environ`) so the same codebase runs against a local dev Postgres/Cloudinary sandbox and a production instance without code changes, only environment differences.

---

## 9. Deployment shape

```
┌────────────────────┐        ┌──────────────────────┐
│  Next.js frontend     │        │  Django API (this repo) │
│  (Vercel or similar)  │──────▶│  (Railway/Render/EC2,   │
│                       │        │   gunicorn + nginx)      │
└────────────────────┘        └──────────────────────┘
                                          │
                        ┌──────────────────┼──────────────────┐
                        ▼                  ▼                  ▼
                 ┌─────────────┐   ┌──────────────┐   ┌───────────────┐
                 │  PostgreSQL   │   │  Firebase      │   │  Cloudinary     │
                 │  (managed)     │   │  (managed)      │   │  (managed)      │
                 └─────────────┘   └──────────────┘   └───────────────┘
```

The Django app itself is stateless (no local file storage, no server-side sessions) — every request is fully served from Postgres + the Firebase token + Cloudinary URLs. This means it can run behind a load balancer with multiple instances with zero sticky-session concerns, which matters if this ever needs to scale beyond a single server during intake-deadline traffic spikes.

---

## 10. Security notes specific to this system

- **Signed uploads for sensitive documents.** Passport, transcript, and certificate uploads (via `ApplicationDocument`, scoped to a specific application) use signed Cloudinary upload presets — never unsigned — since these are private student documents, not public marketing images like university logos.
- **Firebase token verification, not trust.** The `Authorization` header token is verified against Firebase's public keys on every request via `firebase_admin`, not decoded and trusted blindly.
- **File type/size validation happens before the Cloudinary call**, not after — reject bad uploads at the Django view layer so invalid files never reach external storage.
- **Admin-only write endpoints check `is_staff` explicitly** in the view/permission class, not just "is this user authenticated" — a logged-in student should never be able to `POST /universities/`.
- **Cloudinary deletion is not optional.** Any model `.delete()` that owns a `public_id` must call `delete_file()` first (via override or `pre_delete` signal) — otherwise files pile up in Cloudinary storage indefinitely with no corresponding DB row to clean them up from.

---

## 11. How this maps to the other project docs

- **`university-portal-agent-build-spec.md`** — the phase-by-phase implementation order (build Phase 0 → 8 in sequence). This architecture doc explains *why* the phases are ordered and grouped that way.
- **`university-portal-database-schema.md`** — the literal table DDL. This architecture doc explains the relationships and lifecycle around those tables, not the columns themselves.
- Read this file first when onboarding a new engineer (or agent) to the codebase; read the build spec when actually writing code; reference the schema file when writing migrations or raw queries.