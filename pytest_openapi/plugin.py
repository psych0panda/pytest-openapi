import json
import yaml
import dotenv
import pytest
import requests
import responses
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def pytest_addoption(parser):
    parser.addoption("--openapi-spec", action="store", help="Path to the OpenAPI spec file")

def upload_fixture(file_path):
    # with open(file_path, 'r') as f:
    #     data = yaml.safe_load(f)
    # return data
    pass

@pytest.fixture
def path_parameters(yaml_fixture):
    # if yaml_fixture:
    #     logger.debug(f"Upload yaml fixture: {yaml_fixture}")
    #     fixture = upload_fixture(yaml_fixture)
    # else:
    #     logger.debug(f"Upload local .env fixture")
    #     fixture = dotenv.dotenv_values(".env")
    # return fixture
    logger.debug(f"Upload local .env fixture")
    fixture = dotenv.dotenv_values(".env")
    return fixture
    

def pytest_generate_tests(metafunc):
    if 'openapi_test' in metafunc.fixturenames:
        with open(metafunc.config.option.openapi_spec) as f:
            spec = json.load(f)
        tests = []
        for path, path_item in spec['paths'].items():
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete', 'patch']:
                    tests.append((method, path))
        metafunc.parametrize("openapi_test", tests)

@responses.activate
def test_openapi(openapi_test, path_parameters):
    method, path, parameters = openapi_test
    responses.add(
        getattr(responses, method.upper()),
        f'http://localhost:8000{path}',
        json={},
        status=200
    )
    url = f'http://localhost:8000{path}'
    for parameter in parameters:
        url = url.replace(f'{{{parameter}}}', path_parameters[parameter])
    response = getattr(requests, method)(url)
    assert response.status_code == 200


