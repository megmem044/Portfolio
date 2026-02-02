# Final Product – VolunteerHub

**Course:** CMPT 370  
**Team:** Team 9  
**Project Name:** VolunteerHub – Volunteer Tracking & Matching System  
**Repository:** https://git.cs.usask.ca/adr480/cmpt370-team9

---

## 1. Final Product Overview

VolunteerHub is a web-based volunteer management system designed to streamline the process of recruiting, managing, and participating in volunteer opportunities. The system supports multiple user personas, including coordinators and volunteers, each with distinct needs. By centralizing volunteer postings, event management, enrollment, tracking, and personalized discovery, VolunteerHub reduces manual coordination effort and improves accessibility and usability for all users.

The final product fully implements the epics and user stories proposed in earlier deliverables and demonstrates all functionality live at runtime in the final demo video.

---

## 2. Implemented Epics & User Stories (Final Product)

### Epic: StressedSally – Volunteer Recruitment & Posting (Katelyn)
- Create volunteer recruitment posts
- Edit and delete existing posts
- Display posts immediately to all volunteers
- **Status:** Completed

### Epic: PlannerPaco – Event, Role, and Volunteer Management (Meghal)

**User Story 1:** Post detailed events with volunteer roles and shifts
- Create event announcements with title and description
- Add multiple volunteer roles to a single event (e.g., Greeter, Setup Crew)
- Define shift times (start/end times) for each role
- Display real-time list of volunteer names under each role
- Automatically update volunteer list when volunteers sign up or cancel
- Edit events after creation (description, date, roles)
- Delete events from the system
- Acceptance Criteria: Real-time volunteer signup display, automatic updates on cancellation

**User Story 2:** Track volunteer hours, contact info, and certifications
- View volunteer profiles with contact information
- Automatically calculate total hours worked from shift durations
- Support PDF certificate uploads with optional remarks
- Verify and reject uploaded certificates with status tracking
- Display certificate verification status (Verified, Rejected, Pending)
- Restrict verification buttons to admin/coordinator view only
- Handle multiple certificate uploads per volunteer
- Gracefully display empty state for volunteers without certificates
- Acceptance Criteria: Auto-calculated hours match actual enrollments, certificate status updates correctly, file type validation

**Status:** Completed (20/20 test cases passing)

### Epic: JudoArtist – Volunteer Progress & Portfolio (Justin)
- View assigned volunteer projects
- Track project status (Upcoming, Ongoing, Completed)
- Update project status dynamically
- Upload artwork and portfolio images
- Display portfolio gallery in chronological order
- **Status:** Completed

### Epic: EmiExplorer – Personalized Volunteer Discovery (Jessie)
- Set English comfort level preferences
- Select cultural interest tags
- Save user preferences
- View volunteer opportunities aligned with preferences
- Sign up for volunteer shifts through a simplified interface
- **Status:** Completed

---

## 3. Architecture of the Final Web Application

VolunteerHub follows a client-server architecture:

- **Frontend:** HTML/CSS/JavaScript templates providing role-specific interfaces for volunteers and coordinators
- **Backend:** Django with Django REST Framework managing business logic, filtering, and data processing
- **Database:** Relational database storing users, roles, events, enrollments, preferences, and certificates
- **APIs:** REST endpoints supporting posts, events, enrollments, filtering, and preference management

The architecture supports real-time updates, automatic calculations, and modular feature development.

---

## 4. Quality Assurance Strategy

Quality assurance for the final product was conducted using a combination of:

- Acceptance testing based on user stories defined in Deliverable 1
- Manual testing by acting as real users and coordinators
- Runtime verification during live demonstrations

Each user story includes acceptance criteria that were tested and verified in the final product. Test results are documented in supporting materials.

---

## 5. Acceptance Test Results (Final Product)

Team members tested user stories implemented by other teammates, not their own.

### PlannerPaco – Event Management (User Story 1) - 10/10 Tests Passing

