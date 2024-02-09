import json
import pytest
import requests
import responses
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def pytest_addoption(parser):
    parser.addoption("--openapi-spec", action="store", help="Path to the OpenAPI spec file")


def upload_fixture(file_path=None):
    return {
        ('get', '/gcs/head/{bucket_name}/{focus_object}'): '/gcs/head/devlocalbucket/kiwi.png',
        ('get', '/gcs/download/{bucket_name}/{source_file_name}/{destination_file_name}'): '/gcs/download/devlocalbucket/kiwi.png/kiwi.png',
        ('put', '/gcs/upload/{bucket_name}/{source_file_name}/{destination_file_name}'): '/gcs/upload/devlocalbucket/kiwi.png/kiwi.png',
        ('get', '/gcs/buckets/{project_id}'): '/gcs/buckets/titanium-arc-327213',
        ('delete', '/gcs/{bucket_name}'): '/gcs/devlocalbucket',
        ('put', '/gcs/{bucket_name}'): '/gcs/devlocalbucket',
        ('get', '/aws/head/{bucket_name}/{focus_object}'): '/aws/head/devlocalbucket/kiwi.png',
        ('get', '/aws/download/{bucket_name}/{source_file_name}/{destination_file_name}'): '/aws/download/devlocalbucket/kiwi.png/kiwi.png',
        ('put', '/aws/upload/{bucket_name}/{source_file_name}/{destination_file_name}'): '/aws/upload/devlocalbucket/kiwi.png/kiwi.png',
        ('get', '/aws/buckets/{project_id}'): '/aws/buckets/titanium-arc-327213',
        ('delete', '/aws/{bucket_name}'): '/aws/devlocalbucket',
        ('put', '/aws/{bucket_name}'): '/aws/devlocalbucket',
    }


@pytest.fixture
def path_parameters(yaml_fixture):
    logger.debug(f"Upload yaml fixture: {yaml_fixture}")
    fixture = upload_fixture(yaml_fixture)
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


def update_path(openapi_test: tuple):
    method, path = openapi_test
    path = upload_fixture().get(openapi_test, 'ATTENTION: Path not found!')
    return method, path


@responses.activate
def test_openapi(openapi_test: tuple):
    method, path = update_path(openapi_test)
    responses.add(
        getattr(responses, method.upper()),
        f'http://localhost:8000{path}',
        json={},
        status=200
    )
    url = f'http://localhost:8000{path}'
    response = getattr(requests, method)(url)
    assert response.status_code == 200
