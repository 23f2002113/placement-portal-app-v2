from flask import Blueprint, jsonify, request
from flask_security import auth_required, roles_required
from models import db, User, StudentProfile, CompanyProfile, PlacementDrive, Application, Placement

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")

# 1. Get Statistics 
@admin_blueprint.route("/statistics", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def get_statistics():
    total_companies = CompanyProfile.query.filter_by(status="approved").count()
    total_students = StudentProfile.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
    total_placements = Placement.query.count()
    
    return jsonify({
        "total_companies": total_companies,
        "total_students": total_students,
        "total_drives": total_drives,
        "total_applications": total_applications,
        "total_placements": total_placements
    }), 200


# 2. Get (Approved) Companies list
@admin_blueprint.route("/companies", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def get_approved_companies():
    search_word = request.args.get("search", "").strip()
    
    query = db.session.query(CompanyProfile, User).join(User, CompanyProfile.user_id == User.id).filter(CompanyProfile.status == "approved")
    
    if search_word:
        query = query.filter(
            (CompanyProfile.name.ilike(f"%{search_word}%")) |
            (CompanyProfile.industry.ilike(f"%{search_word}%"))
        )
        
    results = query.all()
    companies_list = []
    
    for profile, user in results:
        companies_list.append({
            "profile_id": profile.id,
            "user_id": user.id,
            "name": profile.name,
            "industry": profile.industry,
            "website": profile.website,
            "location": profile.location,
            "status": profile.status,
            "active": user.active
        })
    return jsonify(companies_list), 200


# 3. Get Pending Company Registration Applications
@admin_blueprint.route("/companies/pending", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def get_pending_companies():
    query = db.session.query(CompanyProfile, User).join(User, CompanyProfile.user_id == User.id).filter(CompanyProfile.status == "pending")

    results = query.all()
    pending_list = []

    for profile, user in results:
        pending_list.append({
            "profile_id": profile.id,
            "user_id": user.id,
            "name": profile.name,
            "industry": profile.industry,
            "website": profile.website,
            "location": profile.location,
            "status": profile.status,
            "active": user.active
        })
        
    return jsonify(pending_list), 200


# 4. Approve / Reject Company Applications
@admin_blueprint.route("/company/<int:id>/<string:action>", methods=["PUT"])
@auth_required("token")
@roles_required("admin")
def manage_company_application(id, action):
    profile = CompanyProfile.query.get_or_404(id)
    user = User.query.get(profile.user_id)
    
    if action == "approve":
        profile.status = "approved"
        if user:
            user.active = True
    elif action == "reject":
        profile.status = "rejected"
        if user:
            user.active = False
    else:
        return jsonify({"message": "Invalid action value"}), 400
        
    db.session.commit()

    return jsonify({"message": f"Company profile '{profile.name}' status change to {action}d."}), 200


# 5. Blacklist Company Profile
@admin_blueprint.route("/company/<int:id>/blacklist", methods=["POST"])
@auth_required("token")
@roles_required("admin")
def blacklist_company(id):
    profile = CompanyProfile.query.get_or_404(id)
    user = User.query.get(profile.user_id)
    
    profile.status = "rejected" 
    if user:
        user.active = False 
        
    db.session.commit()

    return jsonify({"message": f"Company '{profile.name}' has been blacklisted "}), 200


# 6. Get Registered Students list
@admin_blueprint.route("/students", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def get_registered_students():
    search_word = request.args.get("search", "").strip()
    
    query = db.session.query(StudentProfile, User).join(User, StudentProfile.user_id == User.id).filter(StudentProfile.is_blacklisted == False)
    
    if search_word:
        query = query.filter(
            (User.name.ilike(f"%{search_word}%")) | 
            (User.email.ilike(f"%{search_word}%")) | 
            (StudentProfile.roll_number.ilike(f"%{search_word}%")) |
            (StudentProfile.department.ilike(f"%{search_word}%"))
        )
        
    results = query.all()
    students_list = []

    for profile, user in results:
        students_list.append({
            "profile_id": profile.id,
            "user_id": user.id,
            "name": user.name,
            "email": user.email,
            "roll_number": profile.roll_number,
            "cgpa": float(profile.cgpa),
            "skills": profile.skills,
            "department": profile.department,
            "is_blacklisted": profile.is_blacklisted,
            "active": user.active
        })

    return jsonify(students_list), 200


# 7. Blacklist Student Profile
@admin_blueprint.route("/student/<int:id>/blacklist", methods=["POST"])
@auth_required("token")
@roles_required("admin")
def blacklist_student(id):
    profile = StudentProfile.query.get_or_404(id)
    user = User.query.get(profile.user_id)
    
    profile.is_blacklisted = True
    if user:
        user.active = False
        
    db.session.commit()

    return jsonify({"message": f"Student '{user.name if user else 'Unknown'}' blacklisted successfully."}), 200


# 8. Get Placement Drives (Separated into Ongoing and Pending)
@admin_blueprint.route("/drives", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def placement_drives():
    all_drives = PlacementDrive.query.all()
    ongoing_list = []
    pending_list = []
    
    for drive in all_drives:
        company = CompanyProfile.query.get(drive.company_id)

        drive_data = {
            "id": drive.id,
            "company_name": company.name if company else "Unknown",
            "job_title": drive.job_title,
            "job_description": drive.job_description,
            "salary_package": drive.package_details,
            "eligibility_criteria": f"CGPA >= {drive.min_cgpa_criteria}",
            "application_deadline": drive.deadline.strftime('%d-%b-%Y') if drive.deadline else "Not Specified",
            "location": company.location if company else "Not Specified"
        }
        if drive.drive_status == "approved":
            ongoing_list.append(drive_data)

        elif drive.drive_status == "pending":
            pending_list.append(drive_data)
            
    return jsonify({"ongoing": ongoing_list, "pending": pending_list}), 200


# 9. Approve / Reject / Complete Placement Drives
@admin_blueprint.route("/drive/<int:id>/<string:action>", methods=["PUT"])
@auth_required("token")
@roles_required("admin")
def manage_placement_drive(id, action):
    drive = PlacementDrive.query.get_or_404(id)
    
    if action == "approve":
        drive.drive_status = "approved"
    elif action == "reject":
        drive.drive_status = "closed"
    elif action == "complete":
        drive.drive_status = "closed"
    else:
        return jsonify({"message": "Invalid action"}), 400
        
    db.session.commit()

    return jsonify({"message": f"Placement drive updated successfully."}), 200


# 10. Get All Student Applications
@admin_blueprint.route("/applications", methods=["GET"])
@auth_required("token")
@roles_required("admin")
def get_all_student_applications():
    query = (
    db.session.query(Application, StudentProfile, User, PlacementDrive, CompanyProfile)
    .join(StudentProfile, Application.student_id == StudentProfile.id)
    .join(User, StudentProfile.user_id == User.id)
    .join(PlacementDrive, Application.drive_id == PlacementDrive.id)
    .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)
     )
        
    results = query.all()
    apps_list = []

    for app, student, user, drive, company in results:
        apps_list.append({
            "id": app.id,
            "student_name": user.name,
            "department": student.department,
            "drive_id": drive.id,
            "job_title": drive.job_title,
            "job_description": drive.job_description,
            "company_name": company.name,
            "status": app.status,
            "application_date": app.created_at.strftime('%d-%b-%Y') if app.created_at else "Not Specified",
            "resume_link": student.resume_path or "Not_Provided.pdf"
        })

    return jsonify(apps_list), 200