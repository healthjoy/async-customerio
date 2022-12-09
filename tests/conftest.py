import pytest
from faker import Faker


@pytest.fixture()
def faker_():
    return Faker()
