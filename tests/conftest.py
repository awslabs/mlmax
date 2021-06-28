# -*- coding: utf-8 -*-
import pytest

def pytest_addoption(parser):
    parser.addoption('--smlocal', action='store_true', dest="smlocal",
                 default=False, help="enable local SageMaker environment tests")
    parser.addoption(
        "--inspectlocal", action="store_true",
        default=None, help="run local SageMaker environment tests in inspect (python -i) mode"
    )


@pytest.fixture
def inspectlocal(request):
    return request.config.getoption("--inspectlocal")


def pytest_configure(config):
    config.addinivalue_line("markers", "smlocal: runs in local SageMaker Docker environment")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--smlocal"):
        # --smlocal given in cli: run MLMax scripts in local SageMaker environment
        return
    skip_local = pytest.mark.skip(reason="need --smlocal option to run")
    for item in items:
        if "smlocal" in item.keywords:
            item.add_marker(skip_local)


@pytest.fixture
def cmdopt(request):
    return request.config.getoption("--cmdopt")
