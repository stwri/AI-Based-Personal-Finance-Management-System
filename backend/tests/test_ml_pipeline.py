import pytest
from backend.ml_pipeline import ModelManager
from backend.app import create_app


def test_model_training(tmp_path):
    app = create_app()
    mm = ModelManager()
    mm.train_initial()
    cat = mm.predict_category('Bought coffee at Starbucks')
    assert isinstance(cat, str)
