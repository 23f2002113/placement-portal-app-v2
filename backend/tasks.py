import os
import csv

from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab

from flask import current_app
from flask_mail import Message
from extensions import db, mail
from models import User, StudentProfile, CompanyProfile, Application, PlacementDrive, Placement

from extensions import celery


# 1. Daily Interview Reminders for students to scheduled interviews
@celery.task
def send_daily_interview_reminders():
    tomorrow = datetime.utcnow().date() + timedelta(days=1)
    
    # Query applications
    applications = Application.query.filter(
        Application.status == "interview",
        Application.interview_date >= tomorrow,
        Application.interview_date < tomorrow + timedelta(days=1)
    ).all()

    for app in applications:
        student = StudentProfile.query.get(app.student_id)
        user = User.query.get(student.user_id)
        drive = PlacementDrive.query.get(app.drive_id)
        company = CompanyProfile.query.get(drive.company_id)

        html_content = f"""
        <html>
            <body>
                <h2>Upcoming Placement Interview Tomorrow</h2>
                <p>Hello {user.name},</p>
                <p>This is a reminder that you have an interview scheduled for tomorrow:</p>
                <ul>
                    <li><strong>Company:</strong> {company.name}</li>
                    <li><strong>Position:</strong> {drive.job_title}</li>
                    <li><strong>Date & Time:</strong> {app.interview_date.strftime('%d-%b-%Y at %I:%M %p')}</li>
                    <li><strong>Instructions/Link:</strong> {app.feedback or 'Not provided.'}</li>
                </ul>
                <p>Best of luck from Placement Cell.</p>
            </body>
        </html>
        """

        message = Message(
            subject="Reminder: Upcoming Placement Interview Tomorrow",
            recipients=[user.email],
            html=html_content
        )
        try:
            mail.send(message)
        except Exception as e:
            print(f"\n[MAIL NOT SENT - NO SMTP SERVER]: {e}")
            print(f"EMAIL SUBJECT: {message.subject}")
            print(f"EMAIL RECIPIENT: {user.email}")
            print(f"EMAIL HTML BODY:\n{html_content}\n")
    
    return f"Send {len(applications)} interview reminders."


# 2. Monthly Placement Reports for Companies.
@celery.task
def send_monthly_placement_reports():
    companies = CompanyProfile.query.filter_by(status="approved").all()
    
    for company in companies:
        user = User.query.get(company.user_id)

        drives = PlacementDrive.query.filter_by(company_id=company.id).all()
        drive_ids = [d.id for d in drives]
        
        total_drives = len(drives)

        total_apps = Application.query.filter(Application.drive_id.in_(drive_ids)).count() if drive_ids else 0

        total_placed = Application.query.filter(Application.drive_id.in_(drive_ids), Application.status == 'placed').count() if drive_ids else 0

        # HTML layout of report.
        html_content = f"""
        <html>
            <body>
                <h2>Monthly Recruitment Performance Report</h2>
                <p>Hello {user.name},</p>
                <p>Here is your placement portal recruitment report for the past month:</p>
                <ul>
                    <li><strong>Total Drives Created:</strong> {total_drives}</li>
                    <li><strong>Total Applications Received:</strong> {total_apps}</li>
                    <li><strong>Successful Placements:</strong> {total_placed}</li>
                </ul>
                <p>Thank you from Placement Cell.</p>
            </body>
        </html>
        """
        
        message = Message(
            subject="Monthly Placement Report",
            recipients=[user.email],
            html=html_content
        )
        try:
            mail.send(message)
        except Exception as e:
            print(f"\n[MAIL NOT SENT - NO SMTP SERVER]: {e}")
            print(f"EMAIL SUBJECT: {message.subject}")
            print(f"EMAIL RECIPIENT: {user.email}")
            print(f"EMAIL HTML BODY:\n{html_content}\n")

    return f"Send reports to {len(companies)} companies."


# 3. Asynchronous CSV Exports 
@celery.task
def export_history_to_csv(user_id, email, role):
    export_dir = os.path.join(current_app.root_path, "static", "exports")
    os.makedirs(export_dir, exist_ok=True)
    
    filename = f"export_{role}_{user_id}.csv"
    file_path = os.path.join(export_dir, filename)

    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if role == 'student':
            student = StudentProfile.query.filter_by(user_id=user_id).first()
            writer.writerow(["Application ID", "Company", "Job Title", "Salary Package", "Date Submitted", "Status"])
            
            applications = Application.query.filter_by(student_id=student.id).all()
            for app in applications:
                drive = PlacementDrive.query.get(app.drive_id)
                company = CompanyProfile.query.get(drive.company_id)
                writer.writerow([
                    app.id, company.name, drive.job_title, drive.package_details,app.created_at.strftime('%d-%b-%Y'), app.status])
                
        elif role == 'company':
            company = CompanyProfile.query.filter_by(user_id=user_id).first()
            writer.writerow(["Application ID", "Student Name", "Roll Number", "Department", "Job Position", "Status"])
            
            drives = PlacementDrive.query.filter_by(company_id=company.id).all()
            for drive in drives:
                applications = Application.query.filter_by(drive_id=drive.id).all()
                for app in applications:
                    student = StudentProfile.query.get(app.student_id)
                    student_user = User.query.get(student.user_id)
                    writer.writerow([
                        app.id, student_user.name, student.roll_number,student.department or "N/A", drive.job_title, app.status
                    ])

    # Send Notification Email containing download link
    download_url = f"http://localhost:5000/static/exports/{filename}"
    message = Message(
        subject="Your Exported Placement History is Ready",
        recipients=[email],
        body=f"Hello,\n\nYour requested data export job has successfully completed.\n"
             f"You can download your CSV report by clicking the link below:\n\n"
             f"{download_url}\n\nBest regards,\nPlacement Cell"
    )
    try:
        mail.send(message)
    except Exception as e:
        print(f"\n[MAIL NOT SENT - NO SMTP SERVER]: {e}")
        print(f"EMAIL SUBJECT: {message.subject}")
        print(f"EMAIL RECIPIENT: {email}")
        print(f"EMAIL BODY:\n{message.body}\n")
    
    return f"Completed CSV compilation for {email}."


# (Celery Beat) ---
celery.conf.beat_schedule = {
    'send-interview-reminders-every-morning': {
        'task': 'tasks.send_daily_interview_reminders',
        'schedule': crontab(hour=9, minute=0),
    },
    'send-monthly-reports': {
        'task': 'tasks.send_monthly_placement_reports',
        'schedule': crontab(day_of_month=1, hour=9, minute=0), 
    }
}