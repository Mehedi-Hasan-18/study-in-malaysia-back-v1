# Frontend API Guide

For Next.js + JavaScript frontend.

## Base Setup

Set API base URL in `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=https://your-backend.vercel.app/api/v1
```

Use one shared API helper:

```js
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;

export async function apiFetch(path, options = {}) {
  const token = options.token;
  const headers = {
    ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
    body:
      options.body instanceof FormData || typeof options.body === "string"
        ? options.body
        : options.body
          ? JSON.stringify(options.body)
          : undefined,
  });

  const data = res.status === 204 ? null : await res.json();
  if (!res.ok) throw data;
  return data;
}
```

Paginated list shape:

```json
{
  "data": [],
  "meta": {
    "count": 100,
    "next": "https://...",
    "previous": null
  }
}
```

Most detail/create responses:

```json
{ "data": {} }
```

Common query params:

```text
?page=2
?search=keyword
?ordering=name
?ordering=-created_at
```

Auth header for protected endpoints:

```js
Authorization: `Bearer ${firebaseIdToken}`
```

## Auth + Profile

### Firebase Login

`POST /auth/firebase-login/`

Body:

```json
{ "id_token": "firebase-id-token" }
```

Returns:

```json
{
  "data": {
    "user": {
      "id": 1,
      "firebase_uid": "...",
      "email": "user@email.com",
      "full_name": "User Name",
      "date_joined": "2026-07-20T..."
    },
    "profile": {
      "id": 1,
      "user": 1,
      "phone": "",
      "country": null,
      "country_detail": null,
      "photo_public_id": "",
      "photo_url": ""
    }
  }
}
```

Next.js:

```js
await apiFetch("/auth/firebase-login/", {
  method: "POST",
  body: { id_token: firebaseIdToken },
});
```

### Current User

`GET /auth/me/` protected

Returns same user + profile shape.

### Logout

`POST /auth/logout/` protected

Frontend should also clear Firebase client state.

### Profile

`GET /profile/` protected

`PUT /profile/` protected

Writable fields:

```json
{
  "phone": "+880...",
  "country": 1
}
```

Read-only fields:

```text
id, user, country_detail, photo_public_id, photo_url
```

### Profile Photo Upload

`POST /profile/photo/` protected, multipart

Field:

```text
photo: File
```

Next.js:

```js
const formData = new FormData();
formData.append("photo", file);

await apiFetch("/profile/photo/", {
  method: "POST",
  token,
  body: formData,
});
```

## Locations

### Countries

`GET /countries/`

Fields:

```text
id, name, code
```

Search/order:

```text
?search=malaysia
?ordering=name
```

### States

`GET /states/`

Fields:

```text
id, country, name
```

Filters:

```text
?country=1
```

### Cities

`GET /cities/`

Fields:

```text
id, state, name
```

Filters:

```text
?state=1
?state__country=1
```

## Universities

### List Universities

`GET /universities/`

Fields:

```text
id
name
slug
short_description
full_description
university_type: public | private
state
state_detail: { id, country, name }
city
city_detail: { id, state, name }
ranking_tier
is_featured
logo_public_id
logo_url
cover_public_id
cover_url
website
contact_email
contact_phone
established_year
total_students
gallery: Gallery[]
```

Filters/search/order:

```text
?search=monash
?ordering=name
?ordering=-total_students
```

Common frontend fields:

```js
university.name
university.logo_url
university.cover_url
university.state_detail?.name
university.city_detail?.name
university.gallery
```

### University Detail

`GET /universities/{id}/`

### Create/Update University

`POST /universities/` staff

`PATCH /universities/{id}/` staff

Use multipart when uploading logo/cover.

Writable fields:

```text
name
slug
short_description
full_description
university_type
state
city
ranking_tier
is_featured
logo: File
cover: File
website
contact_email
contact_phone
established_year
total_students
```

Numbers accept comma:

```text
10,000
10,000.50
```

Upload example:

```js
const formData = new FormData();
formData.append("name", "Asia Pacific University");
formData.append("slug", "asia-pacific-university");
formData.append("university_type", "private");
formData.append("logo", logoFile);
formData.append("cover", coverFile);

await apiFetch("/universities/", {
  method: "POST",
  token,
  body: formData,
});
```

### University Child Data

```text
GET /universities/{id}/faculties/
GET /universities/{id}/programs/
GET /universities/{id}/gallery/
GET /universities/{id}/intakes/
GET /universities/{id}/fees/
GET /universities/{id}/scholarships/
```

### Gallery

Gallery fields:

