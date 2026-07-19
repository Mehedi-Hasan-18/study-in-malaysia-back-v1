# BUILD SPEC — Malaysia University Admission Portal (Backend)

> **Read this entire file before writing any code.** This is a sequential build spec. Follow the phases in order — later phases depend on models/endpoints created in earlier ones. Do not skip Phase 0.

---

## Phase 0 — Stack & Project Setup

**Stack (do not substitute unless told otherwise):**
- Python + Django + Django REST Framework (DRF)
- PostgreSQL
- Firebase Authentication (Google Login) — Django verifies the Firebase ID token, does not issue its own login
- Cloudinary — used for **all** file storage (images AND PDFs, one provider, not S3)

**Setup tasks:**
1. Create Django project `config/` and app folder layout exactly as below.
2. Install: `djangorestframework`, `django-cloudinary-storage`, `cloudinary`, `psycopg2-binary`, `firebase-admin`, `django-filter`.
3. Configure PostgreSQL connection in `settings.py`.
4. Configure Cloudinary in `settings.py` using `CLOUDINARY_STORAGE` dict (cloud_name, api_key, api_secret from env vars).
5. All API routes are versioned under `/api/v1/`.

**App structure (create empty Django apps for each):**
```
backend/
  accounts/
  universities/
  faculties/
  programs/
  intakes/
  tuition/
  scholarships/
  applications/
  documents/
  wishlist/
  dashboard/
  news/
  notifications/
  common/          # shared: Country, State, City models + Cloudinary helpers
  config/
  manage.py
```

**Acceptance check for Phase 0:** `python manage.py runserver` boots with no errors, admin panel loads at `/admin/`, Postgres connection confirmed.

---

## Phase 1 — Common / Location Models

Build these in `common/models.py` first. Every other app's models will FK into these.

```python
class Country(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=5, unique=True)  # e.g. "MY", "BD"

class State(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
```

Register all three in `admin.py` with `list_display` and `search_fields=['name']`.

**Acceptance check:** Can create Country → State → City in Django admin with correct FK dropdowns.

---

## Phase 2 — Cloudinary Upload Helper (build once, reuse everywhere)

Create `common/cloudinary_utils.py` with two functions used by every app that stores files:

```python
def upload_file(file, folder, resource_type="auto"):
    """
    resource_type: "image" for photos/logos, "raw" for PDFs.
    Returns dict: {public_id, secure_url, resource_type, format}
    Save all four fields on the model — never store only the URL.
    """

def delete_file(public_id, resource_type="auto"):
    """Call this in every model's delete() or in a pre_delete signal.
    Never let a DB row disappear without deleting its Cloudinary file."""
```

**Folder convention (use exactly this, every model that uploads a file follows this pattern):**
```
universities/{university_id}/gallery/
universities/{university_id}/logo/
fees/{university_id}/{program_id}/
scholarships/{scholarship_id}/brochure/
profiles/{user_id}/photo/
applications/{application_id}/{document_type}/
```

**Rules the agent must follow for every file field going forward:**
- Images (logos, gallery, photos) → `resource_type="image"`
- PDFs (fees, brochures, transcripts) → `resource_type="raw"`
- Model stores: `cloudinary_public_id`, `cloudinary_url`, `resource_type`, `file_format` — 4 separate fields, not a single URL field.
- On model delete, call `delete_file()` with the stored `public_id`.
- Uploads from authenticated users (passport, transcripts) use a **signed** upload preset, not unsigned.

---

## Phase 3 — Authentication (`accounts/`)

**Model:**
```python
class User(models.Model):
    firebase_uid = models.CharField(max_length=128, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=200)
    date_joined = models.DateTimeField(auto_now_add=True)

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    country = models.ForeignKey('common.Country', on_delete=models.SET_NULL, null=True)
    photo_public_id = models.CharField(max_length=255, blank=True)
    photo_url = models.URLField(blank=True)
```
> Passport and certificate are NOT stored on the profile. Those are per-application documents (a student may use a different transcript or updated passport per application) — they live on `ApplicationDocument` in Phase 7, scoped to a specific `application_id`. The profile only holds account-level data: contact info and an avatar photo.

**Middleware/dependency:** Write a DRF authentication class that:
1. Reads `Authorization: Bearer <firebase_id_token>` header.
2. Verifies it via `firebase_admin.auth.verify_id_token()`.
3. Looks up or creates the `User` row by `firebase_uid`.
4. Attaches `request.user`.

**Endpoints to build:**
```
POST   /api/v1/auth/firebase-login/     → verify token, create/get User, return session info
POST   /api/v1/auth/logout/             → invalidate session (client just drops token; log server-side if needed)
GET    /api/v1/auth/me/                 → return current user + profile

GET    /api/v1/profile/                 → get StudentProfile
PUT    /api/v1/profile/                 → update StudentProfile fields (not files)

POST   /api/v1/profile/photo/           → upload to Cloudinary (image), save 2 fields, delete old file if replacing
```

