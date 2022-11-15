import orjson_pydantic
import pytest


@pytest.mark.parametrize("input", [
    b'"\xc8\x93',
    b'"\xc8',
])
def test_invalid(input):
    with pytest.raises(orjson_pydantic.JSONDecodeError):
        orjson_pydantic.loads(input)
