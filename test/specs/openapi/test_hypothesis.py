import pytest
from hypothesis import given, settings

import schemathesis
from schemathesis.specs.openapi._hypothesis import get_case_strategy


@pytest.fixture
def operation(make_openapi_3_schema):
    schema = make_openapi_3_schema(
        body={
            "required": True,
            "content": {"application/json": {"schema": {"type": "string"}}},
        },
        parameters=[
            {"in": "path", "name": "p1", "required": True, "schema": {"type": "string", "enum": ["FOO"]}},
            {"in": "header", "name": "h1", "required": True, "schema": {"type": "string", "enum": ["FOO"]}},
            {"in": "cookie", "name": "c1", "required": True, "schema": {"type": "string", "enum": ["FOO"]}},
            {"in": "query", "name": "q1", "required": True, "schema": {"type": "string", "enum": ["FOO"]}},
        ],
    )
    return schemathesis.from_dict(schema)["/users"]["POST"]


@pytest.mark.parametrize(
    "values, expected",
    (
        ({"body": "TEST"}, {"body": "TEST"}),
        ({"path_parameters": {"p1": "TEST"}}, {"path_parameters": {"p1": "TEST"}}),
        ({"path_parameters": {}}, {"path_parameters": {"p1": "FOO"}}),
        ({"headers": {"h1": "TEST"}}, {"headers": {"h1": "TEST"}}),
        ({"headers": {}}, {"headers": {"h1": "FOO"}}),
        # Even if the explicit value does not match the schema, it should appear in the output
        ({"headers": {"invalid": "T"}}, {"headers": {"h1": "FOO", "invalid": "T"}}),
        ({"cookies": {"c1": "TEST"}}, {"cookies": {"c1": "TEST"}}),
        ({"cookies": {}}, {"cookies": {"c1": "FOO"}}),
        ({"query": {"q1": "TEST"}}, {"query": {"q1": "TEST"}}),
        ({"query": {}}, {"query": {"q1": "FOO"}}),
    ),
)
def test_explicit_attributes(operation, values, expected):
    # When some Case's attribute is passed explicitly to the case strategy
    strategy = get_case_strategy(operation=operation, **values)

    @given(strategy)
    @settings(max_examples=1)
    def test(case):
        # Then it should appear in the final result
        for attr_name, expected_values in expected.items():
            value = getattr(case, attr_name)
            assert value == expected_values

    test()
