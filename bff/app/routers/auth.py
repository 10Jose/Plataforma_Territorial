from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel, EmailStr
from app.infrastructure.database import get_db
from app.services.user_service import UserService
from app.core.security import create_access_token, decode_token
from app.domain.models import User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


class Token(BaseModel):
    access_token: str
    token_type: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: AsyncSession = Depends(get_db)
) -> User:
    """Obtiene el usuario actual desde el token."""
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user)
) -> User:
    """Obtiene el usuario activo."""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user


async def get_current_admin_user(
        current_user: User = Depends(get_current_user)
) -> User:
    """Obtiene el usuario admin (solo para endpoints admin)."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene permisos de administrador"
        )
    return current_user


@router.post("/register", response_model=UserResponse)
async def register(
        user_data: UserCreate,
        db: AsyncSession = Depends(get_db)
):
    """Registra un nuevo usuario."""
    user_service = UserService(db)

    # Verificar si el usuario ya existe
    existing = await user_service.get_user_by_username(user_data.username)
    if existing:
        raise HTTPException(400, "Nombre de usuario ya registrado")

    existing_email = await user_service.get_user_by_email(user_data.email)
    if existing_email:
        raise HTTPException(400, "Email ya registrado")

    # Crear usuario
    user = await user_service.create_user(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name
    )

    return user


@router.post("/token", response_model=Token)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    """Endpoint de login - devuelve token JWT."""
    user_service = UserService(db)
    user = await user_service.authenticate(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(
        current_user: User = Depends(get_current_active_user)
):
    """Obtener información del usuario autenticado."""
    return current_user