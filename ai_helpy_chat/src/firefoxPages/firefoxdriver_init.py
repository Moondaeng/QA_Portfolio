"""Firefox WebDriver 초기화 및 테스트 실행 설정."""

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

def init_firefox_driver():
    """Firefox WebDriver를 생성하고 창 크기·위치를 설정한다.

    Returns:
        설정이 완료된 Firefox WebDriver 인스턴스.
    """
    options = webdriver.FirefoxOptions()

    service = Service(GeckoDriverManager().install())

    driver = webdriver.Firefox(
        service=service,
        options=options,
    )

    driver.set_window_size(1920, 880)
    driver.set_window_position(0, 0)

    return driver
