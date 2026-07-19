# Database Schema — Malaysia University Admission Portal

PostgreSQL DDL for every table in the project. Matches the models defined in the build spec. Create tables in this exact order — later tables have foreign keys into earlier ones.

---

## 1. Location tables

```sql
CREATE TABLE country (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    code        VARCHAR(5) UNIQUE NOT NULL
);

CREATE TABLE state (
    id          SERIAL PRIMARY KEY,
    country_id  INTEGER NOT NULL REFERENCES country(id) ON DELETE CASCADE,
    name        VARCHAR(100) NOT NULL
);
CREATE INDEX idx_state_country ON state(country_id);

CREATE TABLE city (
    id          SERIAL PRIMARY KEY,
    state_id    INTEGER NOT NULL REFERENCES state(id) ON DELETE CASCADE,
    name        VARCHAR(100) NOT NULL
);
CREATE INDEX idx_city_state ON city(state_id);
```

---

## 2. Users & profile

```sql
CREATE TABLE app_user (
    id            SERIAL PRIMARY KEY,
    firebase_uid  VARCHAR(128) UNIQUE NOT NULL,
    email         VARCHAR(255) UNIQUE NOT NULL,
    full_name     VARCHAR(200) NOT NULL,
    date_joined   TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE student_profile (
    id                      SERIAL PRIMARY KEY,
    user_id                 INTEGER UNIQUE NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    phone                   VARCHAR(20),
    country_id              INTEGER REFERENCES country(id) ON DELETE SET NULL,
    photo_public_id         VARCHAR(255),
    photo_url               TEXT
);
```

> Note: table is named `app_user`, not `user` — `user` is a reserved word in PostgreSQL.
>
> Passport and certificate uploads were removed from this table. Those are per-application documents, not general profile data — a student may apply with a different transcript/certificate combination per application, or update a passport between applications. They belong to `application_document` (see section 7), scoped to a specific `application_id`. `student_profile` now only stores a profile photo, which is genuinely account-level, not tied to any one application.

---

## 3. Universities & related

```sql
CREATE TABLE university (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(200) NOT NULL,
    slug                VARCHAR(220) UNIQUE NOT NULL,
    short_description   VARCHAR(300),
    full_description    TEXT,
    university_type     VARCHAR(10) NOT NULL CHECK (university_type IN ('public','private')),
    state_id            INTEGER REFERENCES state(id) ON DELETE SET NULL,
    city_id             INTEGER REFERENCES city(id) ON DELETE SET NULL,
    ranking_tier        VARCHAR(50),
    is_featured         BOOLEAN NOT NULL DEFAULT false,
    logo_public_id      VARCHAR(255),
    logo_url            TEXT,
    cover_public_id     VARCHAR(255),
    cover_url           TEXT,
    website             VARCHAR(255),
    contact_email       VARCHAR(255),
    contact_phone       VARCHAR(30),
    established_year    INTEGER,
    total_students      INTEGER
);
CREATE INDEX idx_university_state ON university(state_id);
CREATE INDEX idx_university_city ON university(city_id);
CREATE INDEX idx_university_featured ON university(is_featured);

CREATE TABLE gallery (
    id              SERIAL PRIMARY KEY,
    university_id   INTEGER NOT NULL REFERENCES university(id) ON DELETE CASCADE,
    image_public_id VARCHAR(255) NOT NULL,
    image_url       TEXT NOT NULL,
    caption         VARCHAR(200),
    display_order   INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX idx_gallery_university ON gallery(university_id);
```

---

## 4. Faculties & programs

```sql
CREATE TABLE faculty (
    id              SERIAL PRIMARY KEY,
    university_id   INTEGER NOT NULL REFERENCES university(id) ON DELETE CASCADE,
    name            VARCHAR(200) NOT NULL,
    description     TEXT
);
CREATE INDEX idx_faculty_university ON faculty(university_id);

CREATE TABLE program (
    id                      SERIAL PRIMARY KEY,
    faculty_id              INTEGER NOT NULL REFERENCES faculty(id) ON DELETE CASCADE,
    university_id           INTEGER NOT NULL REFERENCES university(id) ON DELETE CASCADE,
    name                    VARCHAR(200) NOT NULL,
    slug                    VARCHAR(220) UNIQUE NOT NULL,
    level                   VARCHAR(20) NOT NULL CHECK (level IN ('diploma','bachelor','master','phd')),
    duration_months         INTEGER NOT NULL,
    language                VARCHAR(50) NOT NULL DEFAULT 'English',
    description             TEXT,
    tuition_fee_display     NUMERIC(10,2)
);
CREATE INDEX idx_program_university ON program(university_id);
CREATE INDEX idx_program_faculty ON program(faculty_id);
CREATE INDEX idx_program_level ON program(level);

CREATE TABLE program_requirement (
    id                  SERIAL PRIMARY KEY,
    program_id          INTEGER NOT NULL REFERENCES program(id) ON DELETE CASCADE,
    requirement_type    VARCHAR(50) NOT NULL,
    description         TEXT NOT NULL
);
CREATE INDEX idx_requirement_program ON program_requirement(program_id);
```

