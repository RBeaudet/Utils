import pytest
from typing import Any, Dict
import os

# === SIMPLE TEST ===

def test_simple() -> None:
    """Simplest form of unit test.
    """
    assert int('5') == 5


def test_simple_exception() -> None:
    """Ensure that an exception was raised.
    """
    with pytest.raises(ValueError):
        int('Hello World!')


# === FIXTURES ===

@pytest.fixture(scope='function')
def fixture_env() -> None:
    """Fixture are used to setup tests. They can execute code before a test is ran and after it finishes.
    It can also be used to build objects required by unit tests?
    A fixture can be reused by multiple tests.

    This fixture sets up an environment variable before the test runs.
    Then, once it finishes, it cleans up the environment.
    Since we have explicitely set the scope of this fixture to 'function', the cleanup part will run after every test.
    """

    # Set an environment variable
    os.environ['KEY'] = 'Hello'
    yield  # Test runs now
    # Tear down (cleanup, sort of)
    del os.environ['KEY']  # Delete the variable we have previously set


@pytest.fixture
def fixture_dict() -> Dict:
    """This fixture returns a dict. Its only role is to minimize the amount of code we have to write.

    :return: A dict
    """
    os.environ['KEY'] = 'Hello'

    my_dict = {
        'Hello': {
            'World': '!',
            1: {
                2: 3
            }
        }
    }
    return my_dict


def test_fixture_1(fixture_env, fixture_dict) -> None:
    key = os.environ['KEY']
    assert fixture_dict[key]['World'] == '!'


def test_fixture_2(fixture_env, fixture_dict) -> None:
    key = os.environ['KEY']
    assert fixture_dict[key][1] == {2: 3}


# === PARAMETRIZED TEST ===

@pytest.mark.parametrize(
    'param_a, param_b',  # Declare the parameters you want to test
    [  # Declare multiple sets of values to assign to the aforementioned parameters
        (1, '1'),
        (1.0, '1'),
        (1, '1.0'),
        (1.0, '1.0')
    ],
    ids=[  # This entry is optional - you can use it to name your different sets of parameters
        'int to string int',
        'float to string int',
        'int to string float',
        'float to string float'
    ]
)
def test_parametrized(param_a, param_b) -> None:
    """If you want to test a function against multiple sets of parameters, use a parametrized test.
    """
    assert float(param_a) == float(param_b)


# === SIMPLE PARAMETRIZED FIXTURES ===

@pytest.fixture(params=[1, '1'])
def fixture_int(request) -> Any:
    """This parametrized fixture will be called multiple times: once per param value.
    """
    return request.param  # Returns the current parameter


@pytest.fixture(params=[1.0, '1.0', 1, '1.0'])
def fixture_float(request) -> Any:
    """This parametrized fixture will be called multiple times: once per param value.
    """
    return request.param  # Returns the current parameter


def test_parametrized_fixtures(fixture_int, fixture_float) -> None:
    assert int(fixture_int) == int(float(fixture_float))


# === PARAMETRIZED TEST WITH INDIRECT PARAMETERS (SIMILAR TO PARAMETRIZED FIXTURES) ===

@pytest.fixture(scope='function')
def fixture_parametrized_env(request) -> None:
    key, value = request.param
    os.environ[key] = value
    yield
    del os.environ[key]


@pytest.mark.parametrize(
    'fixture_parametrized_env, result',
    [
        (('key_1', '4'), 5),
        (('key_2', '3'), 4),
        (('key_3', '2'), 4)
    ],
    indirect=['fixture_parametrized_env']  # The parameters for fixture_parametrized_env will be passed to the fixture
)
def test_parametrized(fixture_parametrized_env, result) -> None:
    """If you want to test a function against multiple sets of parameters, use a parametrized test.
    """
    key_1 = int(os.environ.get('key_1', '1'))
    key_2 = int(os.environ.get('key_2', '1'))
    key_3 = int(os.environ.get('key_3', '1'))

    assert (key_1 + key_2) * key_3 == result
