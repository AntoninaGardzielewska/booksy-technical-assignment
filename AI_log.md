# AI Development Log — Prompt Trail
 
This file contains the full prompt history that shaped the architecture, design, and implementation of the Hardware Hub system. 

---

## Session 1 - Specification & Architecture

### Message 1.1
You have to deliver a solution focusing on these three pillars:
1. The Management Engine (Admin & Users)
● Admin Command Center: A dedicated view where the Admin can:
○ Manage Hardware: Add new items, delete old ones, and toggle the
"Repair" status.
○ Manage Accounts: Create new user accounts (this is the only way to gain
access to the system).
● Login System: A simple login screen. Only users previously created by the Admin
can access the Hub.
● Smart Dashboard: A list of hardware showing Name, Brand, Purchase Date, and
Status (Available, In Use, Repair). Must support sorting and filtering.
2. The Rental Engine (Business Logic)
● Rent/Return Flow: Users should be able to "Rent" gear (Status -> In Use) and
"Return" it.
● Core Logic: Implement guards to ensure the rental process is logical and
prevents impossible states (e.g., renting a device that isn't available).
3. The AI-Native Layer (The "Native" Part)
Integrate an LLM (Gemini, Claude, or OpenAI) to provide one of the following:
● Semantic Search: Allow users to find gear using natural language (e.g., "I need
something to test a mobile app on" → returns iPhones/Androids).
● Smart Assistant: A chat interface or automated logic that helps manage the
equipment or summarizes its history.
● Inventory Auditor: An AI-driven check that flags potential issues in the current
inventory based on all available information.
Technical Guardrails
● Stack: Python (Backend) and Vue.js (Frontend) are our preferred choices.
However, if you are significantly more productive in other programming
languages, use them. We value results and tool proficiency over specific syntax.
● Database: We suggest using a file-based database (e.g., SQLite or TinyDB) for
ease of portability and review.
● Initial Data: Start with the provided JSON seed.
● Testing: We expect at least 3 critical tests (e.g., "Cannot rent broken hardware")
generated/guided by AI.


I want you to create an initial plan for the task — the full specification. Ask me about the problems to solve, identify the current weaknesses of the proposed approach, flag what needs to be discussed, and make it as thorough as possible.

### Message 1.2
For the database layer, include handling for broken seed data:
- Duplicate IDs — the ID should be updated to the first available free value to ensure uniqueness.
- Invalid dates — should be fixed if possible; the final format should be DD-MM-YYYY. if the date is in the future log a warning but keep the data
- Wrong status values — try to normalise and map to one of three options: Available, Repair, In Use. If a record is impossible to repair, drop the row and log a warning.

Create REST API endpoints for this app. Include:
- Login
- Create user
- Add / delete hardware
- Toggle repair status
- Return hardware
- Dashboard listing with filtering, sorting, and the ability to rent hardware
- Dashboard showing the current user's rented hardware

Each endpoint that requires admin or user authentication should be protected using middleware.
Define backend test cases. Focus on business logic guards and the most critical features for a correctly working app. Also include basic unit tests.
I want to use Gemini for semantic search.
The UI should be simple and stylish — ideally inspired by the Booksy design language.


### Message 1.3
Specifically, I want to make sure the authentication flow is solid — JWT tokens with bcrypt password hashing. The admin account should be bootstrapped from environment variables (ADMIN_INITIAL_EMAIL, ADMIN_INITIAL_PASSWORD), not hardcoded in the source code. The seeder should be idempotent — it should only create the admin if no admin account already exists in the database.

### Message 1.4
One more critical business logic requirement: ensure that no two users can rent the same device at the same time. The first request wins. 


---
The initial plan after Session 1 can be found in './.github/prompts/'
---

## Session 2 - building the prototype

### Message 2.1
Build the app as specified in the plan. Make sure all specified functionalities and concerns are included. Write clean, well-structured code.
The expected structure is:
- backend/ — FastAPI application with routes/, models.py, schemas.py, security.py, dependencies.py, seeder.py
- frontend/ — Vue.js 3 with Vite, using Pinia for state and Vue Router for navigation
- tests/ — pytest test suite covering auth, rental business logic, admin features, and data seeding
- data/initial_data.json — the seed file
- .env for all secrets and configuration

### Message 2.2
Fix the styling — it should match Booksy's aesthetic. The buttons should be smaller and dark-blue. The panels are overlapping each other. Everything should follow a minimal style.

### Message 2.3 
Ensure a few more things:
- Hardware should be displayed as a list, not a card grid.
- Minimal style with a white background.
- Use #218cac as the primary styling colour for buttons and interactive elements.
- The navigation bar background should be #1b1d21.
- Use #f0f0f0 for secondary UI elements like sorting controls.
- Everything should follow a clean, minimalist approach — no unnecessary decoration.
---

## Session 3 - Admin Panel Improvements

### Message 3.1
In the admin dashboard, rework the hardware list:
Add an "Add hardware" button. The form for adding new hardware should only appear when the admin clicks the button — it should be hidden by default.
The purchase date field must not accept future dates. The placeholder should show today's date as an example.
The "Any special notes..." placeholder text should match the same greyed-out colour as the other input placeholders — right now it's noticeably darker.
Remove the colour-coded status badges (yellow/green/red). Instead, use a toggle button approach:
- If the item is in repair → show a "Finish Repair" button.
- If the item is available or in use → show a "Start Repair" button.
- Add a subtle light indicator showing whether the item is currently available or in use — similar to the existing indicator in the hardware catalogue (blue when available, grey when in repair or in use).

### Message 3.2
Add a similar "Add user" button to the admin users section — following the same pattern as the hardware add form: hidden by default, revealed on button click. The form layout should be consistent with the hardware form.

---

## Session 4 - upgrading search and filter options

### Message 4.1
Add filtering options so users can filter by status and brand. Keep the existing sort controls but make the buttons smaller — they shouldn't span the full width of the panel.
Filtering and semantic search should be combined: if both are active, first apply the filters to narrow the result set, then run the search within those filtered results.

### Message 4.2
Ensure that filtering logic is working correctly:

When multiple filters are selected, all of them must be applied simultaneously (AND logic, not OR).
If no hardware matches all active filters, return an appropriate empty-state message — do not silently fall back to a wider result set.
The order of operations must always be: filter first, then search within the filtered results.
For search: if there are semantic matches from Gemini, use them. If there are no matches from Gemini (or the query is ambiguous), fall back to keyword search as a secondary strategy.

### Message 4.3
When the user clears the search input, that should also trigger a request — treat an empty query as "no search active" and return the currently filtered results without any semantic search on top.

---

## Session 5 - deployment and documentation

### Message 5.1
Update the documentation to reflect all changes made across the sessions. The README should include:
Setup instructions for both backend and frontend
A full list of API endpoints
A description of the data cleaning logic (duplicate IDs, invalid dates, status normalisation, dropped rows with logging)
A clear implementation status section covering: fully implemented features, shortcuts and trade-offs with justification, partial or missing features, and a 24-hour roadmap
The AI Development Log section: tooling used, data strategy, prompt trail reference, and the correction moment

### Message 5.2
The Scope (The Perfect Core)
You have to deliver a solution focusing on these three pillars:
1. The Management Engine (Admin & Users)
● Admin Command Center: A dedicated view where the Admin can:
○ Manage Hardware: Add new items, delete old ones, and toggle the
"Repair" status.
○ Manage Accounts: Create new user accounts (this is the only way to gain
access to the system).
● Login System: A simple login screen. Only users previously created by the Admin
can access the Hub.
● Smart Dashboard: A list of hardware showing Name, Brand, Purchase Date, and
Status (Available, In Use, Repair). Must support sorting and filtering.
2. The Rental Engine (Business Logic)
● Rent/Return Flow: Users should be able to "Rent" gear (Status -> In Use) and
"Return" it.
● Core Logic: Implement guards to ensure the rental process is logical and
prevents impossible states (e.g., renting a device that isn't available).
3. The AI-Native Layer (The "Native" Part)
Integrate an LLM (Gemini, Claude, or OpenAI) to provide one of the following:
● Semantic Search: Allow users to find gear using natural language (e.g., "I need
something to test a mobile app on" → returns iPhones/Androids).
● Smart Assistant: A chat interface or automated logic that helps manage the
equipment or summarizes its history.
● Inventory Auditor: An AI-driven check that flags potential issues in the current
inventory based on all available information.
CONFIDENTIAL: Unauthorized sharing, reproduction, or distribution of this material is strictly prohibited.
None
💾 The Data & Stack
Initial Dataset (Seed)
Use this as your starting point. You can store it in a simple file-based database like
SQLite or TinyDB.
JSON
[
{ "id": 1, "name": "Apple iPhone 13 Pro Max", "brand": "Apple",
"purchaseDate": "2021-11-23", "status": "Available" },
{ "id": 2, "name": "Apple MacBook Pro 13", "brand": "Apple",
"purchaseDate": "2021-12-20", "status": "In Use" },
{ "id": 3, "name": "Razer Basilisk V2", "brand": "Razer",
"purchaseDate": "2021-06-05", "status": "Repair" },
{ "id": 4, "name": "SAMSUNG Galaxy S21", "brand": "Samsung",
"purchaseDate": "2021-11-23", "status": "Available" },
{ "id": 5, "name": "Dell XPS 15 9510", "brand": "Dell",
"purchaseDate": "2022-03-15", "status": "Available", "notes":
"Battery swelling, do not issue without service." },
{ "id": 6, "name": "Logitech MX Master 3", "brand": "Logitech",
"purchaseDate": "2027-10-10", "status": "Available" },
{ "id": 7, "name": "Sony WH-1000XM4", "brand": "Sony",
"purchaseDate": "2022-01-12", "status": "In Use", "assignedTo":
"j.doe@booksy.com" },
{ "id": 4, "name": "Duplicate ID Test Laptop", "brand": "Lenovo",
"purchaseDate": "2023-01-01", "status": "Repair" },
CONFIDENTIAL: Unauthorized sharing, reproduction, or distribution of this material is strictly prohibited.
{ "id": 9, "name": "iPad Pro 12.9", "brand": "Appel",
"purchaseDate": "22-05-2023", "status": "Available" },
{ "id": 10, "name": "Unknown Device", "brand": "",
"purchaseDate": null, "status": "Unknown" },
{ "id": 11, "name": "MacBook Air M2", "brand": "Apple",
"purchaseDate": "2023-08-01", "status": "Available", "history":
"Returned by user with liquid damage. Keyboard sticky." }
]
💻 Technical Guardrails
● Stack: Python (Backend) and Vue.js (Frontend) are our preferred choices.
However, if you are significantly more productive in other programming
languages, use them. We value results and tool proficiency over specific syntax.
● Database: We suggest using a file-based database (e.g., SQLite or TinyDB) for
ease of portability and review.
● Initial Data: Start with the provided JSON seed.
● Wireframes inspiration: link - We suggest using this only as inspiration on how
the system should look, feel free to remodel it, but please attach justifications. If
the link is not working for you, please try this one.
● Testing: We expect at least 3 critical tests (e.g., "Cannot rent broken hardware")
generated/guided by AI.
CONFIDENTIAL: Unauthorized sharing, reproduction, or distribution of this material is strictly prohibited.
💡 Process Over Perfection
(The
"Engineering Mindset")
At Booksy, we value transparency and the "builder's journey." In an AI-augmented world,
code is cheap, but engineering decisions are expensive. We prefer a rock-solid core
and a clear vision over a buggy, rushed application.
Honesty is a feature. If you have to cut corners or use a "hacky" solution to meet the
deadline, don't hide it. Show us that you are aware of it - document it.
1. Implementation Status & Trade-offs
In your README.md, provide a clear summary of your progress:
● ✅ Fully Implemented: Features that are stable and production-ready.
● ⚡ Shortcuts & "Hacks": What did you build quickly just to make it work?
○ Example: "I used local storage for sessions instead of a proper JWT flow to
save time."
○ The "Why": Why was this shortcut acceptable for this MVP?
○ The "Future": How would you refactor this in a real production
environment?
● ⚠️ Partial/Missing: What started but didn't make the cut?
● 🔮 Next Steps (The 24h Roadmap): If you had one more day, what would be your
top 3 priorities to fix or improve?
2. The AI Development Log (Required)
We want to see your synergy with AI tools. Please include:
● Tooling: Which tools did you use? (e.g., Cursor, Gemini, Claude Dev).
● Data Strategy: Describe how you handled the initial dataset. Did the AI help you
identify any challenges during the integration? (We are looking for your ability to
audit AI-generated data migrations).
● Prompt Trail: Provide a link (or a markdown file) with the prompts history that
shaped the architecture of the system and design.
CONFIDENTIAL: Unauthorized sharing, reproduction, or distribution of this material is strictly prohibited.
● The "Correction": Describe at least one specific moment where the AI gave you a
suboptimal, buggy, or insecure solution. How did you identify the error and how
did you guide the AI (or manually fix it) to match your vision?
📝 Submission Requirements
1. Repository: Link to a public GitHub/GitLab repo with a clean commit history.
a. Pro-tip: A clean commit history showing the incremental "collaboration"
with AI is much better than one giant "initial commit."
2. Documentation: A comprehensive README.md with setup instructions and your
AI Log.
3. Deployment: A live demo link (Vercel, Railway,Fly.io etc.) is a huge plus! ⚡
4. Timeline: The preparation of this assignment should take you about 4-5 hours.
Please share the results of your work at least 48 hours before your interview by
responding to this email.
5. Results: Please be prepared to walk through your assignment results in detail
during the final interview. We will dive deep into your documentation and your
decision-making process.


Finalise the README based on the full scope of what was delivered. Here is the original requirements document for reference — use it to make sure nothing is omitted.
The implementation status section should be honest and specific:
Fully implemented:

Admin Command Center with add/delete hardware and add user forms (hidden by default, revealed on click)
JWT authentication with bcrypt, inactive user blocking
Smart Dashboard with sorting, filtering (multi-filter AND logic), and combined semantic + keyword search
Rental engine with business logic guards — cannot rent unavailable or repair items; concurrent rental prevention (first-come-first-served)
Per-user rental history
Gemini semantic search with keyword fallback when no API key is present or the query is cleared
Data seeder with cleaning: duplicate IDs, malformed dates, status normalisation, dropped rows with logging
15+ tests covering auth, business logic, admin features, and seeder edge cases

Shortcuts and trade-offs:

Invalid seed data is dropped and logged rather than quarantined — acceptable for MVP, but in production should route to a data quarantine table or a manual review UI.
Admin credentials come from .env rather than a first-run setup wizard — better than hardcoding, but production should use a secrets manager.
Future-dated hardware (the Logitech MX Master 3 with a 2027 purchase date) passes through the seeder unchecked — the date validator only checks parseability, not whether the date is in the future.
No edit endpoints for users or hardware — add/delete/toggle-repair only.

Partial / missing:

No ability to deactivate, edit, or delete users from the UI.
Hardware cannot be edited through the UI.
No Docker setup — the app must be run manually in two terminals.

24-hour roadmap:

Seeder improvements: future-date detection, data quarantine flow, admin UI for reviewing import warnings.
Docker Compose setup for one-command startup.
Full PATCH endpoints for users and hardware with corresponding admin UI forms.


The Correction: The AI initially bootstrapped the admin account by hardcoding credentials directly in the seeder (admin@booksy.com / admin123). This is a classic security anti-pattern — hardcoded credentials end up in version control and are easy to miss in a review. I caught this and redirected: credentials should come from environment variables, and the seeder should only run if no admin already exists (making it idempotent). The AI implemented the fix cleanly once I stated the requirement explicitly.

---

## Session X - Hand-fixing with AI
While the AI wrote the bulk of the code, I had to manually intervene and "chat" my way through some specific bugs using gemini. Here is a look at that:

1. CORS problem: The app worked locally but died on Railway/Vercel
Prompt:
My CORS config is failing in production. I think pydantic-settings is reading the string from the env file literally. Help me write a validator or a .split(',') logic in config.py so it handles both local comma-separated strings and proper lists.

2. The seeder was flipping months and days.
Prompt:
The seeder is turning 05-12-2023 into May 12th, but it should be Dec 5th. Ensure that the seeder tries a few options, but tries them in the dd-mm-yyy or yyyy-mm-dd format to aviod date confusion

3. the brand filter was only implemented in frontend logic, and it shown a list only from the currently filtered options
Prompt:
Right now the brand filter is only filtering the local Vue state. If I select 'Apple', it only shows brands of the filtered options, this should be fixed to always show all of the possible 'brand' options. Additionally I need to implement filtering in the backend - right now frontend only sends in the body brand_filter but backend does not use it. Update the GET /hardware endpoint to accept brand and status as optional query params and return the filtered list from the DB

4. Also there were several problems when the code was not running at all or there were small bugs - I usually tried to see if it's an easy fix and fix it manually (for example by adding new dependencies), If it looked more time-consuming, I'd ask the chat about the possible source of error.