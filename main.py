import uvicorn
import pyrebase
from fastapi import FastAPI
from models import SignUpSchema, LoginSchema, UserSchema, UpdateUserSchema
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from fastapi.requests import Request
import firebase_admin
from firebase_admin import credentials, auth, firestore

# Create a FastAPI app instance
app = FastAPI(
    description="This is a simple app to show Firebase Auth with FastAPI",
    title="Firebase Auth",
    docs_url="/",
)

# Initialize Firebase Admin SDK using the service account key
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json")  
    firebase_admin.initialize_app(cred)

# Firebase Web API configuration
firebaseConfig = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_AUTH_DOMAIN",
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_STORAGE_BUCKET",
    "messagingSenderId": "YOUR_MESSAGING_SENDER_ID",
    "appId": "YOUR_APP_ID",
    "measurementId": "YOUR_MEASUREMENT_ID",
    "databaseURL": "",
}

# Initialize the Firebase app using the configuration
firebase = pyrebase.initialize_app(firebaseConfig)

# Initialize Firestore
db = firestore.client()

# Endpoint for user registration
@app.post('/signup')
async def create_an_account(user_data: SignUpSchema):
    email = user_data.email
    password = user_data.password
    username = user_data.username
    full_name = user_data.full_name

    try:
        # Create a new user in Firebase Authentication
        user = auth.create_user(
            email=email,
            password=password
        )

        # Store user information in Firestore
        user_data = {
            "email": email,
            "username": username,
            "full_name": full_name,
            "created_at": firestore.SERVER_TIMESTAMP,
        }
        user_ref = db.collection("users").document(user.uid)
        user_ref.set(user_data)

        return JSONResponse(content={"message": f"User account created successfully for user {user.uid}"}, status_code=201)
    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=400,
            detail=f"Account already created for the email {email}"
        )

# Endpoint for user login
@app.post('/login')
async def create_access_token(user_data: LoginSchema):
    email = user_data.email
    password = user_data.password

    try:
        # Sign in the user with email and password
        user = firebase.auth().sign_in_with_email_and_password(
            email=email,
            password=password
        )

        token = user['idToken']

        return JSONResponse(
            content={
                "token": token
            }, status_code=200
        )

    except:
        raise HTTPException(
            status_code=400, detail="Invalid Credentials"
        )

from fastapi import Query

# Endpoint to get user profile
@app.get('/get_user_profile')
async def get_user_profile(token: str = Query(..., title="Authorization Token")):
    try:
        # Verify the ID token provided by the client
        user = auth.verify_id_token(token)
        user_id = user["user_id"]

        # Retrieve user profile information from Firestore
        user_ref = db.collection("users").document(user_id)
        user_data = user_ref.get().to_dict()

        if user_data:
            created_at = user_data["created_at"].strftime('%Y-%m-%d %H:%M:%S')

            # Update the user_data dictionary with the string representation of created_at
            user_data["created_at"] = created_at

            return JSONResponse(content=user_data, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="User profile not found")
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Invalid or missing ID token")

# Endpoint to update user profile
@app.put('/profile')
async def update_user_profile(updated_data: UpdateUserSchema, token: str = Query(..., title="Authorization Token")):
    try:
        # Verify the ID token provided by the client
        user = auth.verify_id_token(token)
        user_id = user["user_id"]

        # Update user profile information in Firestore
        user_ref = db.collection("users").document(user_id)
        user_ref.update(updated_data.dict(exclude_unset=True))

        return JSONResponse(content={"message": "User profile updated successfully"}, status_code=200)
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Invalid or missing ID token")

# Endpoint to delete user account
@app.delete('/account')
async def delete_user_account(token: str = Query(..., title="Authorization Token")):
    try:
        # Verify the ID token provided by the client
        user = auth.verify_id_token(token)
        user_id = user["user_id"]

        # Delete user account from Firebase Authentication
        auth.delete_user(user_id)

        # Delete user profile from Firestore
        user_ref = db.collection("users").document(user_id)
        user_ref.delete()

        return JSONResponse(content={"message": "User account deleted successfully"}, status_code=200)
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Invalid or missing ID token")

# Endpoint to send a password reset email
@app.post('/reset_password')
async def reset_password(email: str):
    try:
        # Send a password reset email to the provided email address
        firebase.auth().send_password_reset_email(email=email)

        return JSONResponse(content={"message": "Password reset email sent successfully"}, status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail="Password reset email could not be sent: " + str(e)
        )

if __name__ == "__main__":
    # Run the FastAPI server using uvicorn
    uvicorn.run("main:app", reload=True)

