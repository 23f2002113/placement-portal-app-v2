import uuid
from flask import Blueprint,jsonify ,request,current_app
from models import db, User, StudentProfile, CompanyProfile, Role
from flask_security.utils import verify_password,hash_password

auth_blueprint = Blueprint("auth",__name__,url_prefix="/auth")


@auth_blueprint.route("/login",methods=["POST"])
def login():
    data=request.get_json() or {}

    email=data.get("email")
    password=data.get("password")

    if (not email or not password ):
        return jsonify({"message": "Email and Password are required"}),400
    
    user=User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"message": "User not found"}), 404

    if not verify_password(password, user.password):
        return jsonify({"message":"wrong password"}),400
    
    if not user.active:
        return jsonify({"message": "Wait ! Admin approval is required"}), 403
    
    # Fetch roles mapped to user
    roles_list = [role.name for role in user.roles]
    role = roles_list[0] if roles_list else None
    
    # Retrieve auth token using flask security 
    token = user.get_auth_token()
    
    return jsonify({"id": user.id,"email":user.email,"name":user.name,"role":role,"token":token}),200


@auth_blueprint.route("/register",methods=["POST"])
def register():
    data= request.get_json() or {}

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    role_name = data.get("role") 

    active=True

    if (not name or not email or not password or not role_name in ["company","student"]):
        return jsonify({"message":"All fields required or invalid role"}),400

    if User.query.filter_by(email=email).first():
        return jsonify({"message":"User already exists"}),400

    if role_name == "company":
        active = False  
    
    datastore=current_app.datastore

    try:
        new_user=datastore.create_user(name=name,email=email,password=hash_password(password),active=active)
        db.session.flush()

        role=datastore.find_role(role_name)
        datastore.add_role_to_user(new_user,role)

        if role_name == "student":
            unique_roll = data.get("roll_number") or f"STU-{uuid.uuid4().hex[:6].upper()}"
            student_profile = StudentProfile(
                user_id=new_user.id,
                roll_number=unique_roll,
                cgpa= data.get("cgpa", 0.0)
            )
            db.session.add(student_profile)

        elif role_name == "company":
            company_profile = CompanyProfile(
                user_id=new_user.id,
                name=name
            )
            db.session.add(company_profile)

        db.session.commit()

    except Exception as error:
        db.session.rollback()
        return jsonify({"message": str(error)}), 400
    
    return jsonify({"id": new_user.id,"email":new_user.email,"name":new_user.name}),201


    
    

        


    


