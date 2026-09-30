"""학습자 테스트에서 공유하는 설정 및 화면 대기 helper."""

import os
from urllib.parse import urlparse

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.login_page import LoginPage


def required_url(env_name: str) -> str:
    """필수 URL 환경 변수 값을 검증해 반환한다."""
    value = os.getenv(env_name, "").strip()
    if not value:
        raise ValueError(f"필수 URL 환경 변수가 없습니다: {env_name}")

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(
            f"URL 형식이 올바르지 않은 환경 변수입니다: {env_name}"
        )
    return value


def normalized_url_path(url: str) -> str:
    """비교 가능한 형태로 URL 경로를 반환한다."""
    return urlparse(url).path.rstrip("/") or "/"


def wait_for_login_destination(
    driver: WebDriver,
    timeout: float = 15,
) -> tuple[str, WebElement]:
    """일반 로그인 URL과 이메일 입력란이 모두 준비될 때까지 기다린다."""
    login_url = WebDriverWait(driver, timeout).until(
        lambda current_driver: (
            current_driver.current_url
            if "accounts" in current_driver.current_url.lower()
            or "signin" in current_driver.current_url.lower()
            else False
        ),
        message="로그인 URL로 이동하지 않았습니다.",
    )
    email_input = WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(LoginPage.EMAIL_INPUT),
        message="로그인 화면의 이메일 입력란이 표시되지 않았습니다.",
    )
    return login_url, email_input
