# VolunteerHub Project Plan

**Last updated:** August 15, 2026

## Goal

Turn VolunteerHub from a working prototype into a dependable platform that real
organizations can use to run volunteer programs.

The finished product should help organizations recruit volunteers, schedule
shift-based events, confirm that volunteers meet requirements, record actual
attendance, verify service hours, and communicate with participants.

## Guiding principles

- Build for real organizations and real volunteer workflows.
- Keep every organization's information separate and secure.
- Make common tasks simple on both phones and computers.
- Improve the product from user feedback, not guesses alone.
- Keep a clear record of releases, decisions, fixes, and independently added
  work.
- Add complexity only when it solves a real user problem.

## Phase 1: Establish a clean starting point

- Save or tag the original prototype as the first version.
- Record which features already exist and which parts need to be replaced.
- Add automated tests around the most important existing behavior.
- Set up a changelog, issue templates, and a simple release process.
- Rewrite old classroom wording around the real roles of volunteer,
  coordinator, and organization administrator.

**Done when:** The original version can still be identified, the current
application is documented, and future changes can be traced clearly.

## Phase 2: Add organizations and secure access

- Add organizations and organization profiles.
- Let users belong to more than one organization.
- Give each membership a role, such as volunteer, coordinator, or administrator.
- Place events, shifts, certificates, hours, and reports under an organization.
- Check permissions on every page and API action.
- Add tests that prove one organization cannot view or change another
  organization's information.

**Done when:** Two organizations can use the same deployment without seeing or
changing each other's private data.

## Phase 3: Build complete scheduling workflows

- Let coordinators create events with roles and time-based shifts.
- Add shift capacity, registration deadlines, cancellations, and waitlists.
- Detect overlapping shifts for volunteers.
- Add age and certification requirements where needed.
- Explain clearly why a volunteer cannot join a shift.
- Notify the next person when a waitlist space becomes available.

**Done when:** A coordinator can publish an event and volunteers can register
for suitable shifts without manual spreadsheet work.

## Phase 4: Connect certificates to eligibility

- Store the certificate type, issue date, expiry date, document, and review
  status.
- Record who reviewed a certificate and when it was reviewed.
- Show whether a volunteer is eligible, missing a requirement, expired, or
  waiting for review.
- Warn volunteers before a certificate expires.

**Done when:** VolunteerHub can automatically decide whether a volunteer meets
an event's stated requirements while allowing an authorized person to review
supporting documents.

## Phase 5: Record attendance and verified hours

- Create secure, short-lived QR check-in and check-out codes.
- Support a manual attendance option when a phone or camera is unavailable.
- Keep scheduled hours, attended hours, and verified hours separate.
- Let coordinators correct and approve attendance with a recorded reason.
- Prevent repeated scans and invalid attendance changes.

**Done when:** Attendance at a real event can produce accurate volunteer-hour
records that a coordinator can review and verify.

## Phase 6: Add communication and calendar tools

- Send confirmation after registration.
- Send a reminder before a shift.
- Notify coordinators about important cancellations and attendance issues.
- Notify volunteers when a waitlist place opens.
- Provide calendar files that work with Google Calendar, Apple Calendar, and
  Outlook.
- Let users control which optional messages they receive.

**Done when:** Volunteers can keep track of their commitments without relying on
coordinators to send every message by hand.

## Phase 7: Add accountability and reporting

- Record important actions such as certificate reviews, capacity changes,
  cancellations, attendance edits, and hour approvals.
- Show a readable history to authorized users.
- Add coordinator reports for attendance, hours, open shifts, and expiring
  certificates.
- Allow organizations to export their own records.

**Done when:** An organization can understand what happened, who changed it, and
how its volunteer program is performing.

## Phase 8: Prepare for production use

- Move production data to PostgreSQL.
- Set up safe configuration, HTTPS, backups, logging, error reporting, and
  health checks.
- Test accessibility and the main workflows on mobile devices.
- Write short guides for volunteers, coordinators, and administrators.
- Create a process for reporting bugs and responding to production problems.

**Done when:** A small organization can use the hosted application safely and
there is a clear way to recover from mistakes or failures.

## Phase 9: Pilot with real users

- Find one organization willing to try VolunteerHub.
- Interview coordinators and volunteers before the pilot.
- Turn their problems into written requirements and user stories.
- Run a small number of real events through the platform.
- Track only honest results, such as active users, events, registrations,
  attendance records, verified hours, and support issues.
- Review feedback after each release and adjust priorities.

**Done when:** Real users have completed the main workflow and their feedback has
led to at least one measured product improvement.

## Quality checks for every phase

Before a phase is released:

- Important behavior has automated tests.
- Permissions and organization separation have been checked.
- Error messages tell users what happened and what to do next.
- The workflow works on a phone and with keyboard navigation.
- Database changes have safe migrations.
- User-facing changes are added to the changelog.
- Documentation reflects what the product actually does.

## Work that is intentionally out of scope

VolunteerHub will not add machine learning recommendations, chatbots,
microservices, Kafka, Kubernetes, or a React rewrite unless real user needs make
one of them necessary. The focus is a reliable product, not a longer technology
list.

## Success measures

Early success means one organization can use VolunteerHub for real events with
less manual coordination. Useful measures include:

- Organizations actively using the product
- Coordinators and volunteers who complete a workflow
- Events and shift registrations managed
- Attendance records and verified hours created
- Scheduling conflicts or missing requirements caught
- Support issues resolved and improvements shipped from feedback

Targets will be set after speaking with the first pilot organization. Results
will only be published after they have actually been achieved.
