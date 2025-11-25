from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from jose import jwt
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.database import get_db
from app.repositories.user_repository import UserRepository

router = APIRouter()

# Initialize OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)


def create_access_token(data: dict) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


@router.get("/login")
async def login(request: Request, db: Session = Depends(get_db), mock_user: int = 1):
    """Initiate Google OAuth login flow or use mock user in dev mode."""
    # If in development mode, bypass Google OAuth and use mock user
    if settings.DEV_MODE:
        # Define available mock users
        mock_users = {
            1: {
                "google_user_id": "dev-user-12345",
                "email": "dev@example.com",
                "name": "Dev User",
                "picture": "https://ui-avatars.com/api/?name=Dev+User&background=random"
            },
            2: {
                "google_user_id": "dev-user-67890",
                "email": "alice@example.com",
                "name": "Alice Smith",
                "picture": "https://ui-avatars.com/api/?name=Alice+Smith&background=0D8ABC"
            }
        }

        # Get the selected mock user (default to user 1)
        mock_user_data = mock_users.get(mock_user, mock_users[1])

        # Get or create mock user in database
        user_repo = UserRepository(db)
        user = user_repo.get_or_create(
            google_user_id=mock_user_data["google_user_id"],
            email=mock_user_data["email"],
            name=mock_user_data["name"],
            picture=mock_user_data["picture"]
        )

        # Create access token
        access_token = create_access_token(
            data={
                "sub": user.google_user_id,
                "email": user.email,
                "name": user.name
            }
        )

        # Redirect to frontend with token
        frontend_url = "http://localhost:5173"
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?token={access_token}&user_id={user.google_user_id}&name={user.name}&email={user.email}&picture={user.picture or ''}"
        )

    # Production mode: use Google OAuth
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback."""
    try:
        # Get the token from Google
        token = await oauth.google.authorize_access_token(request)

        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info from Google")

        # Extract user data
        google_user_id = user_info.get('sub')
        email = user_info.get('email')
        name = user_info.get('name')
        picture = user_info.get('picture')

        if not google_user_id or not email or not name:
            raise HTTPException(status_code=400, detail="Incomplete user info from Google")

        # Get or create user in database
        user_repo = UserRepository(db)
        user = user_repo.get_or_create(
            google_user_id=google_user_id,
            email=email,
            name=name,
            picture=picture
        )

        # Create access token
        access_token = create_access_token(
            data={
                "sub": user.google_user_id,
                "email": user.email,
                "name": user.name
            }
        )

        # Redirect to frontend with token
        frontend_url = "http://localhost:5173"
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?token={access_token}&user_id={user.google_user_id}&name={user.name}&email={user.email}&picture={user.picture or ''}"
        )

    except Exception as e:
        print(f"Error during OAuth callback: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")
