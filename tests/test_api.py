"""API acceptance against the real saved pipeline and strict request contract."""
import numpy as np
import pandas as pd
import pytest
from app.messages import COPY
from app.schemas import CheckIn
from ml.config import FEATURES


FIELDS = [q['key'] for q in COPY['questions']]


def test_health_and_configuration(client):
    assert client.get('/health').json() == {'status': 'ok', 'model_loaded': True}
    config = client.get('/api/config')
    assert config.status_code == 200
    assert set(config.json()) == {'copy', 'faculty_groups', 'support_contacts'}
    assert len(config.json()['copy']['questions']) == 9
    assert all(item['verified_on'] is None and item['source'] for item in config.json()['support_contacts']['items'])
    page = client.get('/')
    assert page.status_code == 200
    assert COPY['welcome']['title'] not in page.text  # loaded by the buildless JS
    assert '__APP_TITLE__' not in page.text
    assert '__ASSET_VERSION__' not in page.text
    assert COPY['app_title'] in page.text


def test_versioned_assets_and_config_use_one_public_build_fingerprint(client):
    from app.main import ASSET_VERSION
    page = client.get('/')
    assert f'data-asset-version="{ASSET_VERSION}"' in page.text
    assert f'/static/js/app.js?v={ASSET_VERSION}' in page.text
    assert f'/static/css/styles.css?v={ASSET_VERSION}' in page.text
    asset = client.get(f'/static/js/app.js?v={ASSET_VERSION}')
    assert asset.status_code == 200
    assert asset.headers['cache-control'] == 'no-cache'
    assert client.get(f'/api/config?v={ASSET_VERSION}').json() == client.get('/api/config').json()


def test_valid_response_and_determinism(client, valid_answers):
    first = client.post('/predict', json=valid_answers)
    assert first.status_code == 200
    body = first.json()
    assert set(body) == {'category', 'label', 'title', 'message', 'disclaimer', 'out_of_range_notes', 'model_note'}
    assert body['category'] in {'lower', 'higher'}
    assert body['disclaimer'] == COPY['disclaimer']
    assert first.json() == client.post('/predict', json=valid_answers).json()
    assert body['out_of_range_notes'] == []


@pytest.mark.parametrize('field', FIELDS)
def test_every_missing_field(client, valid_answers, field):
    del valid_answers[field]
    response = client.post('/predict', json=valid_answers)
    assert response.status_code == 422
    assert response.json()['detail'][0]['field'] == field
    assert response.json()['detail'][0]['message']


@pytest.mark.parametrize('field,value', [
    ('gender','other'), ('gender',1), ('age',15), ('age',61), ('age',21.5),
    ('age','21'), ('age',True), ('faculty_group','Unknown'), ('faculty_group',None),
    ('year',0), ('year',5), ('year','2'), ('year',True), ('cgpa_band','3.00 - 3.49'),
    ('married','false'), ('married',0), ('anxiety','yes'), ('anxiety',1),
    ('panic','no'), ('panic',0), ('specialist','true'), ('specialist',1),
    *[(field,None) for field in FIELDS if field != 'faculty_group']])
def test_invalid_fields_are_rejected(client, valid_answers, field, value):
    valid_answers[field] = value
    response = client.post('/predict', json=valid_answers)
    assert response.status_code == 422
    assert response.json()['detail'][0]['field'] == field


@pytest.mark.parametrize('age,status,noted', [(15,422,False),(16,200,True),(18,200,False),
                                            (24,200,False),(60,200,True),(61,422,False)])
def test_age_boundaries(client, valid_answers, age, status, noted):
    response = client.post('/predict', json={**valid_answers,'age':age})
    assert response.status_code == status
    if status == 200:
        assert bool(response.json()['out_of_range_notes']) == noted


def test_year_four_disclosure(client, valid_answers):
    response = client.post('/predict', json={**valid_answers,'year':4})
    assert response.json()['out_of_range_notes'] == [COPY['out_of_range']['year']]


def test_inference_matches_training_feature_conventions(client, valid_answers):
    predictor = client.app.state.predictor
    # Law is offered in the UI and was merged into Other by the fitted training pipeline.
    answers = CheckIn(**{**valid_answers, 'faculty_group':'Law'})
    prepared = predictor.features(answers)
    assert list(prepared) == FEATURES
    assert prepared.iloc[0].to_dict() == dict(zip(FEATURES,[0,21,'Other',2,3,0,1,0,0]))
    unmerged = pd.DataFrame([[0,21,'Law',2,3,0,1,0,0]],columns=FEATURES)
    np.testing.assert_allclose(predictor.model.predict_proba(unmerged),predictor.model.predict_proba(prepared))


@pytest.mark.parametrize('probability,category', [(0.499,'lower'),(0.5,'higher'),(0.501,'higher')])
def test_fixed_probability_threshold(client, valid_answers, monkeypatch, probability, category):
    # Test only the decision boundary; real-artifact prediction is checked separately.
    monkeypatch.setattr(client.app.state.predictor.model,'predict_proba',lambda _:np.array([[1-probability,probability]]))
    assert client.post('/predict',json=valid_answers).json()['category'] == category


def test_model_loaded_only_once_per_lifespan(valid_answers, monkeypatch):
    import app.main as main
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    real = main.Predictor
    calls = []
    def load():
        calls.append(True)
        return real()
    monkeypatch.setattr(main,'Predictor',load)
    isolated = FastAPI(lifespan=main.lifespan)

    @isolated.post('/predict')
    def predict(answers: CheckIn):
        return isolated.state.predictor.predict(answers)

    with TestClient(isolated) as client:
        for _ in range(2):
            assert client.post('/predict',json=valid_answers).status_code == 200
        assert len(calls) == 1
    assert not hasattr(isolated.state,'predictor')
