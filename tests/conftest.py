import os

import pytest


@pytest.fixture
def data_dir(pytestconfig):
    return os.path.join(pytestconfig.rootdir, 'tests', 'data')