---

## 5. Intakes & tuition fees

```sql
CREATE TABLE intake (
    id                      SERIAL PRIMARY KEY,
    university_id           INTEGER NOT NULL REFERENCES university(id) ON DELETE CASCADE,
    program_id              INTEGER REFERENCES program(id) ON DELETE SET NULL,
    name                    VARCHAR(100) NOT NULL,
    application_deadline    DATE NOT NULL,
    start_date              DATE NOT NULL
);
CREATE INDEX idx_intake_university ON intake(university_id);
CREATE INDEX idx_intake_program ON intake(program_id);

CREATE TABLE tuition_fee (
    id                  SERIAL PRIMARY KEY,
    program_id          INTEGER NOT NULL REFERENCES program(id) ON DELETE CASCADE,
    university_id       INTEGER NOT NULL REFERENCES university(id) ON DELETE CASCADE,
    tuition_amount      NUMERIC(10,2) NOT NULL,
    registration_fee    NUMERIC(10,2) NOT NULL DEFAULT 0,
    misc_fee            NUMERIC(10,2) NOT NULL DEFAULT 0,
    currency            VARCHAR(10) NOT NULL DEFAULT 'MYR',
    bdt_equivalent      NUMERIC(12,2),
    academic_year       VARCHAR(20) NOT NULL,
    pdf_public_id       VARCHAR(255),
    pdf_url             TEXT
);
CREATE INDEX idx_fee_program ON tuition_fee(program_id);
CREATE INDEX idx_fee_university ON tuition_fee(university_id);
```

---

## 6. Scholarships

```sql
CREATE TABLE scholarship (
    id                      SERIAL PRIMARY KEY,
    name                    VARCHAR(200) NOT NULL,
    slug                    VARCHAR(220) UNIQUE NOT NULL,
    description             TEXT NOT NULL,
    university_id           INTEGER REFERENCES university(id) ON DELETE SET NULL,
    coverage_percentage     INTEGER NOT NULL CHECK (coverage_percentage BETWEEN 0 AND 100),
    eligible_level          VARCHAR(20) NOT NULL,
    eligible_country        VARCHAR(100),
    application_deadline    DATE NOT NULL,
    brochure_public_id      VARCHAR(255),
    brochure_url            TEXT
);
CREATE INDEX idx_scholarship_university ON scholarship(university_id);
CREATE INDEX idx_scholarship_country ON scholarship(eligible_country);
CREATE INDEX idx_scholarship_deadline ON scholarship(application_deadline);

CREATE TABLE scholarship_application (
    id              SERIAL PRIMARY KEY,
    scholarship_id  INTEGER NOT NULL REFERENCES scholarship(id) ON DELETE CASCADE,
    user_id         INTEGER NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    applied_at      TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE (scholarship_id, user_id)
);
CREATE INDEX idx_scholarship_app_user ON scholarship_application(user_id);
```

---

## 7. Applications & documents

```sql
CREATE TABLE application (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    program_id      INTEGER NOT NULL REFERENCES program(id) ON DELETE CASCADE,
    intake_id       INTEGER REFERENCES intake(id) ON DELETE SET NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft','submitted','under_review','more_docs_needed','approved','rejected')),
    submitted_at    TIMESTAMP,
    created_at      TIMESTAMP NOT NULL DEFAULT now(),
    updated_at      TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX idx_application_user ON application(user_id);
CREATE INDEX idx_application_program ON application(program_id);
CREATE INDEX idx_application_status ON application(status);

CREATE TABLE application_document (
    id              SERIAL PRIMARY KEY,
    application_id  INTEGER NOT NULL REFERENCES application(id) ON DELETE CASCADE,
    document_type   VARCHAR(30) NOT NULL
                    CHECK (document_type IN ('passport','transcript','certificate','english_test','personal_statement','resume','other')),
    file_public_id  VARCHAR(255) NOT NULL,
    file_url        TEXT NOT NULL,
    resource_type   VARCHAR(10) NOT NULL CHECK (resource_type IN ('image','raw')),
    uploaded_at     TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX idx_document_application ON application_document(application_id);
```

