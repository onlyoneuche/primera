"""No submitted values in errors/logs/files; same-origin, no-store responses."""
import logging
from pathlib import Path
import tempfile
import pytest
from app.main import SECURITY_HEADERS


@pytest.mark.parametrize('path', ['/', '/health', '/api/config', '/static/js/app.js', '/missing'])
def test_security_headers_and_no_cookies(client, path):
    response = client.get(path)
    assert 'set-cookie' not in response.headers
    assert 'access-control-allow-origin' not in response.headers
    for key, value in SECURITY_HEADERS.items():
        assert response.headers[key] == value


def test_predict_no_store_including_errors(client, valid_answers):
    for body,status in [(valid_answers,200),({},422),({**valid_answers,'unknown':'secret'},422)]:
        response = client.post('/predict',json=body)
        assert response.status_code == status
        assert response.headers['cache-control'] == 'no-store'
        assert 'set-cookie' not in response.headers
    response = client.post('/predict',content=b'{invalid',headers={'content-type':'application/json'})
    assert response.status_code == 422
    assert response.headers['cache-control'] == 'no-store'


def test_unknown_fields_and_input_values_never_echoed(client, valid_answers, caplog):
    marker = 'PRIVATE_SENTINEL_63ae8'
    with caplog.at_level(logging.DEBUG):
        for body in [{**valid_answers,'gender':marker},{**valid_answers,marker:marker}]:
            response = client.post('/predict',json=body)
            assert response.status_code == 422
            assert marker not in response.text
    assert marker not in caplog.text


def test_valid_prediction_does_not_log_answers(client, valid_answers, caplog):
    with caplog.at_level(logging.DEBUG):
        assert client.post('/predict',json=valid_answers).status_code == 200
    # httpx logs the route/status in this test harness, never submitted data.
    assert 'Health sciences' not in caplog.text
    assert 'female' not in caplog.text
    assert '3.00-3.49' not in caplog.text
    assert '21' not in caplog.text
    assert 'False' not in caplog.text
    assert 'True' not in caplog.text


def test_prediction_writes_no_working_or_temp_files(client, valid_answers, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(tempfile,'tempdir',str(tmp_path))
    # Observe both the configured working directory and actual process temp directory.
    roots = {Path.cwd(),Path('/tmp')}
    def snapshot():
        return {str(path):(path.stat().st_size,path.stat().st_mtime_ns)
                for root in roots for path in root.rglob('*') if path.is_file()}
    before = snapshot()
    assert client.post('/predict',json=valid_answers).status_code == 200
    assert snapshot() == before


def test_inference_exceptions_are_generic_and_not_logged(client, valid_answers, monkeypatch, caplog):
    marker = 'PRIVATE_INFERENCE_SENTINEL'
    def broken(_):
        raise ValueError(marker)
    monkeypatch.setattr(client.app.state.predictor,'predict',broken)
    with caplog.at_level(logging.DEBUG):
        response = client.post('/predict',json=valid_answers)
    assert response.status_code == 500
    assert marker not in response.text + caplog.text
    assert response.headers['cache-control'] == 'no-store'
    assert response.headers['content-security-policy'] == SECURITY_HEADERS['Content-Security-Policy']


def test_browser_assets_do_not_use_storage_or_third_party_requests():
    root = Path(__file__).resolve().parents[1]
    script = (root/'app/static/js/app.js').read_text()
    for forbidden in ['localStorage','sessionStorage','indexedDB','document.cookie','console.log','sendBeacon']:
        assert forbidden not in script
    assert 'https://' not in script and 'http://' not in script
    dockerfile=(root/'Dockerfile').read_text()
    assert '--no-access-log' in dockerfile
