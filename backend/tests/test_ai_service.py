import pytest
from app.models.match import AIPrediction
from app.services.football_api import get_match_detail
from app.services.ai_service import get_prediction, _mock_prediction


def test_mock_prediction_returns_valid_prediction():
    detail = get_match_detail(1)
    pred = _mock_prediction(detail.match)
    assert isinstance(pred, AIPrediction)
    assert 0 <= pred.confidence_percentage <= 100
    assert len(pred.key_factors) == 3
    assert pred.value_bet.target_odds > 1.0


@pytest.mark.asyncio
async def test_get_prediction_without_api_key_uses_mock(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "anthropic_api_key", "")
    detail = get_match_detail(1)
    pred = await get_prediction(
        detail.match, detail.home_form, detail.away_form, detail.h2h, detail.odds_comparison
    )
    assert isinstance(pred, AIPrediction)


@pytest.mark.asyncio
async def test_prediction_score_is_non_negative(monkeypatch):
    from app.core import config
    monkeypatch.setattr(config.settings, "anthropic_api_key", "")
    detail = get_match_detail(1)
    pred = await get_prediction(
        detail.match, detail.home_form, detail.away_form, detail.h2h, detail.odds_comparison
    )
    assert pred.projected_score.home_goals >= 0
    assert pred.projected_score.away_goals >= 0
