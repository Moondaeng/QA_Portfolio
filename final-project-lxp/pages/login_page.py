import logging
import time
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, Locator

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """엘리스 LXP 로그인 페이지 Object.

    로그인 화면의 요소(이메일 입력창, 비밀번호 입력창, 로그인 버튼)와
    로그인 관련 사용자 동작을 제공한다.
    """

    # Locators
    EMAIL_INPUT: Locator = (By.NAME, "loginId")
    PASSWORD_INPUT: Locator = (By.NAME, "password")
    LOGIN_BUTTON: Locator = (By.CSS_SELECTOR, "button[type='submit']")

    def __init__(self, driver: WebDriver, timeout: float = 15) -> None:
        """LoginPage를 초기화한다."""
        super().__init__(driver, timeout)

    def navigate(self, url: str) -> None:
        """지정한 URL로 이동하고 로그인 입력 폼이 준비될 때까지 기다린다.

        LXP 기본 URL에서 계정 로그인 문서로 리다이렉트되는 동안에는
        ChromeDriver의 요소 조회가 ``aborted by navigation``으로 잠시
        중단될 수 있다. 이 경우에만 현재 locator를 다시 조회하며, 다른
        WebDriver 오류는 예상하지 못한 실행 실패로 그대로 전달한다.
        """
        logger.info("로그인 페이지로 이동: url=%s", url)
        self.open_url(url)

        def login_form_is_ready(driver: WebDriver) -> WebElement | bool:
            try:
                for element in driver.find_elements(*self.EMAIL_INPUT):
                    if element.is_displayed() and element.is_enabled():
                        return element
                return False
            except WebDriverException as error:
                if "aborted by navigation" not in str(error).lower():
                    raise
                logger.debug("로그인 페이지 리다이렉트 완료 대기")
                return False

        WebDriverWait(self.driver, self.default_timeout).until(
            login_form_is_ready
        )
        logger.info("로그인 입력 폼 준비 완료")

    def enter_email(self, email: str) -> WebElement:
        """이메일(아이디)을 입력한다."""
        logger.info("이메일 입력 완료")
        return self.fill_text(self.EMAIL_INPUT, email)

    def enter_password(self, password: str) -> WebElement:
        """비밀번호를 입력한다. (보안을 위해 로그에는 값을 남기지 않음)"""
        logger.info("비밀번호 입력 완료 (마스킹)")
        return self.fill_text(self.PASSWORD_INPUT, password)

    def click_login_button(self) -> WebElement:
        """로그인 제출 버튼을 클릭한다."""
        logger.info("로그인 버튼 클릭")
        return self.click(self.LOGIN_BUTTON)

    def login(self, email: str, password: str) -> None:
        """이메일과 비밀번호를 입력하고 로그인을 수행한다.

        Args:
            email: 로그인할 사용자 계정 이메일.
            password: 로그인할 사용자 계정 비밀번호.
        """
        logger.info("일반 로그인 수행")
        self.enter_email(email)
        self.enter_password(password)
        self.click_login_button()

    def wait_until_logged_in(self, timeout: float | None = None) -> bool:
        """로그인 완료 후 메인 LXP 화면이 완전히 로드될 때까지 대기한다.

        Args:
            timeout: 최대 대기 시간(초). None이면 기본값 사용.

        Returns:
            bool: 로그인 완료(메인 요소 로드 성공) 여부.
        """
        logger.info("로그인 완료 대기")
        selected_timeout = self._get_timeout(timeout)

        try:
            # 1. accounts 도메인에서 빠져나와 lxp 도메인으로 복귀 대기
            WebDriverWait(self.driver, selected_timeout).until(
                lambda d: "accounts" not in d.current_url.lower()
                and "signin" not in d.current_url.lower()
                and ("lxp" in d.current_url.lower() or "classrooms" in d.current_url.lower() or "my" in d.current_url.lower())
            )
            # 2. 메인 화면(클래스룸 링크 또는 네비게이션) 렌더링 대기
            WebDriverWait(self.driver, selected_timeout).until(
                lambda d: len(
                    d.find_elements(
                        By.XPATH,
                        "//a[contains(@href, '10e4be6f') or contains(., 'QA6_2') or contains(., '탐색') or contains(., '내 클래스')]",
                    )
                ) > 0
            )
            return True
        except TimeoutException:
            return False

    def handle_reauth_if_present(
        self,
        password: str | None = None,
        timeout: float | None = None,
        *,
        source: str = "unknown",
        reason: str = "unspecified",
    ) -> bool:
        """재인증 화면이면 렌더링을 기다린 후 비밀번호를 입력해 통과한다.

        Args:
            password: 입력할 비밀번호. None이면 환경변수 EDUCATOR_PASSWORD 또는 LEARNER_PASSWORD 사용.
            timeout: 재인증 입력 요소와 완료 이동을 기다릴 최대 시간(초).
            source: 재인증 확인을 요청한 fixture 또는 Page Object 위치.
            reason: 재인증 확인이 필요한 사용자 흐름 또는 이동 유형.

        Returns:
            bool: 재인증을 수행했으면 True, 일반 페이지 상태였으면 False.
        """
        import os
        current_url = self.driver.current_url.lower()
        if "accounts" not in current_url and "signin" not in current_url:
            return False

        pwd = password or os.getenv("EDUCATOR_PASSWORD", "").strip() or os.getenv("LEARNER_PASSWORD", "").strip()
        if not pwd:
            raise ValueError("재인증에 사용할 비밀번호가 설정되지 않았습니다.")

        selected_timeout = self._get_timeout(timeout)
        started_at = time.monotonic()
        logger.info(
            "비밀번호 재인증 화면 감지 및 자동 통과 수행 시작: "
            "source=%s, reason=%s",
            source,
            reason,
        )

        # URL이 먼저 변경되고 입력 DOM이 나중에 렌더링될 수 있으므로 기다린다.
        password_input = self.wait_for_first_visible(
            self.PASSWORD_INPUT,
            selected_timeout,
        )
        password_input.clear()
        password_input.send_keys(pwd)

        # 동적 MUI 클래스 대신 표준 submit 속성을 가진 표시 버튼을 사용한다.
        submit_button = self.wait_for_first_visible(
            self.LOGIN_BUTTON,
            selected_timeout,
        )
        submit_button.click()

        WebDriverWait(self.driver, selected_timeout).until(
            lambda driver: "accounts" not in driver.current_url.lower()
            and "signin" not in driver.current_url.lower()
        )
        logger.info(
            "비밀번호 재인증 처리 완료: source=%s, reason=%s, elapsed=%.2fs",
            source,
            reason,
            time.monotonic() - started_at,
        )
        return True
