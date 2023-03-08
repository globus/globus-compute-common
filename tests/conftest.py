import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--compute-s3-bucket",
        default=None,
        nargs=1,
        help="A live S3 bucket which will be used for testing. "
        "AWS credentials must be present in the environment or local configuration "
        "in order for this to work. They will be loaded via a simple "
        "boto3 client instantiation",
    )


@pytest.fixture
def compute_s3_bucket(pytestconfig, monkeypatch):
    value = pytestconfig.getoption("--compute-s3-bucket")

    if value is not None:
        value = value[0]
        monkeypatch.setenv("COMPUTE_S3_BUCKET_NAME", value)
        return value

    return None


@pytest.fixture(autouse=True)
def _unset_envvar_if_set(monkeypatch):
    # use monkeypatch.delenv to ensure that the env var is not set, preventing
    # test behaviors from changing
    # TODO: allow use of the redis URL env var to control test behavior
    monkeypatch.delenv("COMPUTE_COMMON_REDIS_URL", raising=False)
