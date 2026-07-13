#          PLACEMENT-PORTAL-APP-V2

# PROJECT STATEMENT:
Institutes require efficient systems to manage campus recruitment activities involving companies and students. Currently, many institutes rely on spreadsheets, emails, or manual coordination, which makes it difficult to manage company approvals, placement drives, student registrations, and application tracking.

# FRAMEWORK USED:
This is a Placement Portal App V2 made by using Flask for API, VueJS for UI ,Bootstrap for HTML generation and styling ,SQLite for database ,Redis for caching,Redis and Celery for batch jobs.

# FEATURES:
* User(Students and Companies) registration and authentication using Flask Security. Admin don't required registration.
* Students edit their profile,view the companies whose registration is approved and also view the approved drives of these approved companies, view the applied drive and their status and also see the application history and their status.
* After registration approved by admin,company edit their profile ,create drives ,and sees the application for the drive and also see the profile of students and update their application status.
* Admin view the company registeration and their drives and approved their registration and drives and also view the students details and their application,and also blacklist students and companies,etc.

# MILESTONES(COMPLETED):
1.Database Models and Schema Setup (Flask)
2.Authentication and Role-Based Access (Admin/Company/ Student) (Flask+Vue)
3.Admin Dashboard and Management (Flask+Vue)
4.Company Dashboard and Job/Application Management (Flask+Vue)
5.Student Dashboard and Job Application System (Flask+Vue)
6.Job Application History and Status Tracking (Flask+Vue)
7.Backend Jobs – Interview Reminders, Placement Reports, and Triggered Jobs (CSV Export using Celery + Redis) (Flask)
8.API Performance Optimization and Caching Using Redis (Flask)