```text
id
university
image_public_id
image_url
caption
display_order
```

Upload multiple photos:

`POST /universities/{id}/gallery/` staff, multipart

Fields:

```text
images[]: File
display_order: optional number
caption: optional string
```

Next.js:

```js
const formData = new FormData();
files.forEach((file) => formData.append("images[]", file));
formData.append("display_order", "1");

await apiFetch(`/universities/${universityId}/gallery/`, {
  method: "POST",
  token,
  body: formData,
});
```

Returns:

```json
{ "data": [{ "id": 1, "image_url": "...", "display_order": "1.00" }] }
```

`display_order` controls gallery sorting. Lower number shows first.

## Faculties

`GET /faculties/`

Fields:

```text
id
university
name
description
```

Filters/search/order:

```text
?university=1
?search=engineering
?ordering=name
```

## Programs

`GET /programs/`

Fields:

```text
id
faculty
university
name
slug
level: diploma | bachelor | master | phd
duration_months
language
description
tuition_fee_display
requirements: ProgramRequirement[]
```

Requirement fields:

```text
id
program
requirement_type
description
```

Filters/search/order:

```text
?search=computer
?ordering=name
?ordering=-tuition_fee_display
```

Child endpoints:

```text
GET /programs/{id}/requirements/
GET /programs/{id}/fees/
```

## Intakes

`GET /intakes/`

Fields:

```text
id
university
program
name
start_date
```

Filters/search/order:

```text
?university=1
?program=2
?search=january
?ordering=start_date
```

`start_date` optional.

## Tuition Fees

`GET /fees/`

Fields:

```text
id
program
university
tuition_amount
registration_fee
misc_fee
currency
bdt_equivalent
academic_year
pdf_public_id
pdf_url
```

Filters/search/order:

```text
?university=1
?program=2
?currency=MYR
?academic_year=2026
?ordering=tuition_amount
```

Download PDF:

```text
GET /fees/{id}/download/
```

This redirects to `pdf_url`.

## Scholarships

`GET /scholarships/`

Fields:

```text
id
name
slug
description
university
coverage_percentage
eligible_level: string[]
eligible_country
application_deadline
brochure_public_id
brochure_url
```

Eligible level values:

```text
foundation
diploma
bachelor
masters
```

Filters/search/order:

```text
?country=Bangladesh
?coverage=50
?level=bachelor
?university=1
?deadline_before=2026-12-31
?search=merit
?ordering=application_deadline
```

Create/update with brochure upload:

```js
const formData = new FormData();
formData.append("name", "Merit Scholarship");
formData.append("slug", "merit-scholarship");
formData.append("coverage_percentage", "50");
formData.append("eligible_country", "Bangladesh");
formData.append("application_deadline", "2026-12-31");
formData.append("brochure", file);
formData.append("eligible_level", JSON.stringify(["foundation", "bachelor"]));
```

For JSON create/update without file:

```json
{
  "name": "Merit Scholarship",
  "slug": "merit-scholarship",
  "coverage_percentage": "50",
  "eligible_level": ["foundation", "bachelor"],
  "eligible_country": "Bangladesh",
  "application_deadline": null
}
```

Student actions:

```text
POST /scholarships/{id}/save/      protected
DELETE /scholarships/{id}/save/    protected
POST /scholarships/{id}/apply/     protected
GET /my-scholarships/              protected
```

## Applications

Protected endpoints. User sees only own applications.

`GET /applications/`

`POST /applications/`

Create body:

```json
{
  "program": 1,
  "intake": 2
}
```

Fields:

```text
id
user
program
intake
status
submitted_at
created_at
updated_at
```

Status values:

```text
draft
submitted
under_review
more_docs_needed
approved
rejected
```

Actions:

```text
POST /applications/{id}/submit/
GET /applications/{id}/status/
GET /applications/history/
GET /applications/{id}/documents/
POST /applications/{id}/documents/
```

Upload document:

```js
const formData = new FormData();
formData.append("document_type", "passport");
formData.append("resource_type", "raw");
formData.append("file", file);

await apiFetch(`/applications/${applicationId}/documents/`, {
  method: "POST",
  token,
  body: formData,
});
```

Document types:

```text
passport
transcript
certificate
english_test
personal_statement
resume
other
```

Resource types:

```text
raw
image
```

## Documents

`GET /documents/` protected

`GET /documents/{id}/` protected

`DELETE /documents/{id}/` protected

Fields:

```text
id
application
document_type
file_public_id
file_url
resource_type
uploaded_at
```

## Wishlist

