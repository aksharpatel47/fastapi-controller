import pytest

from fastapi_controller.controller_utils import _compute_path


@pytest.mark.parametrize("controller_name,path",
                         [("PeopleController", "v1.0/people/"), ("APPTestController", "v1.0/app_test/"),
                          ("PeopleAppController", "v1.0/people_app/")])
def test_compute_path(controller_name, path):
    assert _compute_path("/", controller_name, "{version}/{controller}", "v1.0") == path