> No `/profile/passport/` or `/profile/certificate/` endpoints — those documents are uploaded per-application via `/applications/{id}/documents/` in Phase 7, not attached to the general profile.

**Acceptance check:** A test Firebase token round-trips through `/auth/firebase-login/` and creates a `User` + empty `StudentProfile`.

---

## Phase 4 — University, Faculty, Program (core catalog)

Build in this exact FK order: University → Faculty → Program → ProgramRequirement.

```python
# universities/models.py
class University(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=300)
    full_description = models.TextField()
    university_type = models.CharField(choices=[("public","Public"),("private","Private")], max_length=10)
    state = models.ForeignKey('common.State', on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey('common.City', on_delete=models.SET_NULL, null=True)
    ranking_tier = models.CharField(max_length=50, blank=True)  # powers ?ranking=top
    is_featured = models.BooleanField(default=False)
    logo_public_id = models.CharField(max_length=255, blank=True)
    logo_url = models.URLField(blank=True)
    cover_public_id = models.CharField(max_length=255, blank=True)
    cover_url = models.URLField(blank=True)
    website = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    established_year = models.IntegerField(null=True, blank=True)
    total_students = models.IntegerField(null=True, blank=True)

class Gallery(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='gallery')
    image_public_id = models.CharField(max_length=255)
    image_url = models.URLField()
    caption = models.CharField(max_length=200, blank=True)
    display_order = models.IntegerField(default=0)

# faculties/models.py
class Faculty(models.Model):
    university = models.ForeignKey('universities.University', on_delete=models.CASCADE, related_name='faculties')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)

# programs/models.py
class Program(models.Model):
    faculty = models.ForeignKey('faculties.Faculty', on_delete=models.CASCADE, related_name='programs')
    university = models.ForeignKey('universities.University', on_delete=models.CASCADE, related_name='programs')
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    level = models.CharField(choices=[("diploma","Diploma"),("bachelor","Bachelor"),("master","Master"),("phd","PhD")], max_length=20)
    duration_months = models.IntegerField()
    language = models.CharField(max_length=50, default="English")
    description = models.TextField(blank=True)
    tuition_fee_display = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # denormalized for fast ?tuition_max= filtering

class ProgramRequirement(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='requirements')
    requirement_type = models.CharField(max_length=50)  # academic / english / document
    description = models.TextField()
```

**Endpoints:**
```
GET    /api/v1/universities/
GET    /api/v1/universities/{id}/
POST   /api/v1/universities/               (admin only)
PUT    /api/v1/universities/{id}/          (admin only)
DELETE /api/v1/universities/{id}/          (admin only)

GET /api/v1/universities/?search=cyberjaya
GET /api/v1/universities/?state=selangor
GET /api/v1/universities/?city=kuala-lumpur
GET /api/v1/universities/?featured=true
GET /api/v1/universities/?type=private
GET /api/v1/universities/?ranking=top

GET /api/v1/universities/{id}/faculties/
GET /api/v1/universities/{id}/programs/
GET /api/v1/universities/{id}/gallery/
GET /api/v1/universities/{id}/intakes/
GET /api/v1/universities/{id}/fees/
GET /api/v1/universities/{id}/scholarships/

GET    /api/v1/faculties/
GET    /api/v1/faculties/{id}/
GET    /api/v1/universities/{id}/faculties/

GET    /api/v1/programs/
GET    /api/v1/programs/{id}/
POST   /api/v1/programs/                   (admin only)
PUT    /api/v1/programs/{id}/               (admin only)
DELETE /api/v1/programs/{id}/               (admin only)

GET /api/v1/programs/?search=computer
GET /api/v1/programs/?level=diploma|bachelor|master
GET /api/v1/programs/?university=5
GET /api/v1/programs/?faculty=2
GET /api/v1/programs/?duration=3
GET /api/v1/programs/?tuition_max=30000

GET /api/v1/programs/{id}/requirements/
GET /api/v1/programs/{id}/fees/
```

Use `django-filter` FilterSet classes for each list endpoint rather than hand-parsing query params.

**Acceptance check:** Can create 1 University → 1 Faculty → 2 Programs via admin, and `GET /api/v1/universities/{id}/programs/` returns both.

---

## Phase 5 — Intakes & Tuition Fees