### University Wishlist

`GET /wishlist/universities/` protected

`POST /wishlist/universities/` protected

Body:

```json
{ "university": 1 }
```

`DELETE /wishlist/universities/{id}/` protected

Fields:

```text
id
user
university
university_detail
created_at
```

### Scholarship Wishlist

`GET /wishlist/scholarships/` protected

`POST /wishlist/scholarships/` protected

Body:

```json
{ "scholarship": 1 }
```

`DELETE /wishlist/scholarships/{id}/` protected

Fields:

```text
id
user
scholarship
scholarship_detail
created_at
```

## Dashboard

Protected endpoints:

```text
GET /dashboard/
GET /dashboard/recent-applications/
GET /dashboard/statistics/
GET /dashboard/profile-completion/
```

Dashboard response:

```json
{
  "data": {
    "statistics": {
      "total_applications": 1,
      "submitted_applications": 1,
      "approved_applications": 0
    },
    "profile_completion": {
      "completed_fields": 4,
      "total_fields": 5,
      "percentage": 80,
      "fields": {
        "full_name": true,
        "email": true,
        "phone": true,
        "country": true,
        "photo": false
      }
    }
  }
}
```

## Notifications

`GET /notifications/` protected

`PUT /notifications/{id}/` protected

`DELETE /notifications/{id}/` protected

`PUT /notifications/{id}/read/` protected

Fields:

```text
id
user
message
is_read
created_at
```

## News, Blogs, FAQ, Contact

### News

`GET /news/`

Fields:

```text
id
title
slug
body
cover_public_id
cover_url
published_at
```

Search/order:

```text
?search=visa
?ordering=-published_at
```

### Blogs

`GET /blogs/`

Fields:

```text
id
title
slug
body
cover_public_id
cover_url
author
tags
published_at
```

### FAQ

`GET /faq/`

Fields:

```text
id
question
answer
category
display_order
```

Filters/search/order:

```text
?category=admission
?search=visa
?ordering=display_order
```

### Contact

`POST /contact/`

Body:

```json
{
  "name": "Student",
  "email": "student@email.com",
  "message": "I need help."
}
```

Also available:

```text
POST /inquiry/
```

## Upload Rules

Never send URL paste fields for upload. Send file directly with `FormData`.

Do not manually set `Content-Type` for `FormData`. Browser adds boundary.

Upload fields:

```text
profile photo: photo
university logo: logo
university cover: cover
gallery photos: images[]
scholarship brochure: brochure
application document: file
news/blog cover: cover
```

Stored URL fields are read-only:

```text
photo_url
logo_url
cover_url
image_url
brochure_url
file_url
pdf_url
```

Use those URL fields for displaying images/files.

## Next.js Page Examples

### University List

```js
import { apiFetch } from "@/lib/api";

export default async function UniversitiesPage() {
  const { data, meta } = await apiFetch("/universities/?ordering=name");

  return (
    <main>
      {data.map((university) => (
        <article key={university.id}>
          <img src={university.logo_url} alt={university.name} />
          <h2>{university.name}</h2>
          <p>{university.city_detail?.name}</p>
        </article>
      ))}
    </main>
  );
}
```

### Protected Client Call

```js
import { getAuth } from "firebase/auth";
import { apiFetch } from "@/lib/api";

export async function loadProfile() {
  const user = getAuth().currentUser;
  const token = await user.getIdToken();
  return apiFetch("/profile/", { token });
}
```

### Application Create

```js
await apiFetch("/applications/", {
  method: "POST",
  token,
  body: {
    program: programId,
    intake: intakeId || null,
  },
});
```

### Multiple Gallery Upload

```js
async function uploadGallery(universityId, files, token) {
  const formData = new FormData();
  Array.from(files).forEach((file) => formData.append("images[]", file));

  return apiFetch(`/universities/${universityId}/gallery/`, {
    method: "POST",
    token,
    body: formData,
  });
}
```

## Frontend Field Map

Use these display fields most:

```text
University card: name, logo_url, cover_url, short_description, city_detail.name, state_detail.name
University detail: full_description, website, contact_email, contact_phone, gallery
Program card: name, level, duration_months, tuition_fee_display
Tuition: tuition_amount, registration_fee, misc_fee, bdt_equivalent, currency, academic_year
Scholarship card: name, coverage_percentage, eligible_level, eligible_country, application_deadline
Application card: program, intake, status, submitted_at, updated_at
Document link: file_url, document_type, uploaded_at
News/blog card: title, slug, cover_url, published_at
FAQ list: question, answer, category
```
