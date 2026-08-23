from datetime import datetime
import logging
import pytest

from src.firefoxPages.firefoxdriver_init import init_firefox_driver

logger = logging.getLogger(__name__)

@pytest.fixture(scope="function")
def firefox_driver():
    """Firefox WebDriver를 생성하고 테스트 종료 후 종료한다."""

    driver = init_firefox_driver()

    try:
        yield driver

    finally:
        driver.quit()

@pytest.hookimpl(trylast=True)
def pytest_configure(config):
    """테스트 실행 시각을 포함한 로그 파일 경로를 설정한다."""
    logging_plugin = config.pluginmanager.get_plugin("logging-plugin")

    if logging_plugin is None:
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    logging_plugin.set_log_path(
        f"logs/test_{timestamp}.log"
    )

# def configure_external_loggers():
#     """외부 라이브러리의 상세 로그를 제한한다.
#        selenium, urllib3, WDM의 Level을 변경
#        DEBUG->WARNING
#     """
#     logging.getLogger("selenium").setLevel(logging.WARNING)
#     logging.getLogger("urllib3").setLevel(logging.WARNING)
#     logging.getLogger("WDM").setLevel(logging.WARNING)