```python
# intakes/models.py
class Intake(models.Model):
    university = models.ForeignKey('universities.University', on_delete=models.CASCADE, related_name='intakes')
    program = models.ForeignKey('programs.Program', on_delete=models.SET_NULL, null=True, blank=True, related_name='intakes')
    name = models.CharField(max_length=100)  # "January 2027"
    application_deadline = models.DateField()
    start_date = models.DateField()

# tuition/models.py
class TuitionFee(models.Model):
    program = models.ForeignKey('programs.Program', on_delete=models.CASCADE, related_name='fees')
    university = models.ForeignKey('universities.University', on_delete=models.CASCADE, related_name='fees')
    tuition_amount = models.DecimalField(max_digits=10, decimal_places=2)
    registration_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    misc_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    currency = models.CharField(max_length=10, default="MYR")
    bdt_equivalent = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    academic_year = models.CharField(max_length=20)
    pdf_public_id = models.CharField(max_length=255, blank=True)
    pdf_url = models.URLField(blank=True)
```

**Endpoints:**
```
GET /api/v1/intakes/
GET /api/v1/intakes/{id}/
GET /api/v1/universities/{id}/intakes/

GET /api/v1/fees/
GET /api/v1/fees/{id}/
GET /api/v1/fees/{id}/download/        → 302 redirect to Cloudinary pdf_url (don't proxy the file through Django)
GET /api/v1/universities/{id}/fees/
```

**Acceptance check:** Upload a real PDF through admin, confirm `/fees/{id}/download/` redirects to a working Cloudinary URL.

---

## Phase 6 — Scholarships

```python
class Scholarship(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    university = models.ForeignKey('universities.University', on_delete=models.SET_NULL, null=True, blank=True, related_name='scholarships')
    coverage_percentage = models.IntegerField()  # 0-100
    eligible_level = models.CharField(max_length=20)
    eligible_country = models.CharField(max_length=100, blank=True)
    application_deadline = models.DateField()
    brochure_public_id = models.CharField(max_length=255, blank=True)
    brochure_url = models.URLField(blank=True)

class ScholarshipApplication(models.Model):
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
```

**Endpoints:**
```
GET    /api/v1/scholarships/
GET    /api/v1/scholarships/{id}/
POST   /api/v1/scholarships/                (admin only)
PUT    /api/v1/scholarships/{id}/           (admin only)
DELETE /api/v1/scholarships/{id}/           (admin only)

GET /api/v1/scholarships/?search=engineering
GET /api/v1/scholarships/?country=Bangladesh
GET /api/v1/scholarships/?coverage=100
GET /api/v1/scholarships/?level=bachelor|master
GET /api/v1/scholarships/?university=5
GET /api/v1/scholarships/?deadline_before=2026-12-31

POST   /api/v1/scholarships/{id}/save/      (auth required — wishlist toggle)
DELETE /api/v1/scholarships/{id}/save/
POST   /api/v1/scholarships/{id}/apply/     (auth required — creates ScholarshipApplication)
GET    /api/v1/my-scholarships/             (auth required — list current user's applications)
```

---

## Phase 7 — Applications & Documents

```python
# applications/models.py
class Application(models.Model):
    STATUS_CHOICES = [("draft","Draft"),("submitted","Submitted"),("under_review","Under Review"),
                       ("more_docs_needed","More Documents Needed"),("approved","Approved"),("rejected","Rejected")]
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='applications')
    program = models.ForeignKey('programs.Program', on_delete=models.CASCADE)
    intake = models.ForeignKey('intakes.Intake', on_delete=models.SET_NULL, null=True)
    status = models.CharField(choices=STATUS_CHOICES, default="draft", max_length=20)
    submitted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# documents/models.py
class ApplicationDocument(models.Model):
    DOC_TYPES = [("passport","Passport"),("transcript","Academic Transcript"),("certificate","Certificate"),
                 ("english_test","English Test"),("personal_statement","Personal Statement"),
                 ("resume","Resume"),("other","Other")]
    application = models.ForeignKey('applications.Application', on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(choices=DOC_TYPES, max_length=30)
    file_public_id = models.CharField(max_length=255)
    file_url = models.URLField()
    resource_type = models.CharField(max_length=10)  # "image" or "raw"
    uploaded_at = models.DateTimeField(auto_now_add=True)
```

**Endpoints:**
```
POST   /api/v1/applications/
GET    /api/v1/applications/
GET    /api/v1/applications/{id}/
PUT    /api/v1/applications/{id}/
DELETE /api/v1/applications/{id}/

POST /api/v1/applications/{id}/submit/       → sets status=submitted, submitted_at=now()
GET  /api/v1/applications/{id}/status/
GET  /api/v1/applications/history/

POST   /api/v1/applications/{id}/documents/   → upload to Cloudinary, folder: applications/{id}/{document_type}/
GET    /api/v1/applications/{id}/documents/
DELETE /api/v1/documents/{id}/                → delete from Cloudinary too
```

