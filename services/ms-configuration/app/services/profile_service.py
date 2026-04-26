from typing import List, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
import uuid
from app.domain.models import BusinessProfile, ScoringConfiguration
from app.domain.interfaces import BusinessProfileData
from app.services.weight_validator import WeightValidator
from app.services.audit_client import AuditClient
from app.core.exceptions import InvalidWeightsError, ProfileNotFoundError


class ProfileService:

    def __init__(self, db: AsyncSession, audit_client: Optional[AuditClient] = None):
        self.db = db
        self.validator = WeightValidator()
        self.audit_client = audit_client or AuditClient("ms-configuration")

    async def create_profile(
            self,
            name: str,
            description: str,
            business_type: str,
            weights: Dict[str, float],
            user_id: Optional[int] = None,
            username: Optional[str] = None
    ) -> BusinessProfileData:
        trace_id = str(uuid.uuid4())

        await self.audit_client.log_event(
            event_type="profile_create_started",
            user_id=user_id,
            username=username,
            trace_id=trace_id,
            details={"name": name, "business_type": business_type}
        )

        if not self.validator.validate(weights):
            raise InvalidWeightsError(self.validator.get_errors())

        profile = BusinessProfile(
            name=name,
            description=description,
            target_business_type=business_type,
            is_active=False
        )
        self.db.add(profile)
        await self.db.flush()

        config = ScoringConfiguration(
            business_profile_id=profile.id,
            population_weight=int(weights.get("population", 25)),
            income_weight=int(weights.get("income", 25)),
            education_weight=int(weights.get("education", 25)),
            competition_weight=int(weights.get("competition", 25)),
            additional_weights_json={
                k: v for k, v in weights.items()
                if k not in ["population", "income", "education", "competition"]
            }
        )
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(profile)

        await self.audit_client.log_event(
            event_type="profile_create_completed",
            reference_id=str(profile.id),
            user_id=user_id,
            username=username,
            trace_id=trace_id,
            details={"profile_id": profile.id, "weights": weights}
        )

        return self._to_dto(profile, config)

    async def get_active_profile(self) -> Optional[BusinessProfileData]:
        stmt = select(BusinessProfile).where(BusinessProfile.is_active == True)
        result = await self.db.execute(stmt)
        profile = result.scalar_one_or_none()

        if not profile:
            return None

        config = await self._get_active_config(profile.id)
        return self._to_dto(profile, config) if config else None

    async def get_all_profiles(self) -> List[BusinessProfileData]:
        stmt = select(BusinessProfile).order_by(BusinessProfile.created_at.desc())
        result = await self.db.execute(stmt)
        profiles = result.scalars().all()

        dtos = []
        for profile in profiles:
            config = await self._get_active_config(profile.id)
            if config:
                dtos.append(self._to_dto(profile, config))
        return dtos

    async def get_profile(self, profile_id: int) -> Optional[BusinessProfileData]:
        profile = await self.db.get(BusinessProfile, profile_id)
        if not profile:
            return None

        config = await self._get_active_config(profile.id)
        return self._to_dto(profile, config) if config else None

    async def update_profile(
            self,
            profile_id: int,
            name: str,
            description: str,
            business_type: str,
            weights: Dict[str, float],
            user_id: Optional[int] = None,
            username: Optional[str] = None
    ) -> BusinessProfileData:
        trace_id = str(uuid.uuid4())

        await self.audit_client.log_event(
            event_type="profile_update_started",
            reference_id=str(profile_id),
            user_id=user_id,
            username=username,
            trace_id=trace_id,
            details={"name": name}
        )

        if not self.validator.validate(weights):
            raise InvalidWeightsError(self.validator.get_errors())

        profile = await self.db.get(BusinessProfile, profile_id)
        if not profile:
            raise ProfileNotFoundError(profile_id)

        profile.name = name
        profile.description = description
        profile.target_business_type = business_type

        # Desactivar configuración anterior
        await self.db.execute(
            update(ScoringConfiguration)
            .where(ScoringConfiguration.business_profile_id == profile_id)
            .values(is_active=False)
        )

        # Crear nueva configuración
        config = ScoringConfiguration(
            business_profile_id=profile.id,
            population_weight=int(weights.get("population", 25)),
            income_weight=int(weights.get("income", 25)),
            education_weight=int(weights.get("education", 25)),
            competition_weight=int(weights.get("competition", 25)),
            additional_weights_json={
                k: v for k, v in weights.items()
                if k not in ["population", "income", "education", "competition"]
            }
        )
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(profile)

        await self.audit_client.log_event(
            event_type="profile_update_completed",
            reference_id=str(profile_id),
            user_id=user_id,
            username=username,
            trace_id=trace_id,
            details={"weights": weights}
        )

        return self._to_dto(profile, config)

    async def activate_profile(
            self,
            profile_id: int,
            user_id: Optional[int] = None,
            username: Optional[str] = None
    ) -> BusinessProfileData:
        trace_id = str(uuid.uuid4())

        await self.audit_client.log_event(
            event_type="profile_activate_started",
            reference_id=str(profile_id),
            user_id=user_id,
            username=username,
            trace_id=trace_id
        )

        await self.db.execute(update(BusinessProfile).values(is_active=False))

        profile = await self.db.get(BusinessProfile, profile_id)
        if not profile:
            raise ProfileNotFoundError(profile_id)

        profile.is_active = True
        await self.db.commit()
        await self.db.refresh(profile)

        config = await self._get_active_config(profile.id)

        await self.audit_client.log_event(
            event_type="profile_activate_completed",
            reference_id=str(profile_id),
            user_id=user_id,
            username=username,
            trace_id=trace_id,
            details={"profile_name": profile.name}
        )

        return self._to_dto(profile, config) if config else None

    async def get_active_weights(self) -> Dict[str, float]:
        profile = await self.get_active_profile()
        if not profile:
            return {"population": 25, "income": 25, "education": 25, "competition": 25}
        return profile.weights

    async def _get_active_config(self, profile_id: int) -> Optional[ScoringConfiguration]:
        stmt = select(ScoringConfiguration).where(
            ScoringConfiguration.business_profile_id == profile_id,
            ScoringConfiguration.is_active == True
        ).order_by(ScoringConfiguration.created_at.desc()).limit(1)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_profile(
            self,
            profile_id: int,
            user_id: Optional[int] = None,
            username: Optional[str] = None
    ) -> bool:
        """Elimina un perfil y sus configuraciones."""
        trace_id = str(uuid.uuid4())

        profile = await self.db.get(BusinessProfile, profile_id)
        if not profile:
            raise ProfileNotFoundError(profile_id)

        profile_name = profile.name

        await self.audit_client.log_event(
            event_type="profile_delete_started",
            reference_id=str(profile_id),
            user_id=user_id,
            username=username,
            trace_id=trace_id,
            details={"profile_name": profile_name}
        )

        # Eliminar configuraciones asociadas
        await self.db.execute(
            delete(ScoringConfiguration).where(
                ScoringConfiguration.business_profile_id == profile_id
            )
        )

        # Eliminar perfil
        await self.db.delete(profile)
        await self.db.commit()

        await self.audit_client.log_event(
            event_type="profile_delete_completed",
            reference_id=str(profile_id),
            user_id=user_id,
            username=username,
            trace_id=trace_id,
            details={"profile_name": profile_name}
        )

        return True

    def _to_dto(self, profile: BusinessProfile, config: ScoringConfiguration) -> BusinessProfileData:
        weights = {
            "population": float(config.population_weight),
            "income": float(config.income_weight),
            "education": float(config.education_weight),
            "competition": float(config.competition_weight)
        }
        if config.additional_weights_json:
            weights.update(config.additional_weights_json)

        return BusinessProfileData(
            id=profile.id,
            name=profile.name,
            description=profile.description or "",
            target_business_type=profile.target_business_type,
            is_active=profile.is_active,
            weights=weights,
            created_at=profile.created_at.isoformat() if profile.created_at else None
        )