from app.agents.tools.system_info import (
    get_system_info,
)
from app.core.config import settings


def test_system_info_tool():
    result = (
        get_system_info.invoke({})
    )

    assert (
        result["app_name"]
        == settings.app_name
    )

    assert (
        result["version"]
        == settings.app_version
    )

    assert (
        result["environment"]
        == settings.environment
    )