import os
from flask import Blueprint, jsonify, request, current_app
from flask_security import auth_required, roles_required, current_user
from werkzeug.utils import secure_filename
from models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application,Placement


student_blueprint = Blueprint("student", __name__, url_prefix="/student")


# Helper function to get logged-in student's profile
def get_student_profile():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first()
    if not profile or profile.is_blacklisted:
        return None
    return profile


# 1. Student Profile details(Get and Update)
@student_blueprint.route("/profile", methods=["GET", "PUT"])
@auth_required("token")
@roles_required("student")
def get_and_update_profile():
    profile = StudentProfile.query.filter_by(user_id=current_user.id).first_or_404()
    
    if request.method == "GET":
        return jsonify({
            "profile_id": profile.id,
            "name": current_user.name,
            "email": current_user.email,
            "roll_no": profile.roll_number,
            "cgpa": float(profile.cgpa),
            "education": profile.education or "",
            "department": profile.department or "",
            "skills": profile.skills or "",
            "resume_link": profile.resume_path or ""
        }), 200
        
    elif request.method == "PUT":
        data = request.get_json() or {}

        profile.education = data.get("education", profile.education)
        profile.department = data.get("department", profile.department)
        profile.skills = data.get("skills", profile.skills)
        profile.roll_number = data.get("roll_no", profile.roll_number)
        
        try:
            profile.cgpa = float(data.get("cgpa", profile.cgpa))
        except ValueError:
            return jsonify({"message": "Invalid CGPA numerical format."}), 400
            
        db.session.commit()

        return jsonify({"message": "Profile updated successfully."}), 200
    
    
# 2. Upload PDF Resume
@student_blueprint.route("/upload-resume", methods=["POST"])
@auth_required("token")
@roles_required("student")
def resume_upload():
    profile = get_student_profile()
    if not profile:
        return jsonify({"message": "Access Denied or Profile Blacklisted."}), 403

    if "resume" not in request.files:
        return jsonify({"message": "No file supplied."}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"message": "No file selected."}), 400

    # Check only PDF files are uploaded
    if file and file.filename.lower().endswith(".pdf"):
        filename = f"resume_user_{current_user.id}.pdf"
        
        upload_dir = os.path.join(current_app.root_path, "static", "uploads", "resumes")
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)

        profile.resume_path = filename
        db.session.commit()

        return jsonify({
            "message": "Resume file uploaded successfully.",
            "filename": filename
        }), 200

    return jsonify({"message": "Invalid file format. Only PDF files are allowed."}), 400


# 3. View and Search All Approved Placement Drives 
@student_blueprint.route("/drives", methods=["GET"])
@auth_required("token")
@roles_required("student")
def get_approved_drives():
    profile = get_student_profile()
    if not profile:
        return jsonify({"message": "Access Denied or Profile Blacklisted."}), 403

    search_word = request.args.get("search", "").strip()

    # query for all approved drives
    query = db.session.query(PlacementDrive, CompanyProfile).join(
        CompanyProfile, PlacementDrive.company_id == CompanyProfile.id
    ).filter(PlacementDrive.drive_status == "approved")

    # Apply keyword filtering 
    if search_word:
        query = query.filter(
            (PlacementDrive.job_title.ilike(f"%{search_word}%")) |
            (PlacementDrive.job_description.ilike(f"%{search_word}%")) |
            (CompanyProfile.name.ilike(f"%{search_word}%"))
        )

    results = query.all()
    drives_list = []

    # Get drive IDs where this student has already applied 
    applied_drive_ids = [app.drive_id for app in Application.query.filter_by(student_id=profile.id).all()]

    for drive, company in results:
        drives_list.append({
            "id": drive.id,
            "company_name": company.name,
            "job_title": drive.job_title,
            "job_description": drive.job_description,
            "salary_package": drive.package_details,
            "min_cgpa_criteria": float(drive.min_cgpa_criteria),
            "application_deadline": drive.deadline.strftime('%d-%b-%Y') if drive.deadline else "Not Specified",
            "location": company.location,
            "already_applied": drive.id in applied_drive_ids
        })

    return jsonify(drives_list), 200


# 4. Apply for a Placement Drive 
@student_blueprint.route("/apply/<int:drive_id>", methods=["POST"])
@auth_required("token")
@roles_required("student")
def drive_apply(drive_id):
    profile = get_student_profile()
    if not profile:
        return jsonify({"message": "Access Denied or Profile blacklisted."}), 403

    # Ensure student has uploaded a resume before applying
    if not profile.resume_path:
        return jsonify({"message": "You must upload a resume before apply in placement drive."}), 400

    drive = PlacementDrive.query.get_or_404(drive_id)

    if drive.drive_status != "approved":
        return jsonify({"message": "This drive is not approved by Admin"}), 400

    # Double Application Check
    existing_app = Application.query.filter_by(student_id=profile.id, drive_id=drive.id).first()
    if existing_app:
        return jsonify({"message": "You are already applied to this drive.Now you are not allowed to re-apply in same drive."}), 400

    # CGPA Verification Check
    if float(profile.cgpa) < float(drive.min_cgpa_criteria):
        return jsonify({"message": f"Your CGPA ({profile.cgpa}) does not meet the eligibility cutoff ({drive.min_cgpa_criteria})."}), 400

    # Create new application
    new_application = Application(
        student_id=profile.id,
        drive_id=drive.id,
        status="applied"
    )

    db.session.add(new_application)
    db.session.commit()

    return jsonify({"message": f"Application to '{drive.job_title}' job position submitted successfully!"}), 201

# 5. Accept job offer
@student_blueprint.route("/application/<int:app_id>/accept", methods=["POST"])
@auth_required("token")
@roles_required("student")
def accept_job_offer(app_id):
    profile = get_student_profile()
    if not profile:
        return jsonify({"message": "Access Denied or Profile Blacklisted."}), 403

    application = Application.query.filter_by(id=app_id, student_id=profile.id).first_or_404()
    
    if application.status != "offer":
        return jsonify({"message": " You are not allowed to accept offer."}), 400

    application.status = "placed"
    db.session.commit()

    return jsonify({"message": "Congratulations! Offer accepted."}), 200

# 6. Student's Application History
@student_blueprint.route("/applications", methods=["GET"])
@auth_required("token")
@roles_required("student")
def get_student_applications():
    profile = get_student_profile()
    if not profile:
        return jsonify({"message": "Access Denied or Profile Blacklisted."}), 403

    query = db.session.query(Application, PlacementDrive, CompanyProfile).join(PlacementDrive, Application.drive_id == PlacementDrive.id).join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id).filter(Application.student_id == profile.id)

    results = query.all()
    apps_list = []

    for app, drive, company in results:
        placement = Placement.query.filter_by(application_id=app.id).first()

        apps_list.append({
            "id": app.id,
            "company_name": company.name,
            "job_title": drive.job_title,
            "salary_package": drive.package_details,
            "application_date": app.created_at.strftime('%d-%b-%Y') if app.created_at else "Not Specified",
            "status": app.status,
            "interview_date": app.interview_date.strftime('%d-%b-%Y at %I:%M %p') if app.interview_date else None,
            "feedback" : app.feedback,
            "offer_letter_path": placement.offer_letter_path if placement else None,
            "joining_date": placement.joining_date.strftime('%d-%b-%Y') if (placement and placement.joining_date) else None      
        })

    return jsonify(apps_list), 200




    