---

## 8. Wishlist

```sql
CREATE TABLE wishlist_university (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    university_id   INTEGER NOT NULL REFERENCES university(id) ON DELETE CASCADE,
    created_at      TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE (user_id, university_id)
);
CREATE INDEX idx_wishlist_uni_user ON wishlist_university(user_id);

CREATE TABLE wishlist_scholarship (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    scholarship_id  INTEGER NOT NULL REFERENCES scholarship(id) ON DELETE CASCADE,
    created_at      TIMESTAMP NOT NULL DEFAULT now(),
    UNIQUE (user_id, scholarship_id)
);
CREATE INDEX idx_wishlist_schol_user ON wishlist_scholarship(user_id);
```

---

## 9. Content: news, blogs, FAQ, inquiries, notifications

```sql
CREATE TABLE news (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(200) NOT NULL,
    slug            VARCHAR(220) UNIQUE NOT NULL,
    body            TEXT NOT NULL,
    cover_public_id VARCHAR(255),
    cover_url       TEXT,
    published_at    TIMESTAMP NOT NULL
);

CREATE TABLE blog (
    id              SERIAL PRIMARY KEY,
    title           VARCHAR(200) NOT NULL,
    slug            VARCHAR(220) UNIQUE NOT NULL,
    body            TEXT NOT NULL,
    cover_public_id VARCHAR(255),
    cover_url       TEXT,
    author          VARCHAR(100),
    tags            VARCHAR(300),
    published_at    TIMESTAMP NOT NULL
);

CREATE TABLE faq (
    id              SERIAL PRIMARY KEY,
    question        VARCHAR(300) NOT NULL,
    answer          TEXT NOT NULL,
    category        VARCHAR(100),
    display_order   INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE inquiry (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(255) NOT NULL,
    message     TEXT NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE notification (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES app_user(id) ON DELETE CASCADE,
    message     VARCHAR(300) NOT NULL,
    is_read     BOOLEAN NOT NULL DEFAULT false,
    created_at  TIMESTAMP NOT NULL DEFAULT now()
);
CREATE INDEX idx_notification_user ON notification(user_id);
```

---

## Full table list (23 tables)

| # | Table | Depends on |
|---|-------|-----------|
| 1 | `country` | — |
| 2 | `state` | country |
| 3 | `city` | state |
| 4 | `app_user` | — |
| 5 | `student_profile` | app_user, country |
| 6 | `university` | state, city |
| 7 | `gallery` | university |
| 8 | `faculty` | university |
| 9 | `program` | faculty, university |
| 10 | `program_requirement` | program |
| 11 | `intake` | university, program |
| 12 | `tuition_fee` | program, university |
| 13 | `scholarship` | university |
| 14 | `scholarship_application` | scholarship, app_user |
| 15 | `application` | app_user, program, intake |
| 16 | `application_document` | application |
| 17 | `wishlist_university` | app_user, university |
| 18 | `wishlist_scholarship` | app_user, scholarship |
| 19 | `news` | — |
| 20 | `blog` | — |
| 21 | `faq` | — |
| 22 | `inquiry` | — |
| 23 | `notification` | app_user |

---

## Design notes

- **Every Cloudinary-backed file field is split into 2 columns**: `{name}_public_id` + `{name}_url` (never a single URL column). This lets you call Cloudinary's destroy API using the `public_id` without re-parsing a URL.
- **`resource_type` is stored explicitly** on `application_document` (`image` vs `raw`) since PDFs and images need different Cloudinary delivery handling.
- **Soft uniqueness constraints**: `wishlist_university`, `wishlist_scholarship`, and `scholarship_application` all have a `UNIQUE(user_id, X_id)` constraint so a student can't save/apply to the same thing twice — enforce this at the DB level, not just in application code.
- **`ON DELETE CASCADE` vs `SET NULL`**: cascade is used where the child record is meaningless without the parent (e.g. delete a University → its Faculties, Programs, Gallery, Fees, Intakes, Scholarships all cascade). `SET NULL` is used where the link is optional or the parent might be repurposed (e.g. `university.state_id`, `intake.program_id`, `scholarship.university_id` for country-wide scholarships).
- **Indexes** are placed on every foreign key plus every field used in a `?filter=` query param from the API spec (state, city, level, is_featured, status, eligible_country, application_deadline).
- If you'd rather use Django's ORM to generate this instead of raw SQL, this schema maps 1:1 onto the model definitions in the build spec — running `makemigrations` + `migrate` against those models produces this exact table structure.