from typing import Dict
from app.domain.interfaces import IScoringFormula


class WeightedScoreFormula(IScoringFormula):

    def get_name(self) -> str:
        return "Weighted Score Formula"

    def get_description(self) -> str:
        return "Score = w1*pop + w2*inc + w3*edu - w4*comp"

    def calculate(
            self,
            population: float,
            income: float,
            education: float,
            competition: float,
            weights: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calcula el score usando fórmula ponderada.
        """
        w_pop = weights.get("population", 25) / 100
        w_inc = weights.get("income", 25) / 100
        w_edu = weights.get("education", 25) / 100
        w_comp = weights.get("competition", 25) / 100

        # Contribuciones normalizadas (0-1)
        pop_contrib = population * w_pop
        inc_contrib = income * w_inc
        edu_contrib = education * w_edu
        comp_penalty = competition * w_comp

        # Score bruto (0-1)
        raw_score = pop_contrib + inc_contrib + edu_contrib - comp_penalty

        # Convertir a 0-100 y limitar
        final_score = max(0.0, min(100.0, raw_score * 100))

        return {
            "score": round(final_score, 2),
            "population_contribution": round(pop_contrib * 100, 2),
            "income_contribution": round(inc_contrib * 100, 2),
            "education_contribution": round(edu_contrib * 100, 2),
            "competition_penalty": round(comp_penalty * 100, 2)
        }


class BalancedScoreFormula(IScoringFormula):
    """Fórmula alternativa con pesos balanceados y menor penalización."""

    def get_name(self) -> str:
        return "Balanced Score Formula"

    def get_description(self) -> str:
        return "Score con penalización reducida (50% de competencia)"

    def calculate(
            self,
            population: float,
            income: float,
            education: float,
            competition: float,
            weights: Dict[str, float]
    ) -> Dict[str, float]:
        w_pop = weights.get("population", 25) / 100
        w_inc = weights.get("income", 25) / 100
        w_edu = weights.get("education", 25) / 100
        w_comp = weights.get("competition", 25) / 100

        pop_contrib = population * w_pop
        inc_contrib = income * w_inc
        edu_contrib = education * w_edu
        comp_penalty = competition * w_comp * 0.5  # Penalización reducida

        raw_score = pop_contrib + inc_contrib + edu_contrib - comp_penalty
        final_score = max(0.0, min(100.0, raw_score * 100))

        return {
            "score": round(final_score, 2),
            "population_contribution": round(pop_contrib * 100, 2),
            "income_contribution": round(inc_contrib * 100, 2),
            "education_contribution": round(edu_contrib * 100, 2),
            "competition_penalty": round(comp_penalty * 100, 2)
        }