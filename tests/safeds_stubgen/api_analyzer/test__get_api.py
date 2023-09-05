from pathlib import Path

import pytest

from safeds_stubgen.api_analyzer import API, get_api

_test_dir = Path(__file__).parent.parent.parent
_test_package_name = "some_package"


some_module_module_attributes = [
    {
        "id": "some_package/test.data.some_package.some_module/a",
        "name": "a",
        "types": ...,
        "description": "",
        "is_public": True,
        "is_static": False,
    },
    {
        "id": "some_package/test.data.some_package.some_module/a2",
        "name": "a2",
        "types": ...,
        "description": "",
        "is_public": True,
        "is_static": False,
    },
    {
        "id": "some_package/test.data.some_package.some_module/a3",
        "name": "a3",
        "types": ...,
        "description": "",
        "is_public": True,
        "is_static": False,
    },
    {
        "id": "some_package/test.data.some_package.some_module/a_list",
        "name": "a_list",
        "types": ...,
        "description": "",
        "is_public": True,
        "is_static": False,
    },
    {
        "id": "some_package/test.data.some_package.some_module/a_list_2",
        "name": "a_list_2",
        "types": ...,
        "description": "",
        "is_public": True,
        "is_static": False,
    },
    {
        "id": "some_package/test.data.some_package.some_module/this_a_dict",
        "name": "this_a_dict",
        "types": ...,
        "description": "",
        "is_public": True,
        "is_static": False,
    },
    {
        "id": "some_package/test.data.some_package.some_module/b",
        "name": "b",
        "types": ...,
        "description": "",
        "is_public": True,
        "is_static": False,
    },
    {
        "id": "some_package/test.data.some_package.some_module/c",
        "name": "c",
        "types": ...,
        "description": "",
        "is_public": True,
        "is_static": False,
    },
    {
        "id": "some_package/test.data.some_package.some_module/a_2",
        "name": "a_2",
        "types": ...,
        "description": "",
        "is_public": True,
        "is_static": False,
    },
    {
        "id": "some_package/test.data.some_package.some_module/a_3",
        "name": "a_3",
        "types": ...,
        "description": "",
        "is_public": True,
        "is_static": False,
    },
    {
        "id": "some_package/test.data.some_package.some_module/a_4",
        "name": "a_4",
        "types": ...,
        "description": "",
        "is_public": True,
        "is_static": False,
    },
    {
        "id": "some_package/test.data.some_package.some_module/a_5",
        "name": "a_5",
        "types": ...,
        "description": "",
        "is_public": True,
        "is_static": False,
    }
]


@pytest.mark.parametrize(
    ("package_name", "package_root", "module_name", "expected_attribute_data"),
    [
        (
            _test_package_name,
            Path(_test_dir / "data" / _test_package_name),
            "some_module",
            some_module_module_attributes,
        ),
    ],
    ids=[
        "module_attributes",
    ],
)
def test_module_attributes(
    package_name: str,
    package_root: Path,
    module_name: str,
    expected_attribute_data: list[dict],
) -> None:
    # Get API data
    result = get_api(
        package_name=package_name,
        root=package_root,
    )
    assert isinstance(result, API)

    # Transform data to dict
    result_data = result.to_dict()

    # Get the module we want to get the test data from
    test_module = {}
    for module in result_data["modules"]:
        if module['name'].endswith(module_name):
            test_module = module
    assert test_module != {}

    module_attributes = test_module.get("global_attributes", [])
    assert len(module_attributes) == 5
    ...  # Todo