| Test Case | Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC01 | Create new event post | Event appears on events list | Event displayed correctly | Pass |
| TC02 | Create event with empty form | Validation error shown | Validation error displayed | Pass |
| TC03 | Add multiple roles to event | Roles appear under assigned event | Multiple roles displayed | Pass |
| TC04 | Save shift times for roles | Times display correctly on event card | Times saved and displayed | Pass |
| TC05 | Real-time volunteer signup | New volunteer appears immediately | Name added under correct role | Pass |
| TC06 | Volunteer cancellation updates | Volunteer removed from role list | Volunteer disappears on refresh | Pass |
| TC07 | Multiple volunteers per role | All volunteers appear under same role | Three volunteers all displayed | Pass |
| TC08 | Long event description | Display correctly without breaking layout | 1000+ characters display properly | Pass |
| TC09 | Edit event after creation | Changes shown on event page | Description, date, roles all editable | Pass |
| TC10 | Delete event | Event removed from listings | Event no longer visible | Pass |

### PlannerPaco – Volunteer Hours & Certificates (User Story 2) - 10/10 Tests Passing

| Test Case | Description | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| TC01 | View volunteer profile | Summary card shows contact info + total hours | Profile displays correctly | Pass |
| TC02 | Calculate total hours | Hour totals match sum of enrollments | Calculation accurate | Pass |
| TC03 | Upload certificate | Certificate card appears below form | PDF upload successful | Pass |
| TC04 | Reject unsupported file types | Error message shown | .exe and .zip rejected | Pass |
| TC05 | Admin-only verification buttons | Volunteer view has no buttons, admin view has buttons | Permission handling correct | Pass |
| TC06 | Verify certificate | Status updates to Verified | Status changed correctly | Pass |
| TC07 | Reject certificate | Status updates to Rejected | Status changed correctly | Pass |
| TC08 | View uploaded file | PDF opens in new tab | File opens successfully | Pass |
| TC09 | Empty certificate list | Shows "No certificates uploaded yet" gracefully | Empty state displayed | Pass |
| TC10 | Upload with remarks | Upload succeeds and remarks stored | Optional remarks field works | Pass |

### Other Personas (Summary)

| User Story | Acceptance Test | Expected Result | Actual Result | Pass/Fail |
|---|---|---|---|---|
| StressedSally – Create Post | Submit new post | Post appears immediately | Post displayed correctly | Pass |
| JudoArtist – Portfolio Upload | Upload image | Image shown in gallery | Image displayed | Pass |
| EmiExplorer – Preferences | Save language & interests | Filtered opportunities shown | Correct results displayed | Pass |

All test cases passed. Full documentation available in supporting materials.

---

## 6. Product Installation & Usage (Summary)

### Prerequisites
- Python
- Django
- Required packages listed in requirements.txt

### Installation Steps
1. Clone the GitLab repository
2. Install dependencies
3. Run database migrations
4. Start the development server
5. Access the application via browser

Detailed installation instructions are provided in the README documentation.

---

## 7. Demo Video

**Demo Video Submission:** Canvas Assignment

The demo video includes:
- Product installation walkthrough
- Live runtime demonstration of all features
- Each team member introducing themselves and presenting their own implemented user stories
- No code walkthroughs, only functional demonstrations

---

## 8. Contributions & Next Steps

| Team Member | Contribution | Percentage |
|---|---|---|
| Katelyn | Volunteer post creation, editing, deletion (StressedSally) | 25% |
| Meghal | Event creation, role management, hour tracking, certificate verification (PlannerPaco) | 25% |
| Justin | Volunteer project tracking and portfolio gallery (JudoArtist) | 25% |
| Jessie | Preference system, personalized filtering (EmiExplorer) | 25% |

### Next Steps (If Continued)
- Improve recommendation logic
- Enhance UI/UX accessibility
- Add analytics dashboards
- Expand automated testing coverage

---

## 9. GenAI Statement

Generative AI tools were used to assist with drafting documentation, clarifying requirements, and refining presentation materials. All implementation decisions and final code were developed, reviewed, and validated by the team.

**Katelyn:** Generative AI tools were used to assist with drafting documentation, clarifying requirements, and refining presentation materials. All implementation decisions and final code were developed, reviewed, and validated by the team.

**Meghal:** Generative AI tools were used to assist with drafting documentation, clarifying requirements, and refining presentation materials. All implementation decisions and final code were developed, reviewed, and validated by the team.

**Justin:** Generative AI tools were used to assist with drafting documentation, clarifying requirements, and refining presentation materials. All implementation decisions and final code were developed, reviewed, and validated by the team.

**Jessie:** Generative AI tools were used to assist with drafting documentation, clarifying requirements, and refining presentation materials. All implementation decisions and final code were developed, reviewed, and validated by the team.

---

## 10. Appendix

- Screenshots
- Additional test data
- API endpoint documentation