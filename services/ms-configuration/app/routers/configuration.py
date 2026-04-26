from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from app.infrastructure.database import get_db
from app.services.profile_service import ProfileService
from app.core.exceptions import InvalidWeightsError, ProfileNotFoundError, NoActiveProfileError

router = APIRouter()


class WeightsSchema(BaseModel):
    population: float = Field(25, ge=0, le=100)
    income: float = Field(25, ge=0, le=100)
    education: float = Field(25, ge=0, le=100)
    competition: float = Field(25, ge=0, le=100)

    def to_dict(self) -> Dict[str, float]:
        return self.model_dump()


class CreateProfileRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field("", max_length=500)
    business_type: str = Field(..., min_length=2, max_length=50)
    weights: WeightsSchema


class UpdateProfileRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: str = Field("", max_length=500)
    business_type: str = Field(..., min_length=2, max_length=50)
    weights: WeightsSchema


class ProfileResponse(BaseModel):
    id: int
    name: str
    description: str
    target_business_type: str
    is_active: bool
    weights: Dict[str, float]
    created_at: str


@router.post("/profiles", response_model=ProfileResponse)
async def create_profile(request: CreateProfileRequest, db: AsyncSession = Depends(get_db)):
    try:
        service = ProfileService(db)
        profile = await service.create_profile(
            name=request.name,
            description=request.description,
            business_type=request.business_type,
            weights=request.weights.to_dict()
        )
        return ProfileResponse(**profile.__dict__)
    except InvalidWeightsError as e:
        raise e


@router.get("/profiles", response_model=List[ProfileResponse])
async def get_profiles(db: AsyncSession = Depends(get_db)):
    service = ProfileService(db)
    profiles = await service.get_all_profiles()
    return [ProfileResponse(**p.__dict__) for p in profiles]


@router.get("/profiles/active", response_model=ProfileResponse)
async def get_active_profile(db: AsyncSession = Depends(get_db)):
    service = ProfileService(db)
    profile = await service.get_active_profile()
    if not profile:
        raise NoActiveProfileError()
    return ProfileResponse(**profile.__dict__)


@router.get("/profiles/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    service = ProfileService(db)
    profile = await service.get_profile(profile_id)
    if not profile:
        raise ProfileNotFoundError(profile_id)
    return ProfileResponse(**profile.__dict__)


@router.put("/profiles/{profile_id}", response_model=ProfileResponse)
async def update_profile(profile_id: int, request: UpdateProfileRequest, db: AsyncSession = Depends(get_db)):
    try:
        service = ProfileService(db)
        profile = await service.update_profile(
            profile_id=profile_id,
            name=request.name,
            description=request.description,
            business_type=request.business_type,
            weights=request.weights.to_dict()
        )
        return ProfileResponse(**profile.__dict__)
    except InvalidWeightsError as e:
        raise e
    except ProfileNotFoundError as e:
        raise e


@router.post("/profiles/{profile_id}/activate", response_model=ProfileResponse)
async def activate_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    try:
        service = ProfileService(db)
        profile = await service.activate_profile(profile_id)
        return ProfileResponse(**profile.__dict__)
    except ProfileNotFoundError as e:
        raise e


@router.get("/weights/active")
async def get_active_weights(db: AsyncSession = Depends(get_db)):
    service = ProfileService(db)
    weights = await service.get_active_weights()
    return {"weights": weights}

@router.delete("/profiles/{profile_id}")
async def delete_profile(profile_id: int, db: AsyncSession = Depends(get_db)):
    try:
        service = ProfileService(db)
        profile = await service.get_profile(profile_id)
        if not profile:
            raise ProfileNotFoundError(profile_id)

        if profile.is_active:
            raise HTTPException(400, detail="No se puede eliminar el perfil activo")

        await service.delete_profile(profile_id)
        return {"success": True, "message": f"Perfil {profile_id} eliminado"}
    except ProfileNotFoundError as e:
        raise e
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, detail=f"Error interno: {str(e)}")