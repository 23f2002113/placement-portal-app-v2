import os
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from flask_security import auth_required, roles_required, current_user
from models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application,Placement

company_blueprint = Blueprint("company", __name__, url_prefix="/company")

# function to check if the company is approved by the Admin or not
def get_approved_company_profile():
    profile = CompanyProfile.query.filter_by(user_id=current_user.id).first()
    if not profile or profile.status != "approved":
        return None
    return profile


# 1. Company Profile Details (Get and Update)
@company_blueprint.route("/profile", methods=["GET", "PUT"])
@auth_required("token")
@roles_required("company")
def get_and_update_profile():
    profile = CompanyProfile.query.filter_by(user_id=current_user.id).first_or_404()
    
    if request.method == "GET":
        return jsonify({
            "id": profile.id,
            "name": profile.name,
            "industry": profile.industry,
            "website": profile.website,
            "location": profile.location,
            "status": profile.status
        }), 200
        
    elif request.method == "PUT":
        data = request.get_json() or {}
        profile.industry = data.get("industry", profile.industry)
        profile.website = data.get("website", profile.website)
        profile.location = data.get("location", profile.location)
        
        db.session.commit()

        return jsonify({"message": "Profile updated successfully."}), 200


# 2. Get Statistics (Drives count, applications count, shortlisted count)
@company_blueprint.route("/statistics", methods=["GET"])
@auth_required("token")
@roles_required("company")
def get_statistics():
    profile = get_approved_company_profile()

    if not profile:
        return jsonify({"message": "Access Denied. Pending Admin approval is required."}), 403

    total_drives = PlacementDrive.query.filter_by(company_id=profile.id).count()
    
    # get applications across all drives created by this company
    applications_query = db.session.query(Application).join(PlacementDrive).filter(PlacementDrive.company_id == profile.id)
    total_applications = applications_query.count()
    total_shortlisted = applications_query.filter(Application.status == "shortlisted").count()
    
    return jsonify({
        "total_drives": total_drives,
        "total_applications": total_applications,
        "total_shortlisted": total_shortlisted
    }), 200


# 3. Create and Read Placement Drives
@company_blueprint.route("/drives", methods=["GET", "POST"])
@auth_required("token")
@roles_required("company")
def get_and_create_drives():
    profile = get_approved_company_profile()

    if not profile:
        return jsonify({"message": "Access Denied. Pending Admin approval."}), 403

    if request.method == "GET":
        drives = PlacementDrive.query.filter_by(company_id=profile.id).all()
        drives_list = []

        for drive in drives:
            drives_list.append({
                "id": drive.id,
                "job_title": drive.job_title,
                "job_description": drive.job_description,
                "salary_package": drive.package_details,
                "min_cgpa_criteria": float(drive.min_cgpa_criteria),
                "application_deadline": drive.deadline.strftime("%d-%b-%Y") if drive.deadline else "Not Specified",
                "drive_status": drive.drive_status
            })
        return jsonify(drives_list), 200
        
    elif request.method == "POST":
        data = request.get_json() or {}

        job_title = data.get("job_title")
        job_description = data.get("job_description")
        salary_package = data.get("salary_package")
        min_cgpa = data.get("min_cgpa_criteria", 0.0)
        deadline_str = data.get("application_deadline")

        if not job_title :
            return jsonify({"message": "Job title are required."}), 400

        # Parse deadline date
        parsed_deadline = None
        if deadline_str:
            try:
                parsed_deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            except ValueError:
                return jsonify({"message": "Invalid date format. Use YYYY-MM-DD."}), 400

        new_drive = PlacementDrive(
            company_id=profile.id,
            job_title=job_title,
            job_description=job_description,
            package_details=salary_package,
            min_cgpa_criteria=min_cgpa,
            deadline=parsed_deadline,
            drive_status="pending" 
        )
        
        db.session.add(new_drive)
        db.session.commit()

        return jsonify({"message": "Placement drive created successfully and sent for Admin approval."}), 201


# 4. Change Placement Drive Status (Active / Closed)
@company_blueprint.route("/drive/<int:drive_id>/close", methods=["PUT"])
@auth_required("token")
@roles_required("company")
def close_drive(drive_id):
    profile = get_approved_company_profile()
    if not profile:
        return jsonify({"message": "Access Denied."}), 403

    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=profile.id).first_or_404()
    drive.drive_status = "closed"
    db.session.commit()
    
    return jsonify({"message": "Placement drive has been closed."}), 200


