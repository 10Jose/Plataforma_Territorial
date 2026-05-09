from app.services.model_trainer import RandomForestTrainer, LinearRegressionTrainer


def get_trainer(algorithm: str = "random_forest"):
    if algorithm == "linear_regression":
        return LinearRegressionTrainer()
    return RandomForestTrainer()