**Admin actions to wire into Django Admin (not necessarily REST endpoints):** Approve Application, Reject Application, Request More Documents, Update Status — implement as Django Admin `actions=[...]` on the `Application` admin class, each transitioning `status` and optionally triggering a Notification.

---

## Phase 8 — Wishlist, News/Blog, FAQ, Contact, Dashboard, Notifications

```python
class WishlistUniversity(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    university = models.ForeignKey('universities.University', on_delete=models.CASCADE)

class WishlistScholarship(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    scholarship = models.ForeignKey('scholarships.Scholarship', on_delete=models.CASCADE)

class News(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    cover_public_id = models.CharField(max_length=255, blank=True)
    cover_url = models.URLField(blank=True)
    published_at = models.DateTimeField()

class Blog(models.Model):
    # same shape as News, plus:
    author = models.CharField(max_length=100, blank=True)
    tags = models.CharField(max_length=300, blank=True)  # comma-separated or use a M2M Tag model

class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    display_order = models.IntegerField(default=0)

class Inquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    message = models.CharField(max_length=300)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Endpoints:**
```
GET    /api/v1/wishlist/universities/
POST   /api/v1/wishlist/universities/
DELETE /api/v1/wishlist/universities/{id}/

GET    /api/v1/wishlist/scholarships/
POST   /api/v1/wishlist/scholarships/
DELETE /api/v1/wishlist/scholarships/{id}/

GET /api/v1/news/
GET /api/v1/news/{id}/
GET /api/v1/blogs/
GET /api/v1/blogs/{id}/

POST /api/v1/contact/
POST /api/v1/inquiry/

GET /api/v1/faq/
GET /api/v1/faq/{id}/

GET /api/v1/dashboard/
GET /api/v1/dashboard/recent-applications/
GET /api/v1/dashboard/statistics/
GET /api/v1/dashboard/profile-completion/

GET    /api/v1/notifications/
PUT    /api/v1/notifications/{id}/read/
DELETE /api/v1/notifications/{id}/
```

---

## Cross-Cutting Rules (apply to every phase above)

1. **Pagination** — every list endpoint uses DRF `PageNumberPagination` or `LimitOffsetPagination`. Never return an unpaginated full table.
2. **Filtering/search/ordering** — use `django-filter` + DRF `SearchFilter`/`OrderingFilter` backends, not manual `request.GET.get()` parsing.
3. **Auth** — every endpoint under `/profile/`, `/applications/`, `/wishlist/`, `/my-scholarships/`, `/notifications/`, and any `save/`/`apply/` action requires a valid Firebase token. Everything else (`/universities/`, `/programs/`, `/scholarships/` GET, `/faq/`, `/news/`) is public read.
4. **File uploads** — always go through the `common/cloudinary_utils.py` helper from Phase 2. Never call the Cloudinary SDK directly from a view.
5. **Deletion** — any model with a Cloudinary file must delete that file (via `delete_file()`) before or during its own deletion. Use a `pre_delete` signal or override `.delete()`.
6. **Response format** — consistent JSON shape across all endpoints: `{"data": ..., "meta": {...}}` for lists, `{"data": ...}` for single objects, proper 4xx/5xx status codes on error with `{"error": "message"}`.
7. **Indexes** — add DB indexes on: `University.state`, `University.city`, `Program.level`, `Program.university`, `Scholarship.eligible_country`, `Application.status`.

---

## Build Order Summary (for the agent to track progress)

- [ ] Phase 0 — Project + Cloudinary + Postgres setup
- [ ] Phase 1 — Country / State / City
- [ ] Phase 2 — Cloudinary upload helper
- [ ] Phase 3 — Auth + Profile
- [ ] Phase 4 — University + Faculty + Program + Requirements
- [ ] Phase 5 — Intakes + Tuition Fees
- [ ] Phase 6 — Scholarships
- [ ] Phase 7 — Applications + Documents
- [ ] Phase 8 — Wishlist + News/Blog + FAQ + Contact + Dashboard + Notifications

**Do not start Phase N+1 until Phase N's acceptance check passes.**

---

## Data Seeding Checklist (Django Admin)

Run this after Phase 4 is done, so there's real data to test Phases 5-8 against:

1. 1 Country → 1 State → 1–2 Cities
2. 3–5 Universities (each with a logo + at least 1 gallery image)
3. 1–2 Faculties per university
4. 2–3 Programs per faculty (mix diploma/bachelor for filter testing)
5. 1 TuitionFee + 1 real uploaded PDF per program
6. 1 Intake per university
7. 2–3 Scholarships (mix of university-specific and general/external)
8. 5–8 FAQ entries

This is the minimum needed for every endpoint above to return non-empty, realistic data.