# 5. Get All Received Student Applications
@company_blueprint.route("/applications", methods=["GET"])
@auth_required("token")
@roles_required("company")
def get_received_applications():
    profile = get_approved_company_profile()
    if not profile:
        return jsonify({"message": "Access Denied."}), 403

    # Fetch applications specifically targeting this company's drives
    query = (
        db.session.query(Application, StudentProfile, User, PlacementDrive)
        .join(StudentProfile, Application.student_id == StudentProfile.id)
        .join(User, StudentProfile.user_id == User.id)
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
        .filter(PlacementDrive.company_id == profile.id)
    )
        
    results = query.all()
    applications_list = []
    
    for app, student, user, drive in results:
        applications_list.append({
            "id": app.id,
            "student_name": user.name,
            "roll_no": student.roll_number,
            "cgpa": float(student.cgpa),
            "department": student.department,
            "job_title": drive.job_title,
            "status": app.status,
            "resume_link": student.resume_path or "Not_Provided.pdf",
            "interview_date" : app.interview_date.isoformat() if app.interview_date else None,
            "feedback" : app.feedback
        })
        
    return jsonify(applications_list), 200


# 6. Update Application Selection Status (Shortlisted / Selected / Rejected)
@company_blueprint.route("/application/<int:app_id>/status", methods=["PUT"])
@auth_required("token")
@roles_required("company")
def update_application_status(app_id):
    profile = get_approved_company_profile()
    if not profile:
        return jsonify({"message": "Access Denied."}), 403

    data = request.get_json() or {}
    new_status = data.get("status") 

    if new_status not in ["shortlisted", "interview", "rejected"]:
        return jsonify({"message": "Invalid selection status value."}), 400

    # Ensure application belongs to a drive created by this company
    app = Application.query.join(PlacementDrive).filter(
        Application.id == app_id, 
        PlacementDrive.company_id == profile.id
    ).first_or_404()

    app.status = new_status
    db.session.commit()
    
    return jsonify({"message": f"Student Application status updated to {new_status} successfully."}), 200

# 7.Issue and Upload Job Offer letter
@company_blueprint.route("/application/<int:app_id>/offer", methods=["POST"])
@auth_required("token")
@roles_required("company")
def issue_offer_letter(app_id):
    print("CURRENT USER:", current_user)
    profile = get_approved_company_profile()
    if not profile:
        return jsonify({"message": "Access Denied."}), 403

    application = Application.query.join(PlacementDrive).filter(
        Application.id == app_id,
        PlacementDrive.company_id == profile.id
    ).first_or_404()

    position = request.form.get("position")
    joining_date = request.form.get("joining_date")
    file = request.files.get("offer_letter")

    if not position or not joining_date or not file:
        return jsonify({"message": "Position, Joining date, and Offer Letter are required."}), 400

    try:
        joining_date = datetime.strptime(joining_date, "%Y-%m-%d")
    except ValueError:
        return jsonify({"message": "Use this date format- YYYY-MM-DD."}), 400

    if file and file.filename.lower().endswith(".pdf"):
        filename = f"Offer_app_{application.id}.pdf"
        upload_dir = os.path.join(current_app.root_path, "static", "uploads", "offers")
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, filename)
        file.save(file_path)
    else:
        return jsonify({"message": "Only PDF files are allowed."}), 400

    # create new Placement record
    placement = Placement.query.filter_by(application_id=application.id).first()
    if not placement:
        placement = Placement(
            student_id=application.student_id,
            company_id=profile.id,
            application_id=application.id,
            drive_id=application.drive_id,
            position=position,
            offer_letter_path=filename,
            joining_date=joining_date
        )
        db.session.add(placement)
    else:
        placement.position = position
        placement.offer_letter_path = filename
        placement.joining_date = joining_date

    application.status = "offer"
    db.session.commit()

    return jsonify({"message": "Job offer letter issued successfully."}), 200

# 8.Scheduling Interview and send feedback
@company_blueprint.route("/application/<int:app_id>/schedule-interview", methods=["PUT"])
@auth_required("token")
@roles_required("company")
def schedule_interview(app_id):
    profile = get_approved_company_profile()
    if not profile:
        return jsonify({"message": "Access Denied."}), 403

    data = request.get_json() or {}
    date_str = data.get("interview_date")
    feedback = data.get("feedback", "")

    if not date_str:
        return jsonify({"message": "Interview date is required."}), 400

    app = Application.query.join(PlacementDrive).filter(
        Application.id == app_id, 
        PlacementDrive.company_id == profile.id
    ).first_or_404()

    try:
        if "T" in date_str:
            app.interview_date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
        else:
            app.interview_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD HH:MM."}), 400

    app.feedback = feedback
    app.status = "interview"  
    db.session.commit()

    return jsonify({"message": "Interview details scheduled successfully."}), 200


    
    
    
