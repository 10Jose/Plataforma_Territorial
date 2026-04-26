from typing import List, Dict, Optional
from app.domain.interfaces import IScoringCalculator, IScoringFormula, IOpportunityClassifier
from app.services.scoring.formula import WeightedScoreFormula
from app.services.scoring.classifier import ThresholdClassifier


class ScoringCalculator(IScoringCalculator):

    def __init__(
            self,
            formula: Optional[IScoringFormula] = None,
            classifier: Optional[IOpportunityClassifier] = None
    ):
        self.formula = formula or WeightedScoreFormula()
        self.classifier = classifier or ThresholdClassifier()

    async def calculate(
            self,
            scaled_data: List,
            weights: Dict[str, float]
    ) -> List[Dict]:
        """Calcula scores para todas las zonas."""
        scores = []

        for zone in scaled_data:
            result = self.formula.calculate(
                population=zone.population_scaled,
                income=zone.income_scaled,
                education=zone.education_scaled,
                competition=zone.competition_scaled,
                weights=weights
            )

            scores.append({
                "zone_code": zone.zone_code,
                "zone_name": zone.zone_name,
                "score_value": result["score"],
                "population_contribution": result["population_contribution"],
                "income_contribution": result["income_contribution"],
                "education_contribution": result["education_contribution"],
                "competition_penalty": result["competition_penalty"],
                "opportunity_level": self.classifier.classify(result["score"])
            })

        return scores