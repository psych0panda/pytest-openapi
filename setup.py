from setuptools import setup, find_packages

setup(
    name='pytest-openapi',
    version='0.1.1',
    packages=find_packages(),
    entry_points={
        'pytest11': [
            'openapi = pytest_openapi.plugin',
        ],
    },
    install_requires=[
        'pytest',
        'requests',
        'responses',
    ],
)
