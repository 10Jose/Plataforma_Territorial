from io import BytesIO
from typing import Dict, List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus.flowables import HRFlowable
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, func
from app.services.comparison.comparator import ZoneComparator
import logging
import httpx
import uuid
from app.domain.interfaces import (
    IScoringCalculator,
    IScoringRepository,
    IScoringFormula,
    IOpportunityClassifier,
    ComparisonResult
)
from app.services.configuration_client import ConfigurationClient
from app.services.scoring.calculator import ScoringCalculator
from app.services.scoring.repository import ScoringRepository
from app.services.analytics_service import AnalyticsService
from app.services.audit_client import AuditClient
from app.domain.models import IndicatorResult, ZoneScore

from app.core.exceptions import NoDataError

logger = logging.getLogger(__name__)


class ScoringService:

    def __init__(
            self,
            db: AsyncSession,
            calculator: Optional[IScoringCalculator] = None,
            repository: Optional[IScoringRepository] = None,
            config_client: Optional[ConfigurationClient] = None,
            audit_client: Optional[AuditClient] = None
    ):
        self.db = db
        self.calculator = calculator or ScoringCalculator()
        self.repository = repository or ScoringRepository(db)
        self.config_client = config_client or ConfigurationClient()
        self.audit_client = audit_client or AuditClient("ms-analytics")

    async def _get_active_weights(self) -> Dict[str, float]:
        """Obtiene los pesos activos."""
        try:
            return await self.config_client.get_active_weights()
        except Exception as e:
            logger.warning(f"Error obteniendo pesos, usando defaults: {e}")
            return {"population": 25, "income": 25, "education": 25, "competition": 25}

    async def calculate_scores(
            self,
            user_id: Optional[int] = None,
            username: Optional[str] = None
    ) -> Dict:
        """Calcula el scoring para todas las zonas."""
        trace_id = str(uuid.uuid4())

        await self.audit_client.log_event(
            event_type="scoring_calculate_started",
            user_id=user_id,
            username=username,
            trace_id=trace_id
        )

        try:
            # Verificar si hay datos reescalados
            scaled_data = await self.repository.get_scaled_data()
            stmt = select(func.count()).select_from(IndicatorResult)
            result = await self.db.execute(stmt)
            indicator_count = result.scalar() or 0
            scaled_count = len(scaled_data) if scaled_data else 0

            if indicator_count > scaled_count:
                logger.info(f"Hay {indicator_count} indicadores pero solo {scaled_count} reescalados. Ejecutando scaling...")
                scaled_data = None

            # Si no hay datos reescalados, ejecutar scaling automáticamente
            if not scaled_data:
                logger.info("No hay datos reescalados. Ejecutando scaling automático...")

                await self.audit_client.log_event(
                    event_type="scaling_auto_triggered",
                    user_id=user_id,
                    username=username,
                    trace_id=trace_id,
                    details={"reason": "no_scaled_data"}
                )

                stmt = select(IndicatorResult).limit(1)
                result = await self.db.execute(stmt)
                has_indicators = result.scalar_one_or_none() is not None

                if not has_indicators:
                    await self.repository.clear_all()
                    raise NoDataError("No hay indicadores calculados. Ejecuta primero el cálculo de indicadores.")

                analytics_service = AnalyticsService(self.db)

                try:
                    scaling_result = await analytics_service.run_scaling()
                    logger.info(f"Scaling completado: {scaling_result['zones_processed']} zonas procesadas")
                except Exception as e:
                    logger.error(f"Error en scaling automático: {e}")
                    await self.repository.clear_all()
                    raise NoDataError(f"Error al ejecutar scaling: {str(e)}")

                # Obtener datos reescalados después del scaling
                scaled_data = await self.repository.get_scaled_data()

                if not scaled_data:
                    await self.repository.clear_all()
                    raise NoDataError("No se pudieron obtener datos reescalados después del scaling")

            await self.db.execute(delete(ZoneScore))
            await self.db.commit()
            logger.info("Scores anteriores eliminados")

            # Obtener pesos
            weights = await self._get_active_weights()

            await self.audit_client.log_event(
                event_type="weights_loaded",
                user_id=user_id,
                username=username,
                trace_id=trace_id,
                details={"weights": weights}
            )

            # Crear ejecución
            execution_id = await self.repository.save_execution({
                "weights": weights,
                "formula_version": "1.0.0"
            })

            # Calcular scores
            scores = await self.calculator.calculate(scaled_data, weights)

            # Guardar scores
            saved_count = await self.repository.save_scores(execution_id, scores)

            # Actualizar estado
            await self.repository.update_execution_status(execution_id, "completed")

            await self.audit_client.log_event(
                event_type="scoring_calculate_completed",
                reference_id=str(execution_id),
                user_id=user_id,
                username=username,
                trace_id=trace_id,
                details={
                    "zones_processed": saved_count,
                    "execution_id": execution_id
                }
            )

            #ENTRENAR MODELO ML
            await self._auto_train_ml_model()

            return {
                "status": "completed",
                "execution_id": execution_id,
                "zones_processed": saved_count,
                "weights_used": weights,
                "scaling_executed": scaled_data is None,
                "trace_id": trace_id
            }

        except Exception as e:
            await self.audit_client.log_event(
                event_type="scoring_calculate_failed",
                user_id=user_id,
                username=username,
                trace_id=trace_id,
                status="error",
                details={"error": str(e)}
            )
            if 'execution_id' in locals():
                await self.repository.update_execution_status(execution_id, "failed")
            raise e

    async def _auto_train_ml_model(self):
        """Entrena el modelo ML automáticamente después del scoring."""
        try:
            import httpx
            ml_url = "http://ms-ml:8000"
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{ml_url}/ml/train",
                    json={"algorithm": "random_forest"}
                )
                if response.status_code == 200:
                    logger.info("✅ Modelo ML reentrenado automáticamente después del scoring")
                else:
                    logger.warning(f"⚠️ Entrenamiento ML respondió con {response.status_code}")
        except httpx.ConnectError:
            logger.warning("⚠️ No se pudo conectar con ms-ml para reentrenar el modelo")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo reentrenar el modelo ML: {e}")
    async def get_scores(self, zone_code: Optional[str] = None) -> List[Dict]:
        """Obtiene los scores calculados."""
        execution = await self.repository.get_latest_execution()
        if not execution:
            return []

        scores = await self.repository.get_scores(execution["id"], zone_code)

        for score in scores:
            score["weights_used"] = execution["weights"]
            if score.get("calculated_at"):
                score["calculated_at"] = score["calculated_at"].isoformat()

        return scores

    async def get_score_details(self, zone_code: str) -> Optional[Dict]:
        """Obtiene el detalle del score de una zona."""
        scores = await self.get_scores(zone_code)
        return scores[0] if scores else None

    async def get_ranking(self, limit: Optional[int] = None, opportunity_level: Optional[str] = None) -> List[Dict]:
        """Obtiene el ranking de zonas ordenado por score."""
        execution = await self.repository.get_latest_execution()
        if not execution:
            return []

        scores = await self.repository.get_scores(execution["id"])

        if opportunity_level:
            scores = [s for s in scores if s.get("opportunity_level") == opportunity_level]

        if limit:
            scores = scores[:limit]

        for idx, score in enumerate(scores):
            score["rank_position"] = idx + 1
            score["weights_used"] = execution["weights"]
            if score.get("calculated_at"):
                score["calculated_at"] = score["calculated_at"].isoformat()

        return scores

    async def compare_zones(self, zone_codes: List[str]) -> ComparisonResult:
        """Compara múltiples zonas."""
        comparator = ZoneComparator(self.db)
        return await comparator.compare(zone_codes)

    async def generate_recommendations(self, zone_code: str) -> Dict:
        """Genera recomendaciones basadas en el análisis de la zona."""

        # 1. Obtener score real
        score_data = await self.get_score_details(zone_code)
        if not score_data:
            raise HTTPException(404, detail=f"Zona {zone_code} no encontrada")

        # 2. Obtener predicción ML (si existe)
        prediction_data = None
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"http://ms-ml:8000/ml/predictions",
                    params={"zone_code": zone_code}
                )
                if response.status_code == 200:
                    predictions = response.json()
                    if predictions:
                        prediction_data = predictions[0]
        except Exception:
            pass

        # 3. Analizar fortalezas, debilidades y oportunidades
        contributions = score_data.get("contributions", {})
        score_real = score_data.get("score", 0)
        opportunity_level = score_data.get("opportunity_level", "Baja")

        strengths = []
        weaknesses = []
        opportunities = []
        risks = []

        # Analizar contribuciones
        pop_contrib = contributions.get("population", 0)
        inc_contrib = contributions.get("income", 0)
        edu_contrib = contributions.get("education", 0)
        comp_penalty = contributions.get("competition_penalty", 0)
        #Fortalezas
        if pop_contrib >= 15:
            strengths.append(f"🏘️ Alta densidad poblacional (+{pop_contrib} puntos)")
        if inc_contrib >= 15:
            strengths.append(f"💰 Alto nivel de ingresos (+{inc_contrib} puntos)")
        if edu_contrib >= 15:
            strengths.append(f"🎓 Alto nivel educativo (+{edu_contrib} puntos)")

        # Debilidades
        if pop_contrib < 5:
            weaknesses.append(f"🏘️ Baja densidad poblacional (+{pop_contrib} puntos)")
        if inc_contrib < 5:
            weaknesses.append(f"💰 Bajo nivel de ingresos (+{inc_contrib} puntos)")
        if edu_contrib < 5:
            weaknesses.append(f"🎓 Bajo nivel educativo (+{edu_contrib} puntos)")
        if comp_penalty > 10:
            weaknesses.append(f"🏪 Alta competencia (-{comp_penalty} puntos)")

        # Si no hay fortalezas ni debilidades específicas, agregar mensajes genérico
        if not strengths:
            strengths.append("📊 Indicadores equilibrados sin fortalezas destacables")
        if not weaknesses:
            weaknesses.append("✅ Sin debilidades significativas detectadas")

        # Oportunidades basadas en predicción ML
        if prediction_data:
            predicted = prediction_data.get("prediction_value", 0)
            diff = predicted - score_real

            if diff > 10:
                opportunities.append(f"🚀 El modelo ML predice un potencial de {predicted:.1f} (+{diff:.1f} vs score actual)")
            elif diff > 0:
                opportunities.append(f"📈 El modelo ML sugiere potencial de mejora leve (+{diff:.1f})")

            if predicted >= 70:
                opportunities.append("🌟 Zona con alto potencial de crecimiento según IA")
        else:
            opportunities.append("🔮 Genera predicciones ML para descubrir oportunidades ocultas")

        # Riesgos
        if score_real < 30:
            risks.append("⚠️ Score bajo: requiere análisis detallado antes de invertir")
        if comp_penalty > 15:
            risks.append("⚠️ Competencia elevada: riesgo de saturación del mercado")
        if prediction_data:
            predicted = prediction_data.get("prediction_value", 0)
        if predicted < score_real - 10:
            risks.append(f"📉 El modelo ML predice un desempeño inferior al actual (-{abs(score_real - predicted):.1f})")

        if not risks:
            risks.append("✅ No se detectaron riesgos significativos")

        # 4. Recomendación final
        if opportunity_level == "Alta":
            recommendation = "✅ ZONA RECOMENDADA: Alto potencial de oportunidad. Se sugiere inversión prioritaria."
        elif opportunity_level == "Media":
            if prediction_data and prediction_data.get("prediction_value", 0) > score_real + 5:
                recommendation = "🔍 ZONA A EVALUAR: Potencial medio pero con proyección de mejora según IA. Se sugiere análisis complementario."
            else:
                recommendation = "📋 ZONA A CONSIDERAR: Potencial medio. Se sugiere evaluar junto con otras zonas comparables."
        else:
            if prediction_data and prediction_data.get("prediction_value", 0) > score_real + 10:
                recommendation = "⚠️ ZONA DE RIESGO CON OPORTUNIDAD: Score bajo pero el ML detecta potencial oculto. Requiere validación adicional."
            else:
                recommendation = "❌ ZONA NO RECOMENDADA: Bajo potencial de oportunidad. Se sugiere buscar alternativas."

        return {
            "zone_code": zone_code,
            "zone_name": score_data.get("zone_name", ""),
            "score_real": score_real,
            "opportunity_level": opportunity_level,
            "prediction_ml": prediction_data.get("prediction_value") if prediction_data else None,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "opportunities": opportunities,
            "risks": risks,
            "recommendation": recommendation
        }

    async def generate_recommendations_pdf(self, zone_code: str) -> bytes:
        """Genera un PDF con las recomendaciones de la zona."""
    # 1. Obtener recomendaciones
        recommendations = await self.generate_recommendations(zone_code)

    # 2. Crear PDF en memoria
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20*mm,
            leftMargin=20*mm,
            topMargin=15*mm,
            bottomMargin=15*mm
        )
        styles = getSampleStyleSheet()
        # Estilos personalizados
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=HexColor('#006944'),
            spaceAfter=5*mm,
            alignment=1
        )

        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor('#64748b'),
            spaceAfter=10*mm,
            alignment=1
        )

        zone_style = ParagraphStyle(
            'ZoneName',
            parent=styles['Heading1'],
            fontSize=22,
            textColor=HexColor('#1e293b'),
            spaceAfter=3*mm
        )

        score_style = ParagraphStyle(
            'Score',
            parent=styles['Normal'],
            fontSize=16,
            textColor=HexColor('#006944'),
            spaceAfter=2*mm
        )

        section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#ffffff'),
            spaceAfter=2*mm
        )

        item_style = ParagraphStyle(
            'Item',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor('#334155'),
            spaceAfter=2*mm,
            leftIndent=5*mm
        )

        recommendation_style = ParagraphStyle(
            'Recommendation',
            parent=styles['Normal'],
            fontSize=12,
            textColor=HexColor('#ffffff'),
            alignment=1
        )

        # Construir contenido
        elements = []

        # Título
        elements.append(Paragraph("GUÍA DE ACCIÓN", title_style))
        elements.append(Paragraph("Plataforma de Analítica Territorial", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=HexColor('#006944')))
        elements.append(Spacer(1, 8*mm))

        # Zona y Score
        elements.append(Paragraph(recommendations['zone_name'], zone_style))
        elements.append(Paragraph(
            f"Score: {recommendations['score_real']:.1f} / 100 | Nivel de Potencial: {recommendations['opportunity_level']}",
            score_style
        ))
        elements.append(Spacer(1, 8*mm))

        # Recomendación Principal (fondo verde)
        rec_data = [[Paragraph(recommendations['recommendation'], recommendation_style)]]
        rec_table = Table(rec_data, colWidths=[doc.width])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), HexColor('#006944')),
            ('TOPPADDING', (0, 0), (-1, -1), 12*mm),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12*mm),
            ('LEFTPADDING', (0, 0), (-1, -1), 8*mm),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8*mm),
        ]))
        elements.append(rec_table)
        elements.append(Spacer(1, 10*mm))

        # Función para crear sección
        def add_section(title, items, bg_color):
            section_data = []
            for item in items:
                clean_item = item.replace('🏘️', '').replace('💰', '').replace('🎓', '').replace('🏪', '').replace('📊', '').replace('🚀', '').replace('📈', '').replace('🌟', '').replace('🔮', '').replace('⚠️', '').replace('📉', '').replace('✅', '').replace('🔴', '').replace('❌', '').strip()
                section_data.append([Paragraph(f"• {clean_item}", item_style)])

            if section_data:
                table = Table(section_data, colWidths=[doc.width])
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), HexColor('#f8fafc')),
                    ('TOPPADDING', (0, 0), (-1, -1), 3*mm),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 3*mm),
                    ('LEFTPADDING', (0, 0), (-1, -1), 4*mm),
                ]))
                elements.append(table)

            elements.append(Spacer(1, 6*mm))

        # Secciones
        elements.append(Paragraph("FORTALEZAS", section_title_style))
        elements.append(Spacer(1, 2*mm))
        add_section('FORTALEZAS', recommendations.get('strengths', []), '#10b981')

        elements.append(Paragraph("DEBILIDADES", section_title_style))
        elements.append(Spacer(1, 2*mm))
        add_section('DEBILIDADES', recommendations.get('weaknesses', []), '#f59e0b')

        elements.append(Paragraph("OPORTUNIDADES", section_title_style))
        elements.append(Spacer(1, 2*mm))
        add_section('OPORTUNIDADES', recommendations.get('opportunities', []), '#3b82f6')

        elements.append(Paragraph("RIESGOS", section_title_style))
        elements.append(Spacer(1, 2*mm))
        add_section('RIESGOS', recommendations.get('risks', []), '#ef4444')

        elements.append(Spacer(1, 10*mm))
        elements.append(HRFlowable(width="100%", thickness=1, color=HexColor('#e2e8f0')))
        elements.append(Spacer(1, 5*mm))

        # Datos adicionales
        pred_text = f"Predicción ML: {recommendations['prediction_ml']:.1f}" if recommendations.get('prediction_ml') else "Predicción ML: No disponible"
        elements.append(Paragraph(
            f"{pred_text} | Generado el {__import__('datetime').datetime.now().strftime('%d de %B de %Y')}",
            subtitle_style
        ))

        # Construir PDF
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes