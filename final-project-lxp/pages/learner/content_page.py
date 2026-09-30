"""학습자의 수업·자료 노출과 직접 접근 권한을 검증하는 Page Object."""

import logging
import os
from urllib.parse import urljoin, urlparse

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, Locator


logger = logging.getLogger(__name__)


class LearnerContentPage(BasePage):
    """학습자 관점의 수업 목록과 콘텐츠 직접 접근 화면을 제공한다."""

    PAGE_MAIN: Locator = (By.CSS_SELECTOR, "main")
    EDIT_MODE_CONTROL: Locator = (
        By.XPATH,
        "//main//*[self::button or self::label]"
        "[normalize-space()='과목 편집' "
        "or .//*[normalize-space()='과목 편집']]",
    )
    ACCESS_DENIED_ALERT: Locator = (
        By.XPATH,
        "//main//*[contains(normalize-space(), '접근 권한이 없습니다') "
        "or contains(normalize-space(), '권한이 없습니다') "
        "or contains(normalize-space(), '접근할 수 없습니다') "
        "or contains(normalize-space(), '접근이 제한') "
        "or normalize-space()='403']",
    )
    REAUTH_REDIRECT_TIMEOUT = 5

    def __init__(self, driver: WebDriver, timeout: float = 15) -> None:
        super().__init__(driver, timeout)

    def _wait_for_delayed_reauth_redirect(self) -> bool:
        """직접 URL 접근 뒤 늦게 발생하는 재인증 이동을 제한적으로 기다린다."""
        try:
            WebDriverWait(
                self.driver,
                self.REAUTH_REDIRECT_TIMEOUT,
            ).until(
                lambda driver: "accounts" in driver.current_url.lower()
                or "signin" in driver.current_url.lower()
            )
            logger.info("학습자 콘텐츠 직접 접근 후 지연 재인증 화면 감지")
            return True
        except TimeoutException:
            return False

    def navigate(self, url: str) -> None:
        """학습자 세션으로 대상 URL에 접근하고 주 화면이 표시될 때까지 기다린다.

        접근 중 계정 재인증 화면이 나오면 학습자 비밀번호로만 처리한다.
        재인증 화면이 남아 있으면 권한 차단으로 오인하지 않도록 즉시 실패시킨다.
        """
        self.open_url(url)
        from pages.login_page import LoginPage

        if self._wait_for_delayed_reauth_redirect():
            LoginPage(self.driver).handle_reauth_if_present(
                os.getenv("LEARNER_PASSWORD", "").strip(),
                source="pages.learner.content_page",
                reason="content_direct_navigation",
            )
        current_url = self.driver.current_url.lower()
        if "accounts" in current_url or "signin" in current_url:
            raise RuntimeError(
                "학습자 콘텐츠 접근 중 비밀번호 재인증 화면이 남아 있습니다. "
                "권한 차단 결과로 판정하지 않습니다."
            )
        self.wait_for_visible(self.PAGE_MAIN)

    def is_edit_mode_control_visible(self) -> bool:
        """교육자 전용 과목 편집 제어가 학습자 화면에 보이는지 확인한다."""
        return self.find_optional_visible(self.EDIT_MODE_CONTROL, timeout=3) is not None

    def is_target_link_visible(self, target_url: str) -> bool:
        """현재 학습 화면의 보이는 링크 중 대상 URL과 같은 경로가 있는지 확인한다."""
        target_path = urlparse(target_url).path.rstrip("/")

        for link in self.driver.find_elements(By.CSS_SELECTOR, "main a[href]"):
            if not link.is_displayed():
                continue

            link_path = urlparse(
                urljoin(self.driver.current_url, link.get_attribute("href"))
            ).path.rstrip("/")
            if link_path == target_path:
                return True

        return False

    def is_visible_text(self, expected_text: str) -> bool:
        """현재 주 화면의 보이는 텍스트 요소에 기대 문구가 있는지 확인한다."""
        candidates = self.driver.find_elements(
            By.CSS_SELECTOR, "main p, main h1, main h2, main h3, main h4, main span"
        )
        return any(
            element.is_displayed() and element.text.strip() == expected_text
            for element in candidates
        )

    @staticmethod
    def _xpath_literal(value: str) -> str:
        """동적 제목을 안전한 XPath 문자열 리터럴로 변환한다."""
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        return "concat(" + ", \"'\", ".join(
            f"'{piece}'" for piece in value.split("'")
        ) + ")"

    def _lesson_title_locator(self, title: str) -> Locator:
        """학습자 과목 상세(main)에서 일치하는 수업 제목 locator를 만든다."""
        return (
            By.XPATH,
            "//main//*[self::p or self::h6]"
            f"[normalize-space()={self._xpath_literal(title)}]",
        )

    def is_lesson_visible(self, title: str) -> bool:
        """현재 학습자 과목 화면에 지정 수업 제목이 보이는지 확인한다."""
        return self.find_optional_visible(self._lesson_title_locator(title), timeout=3) is not None

    def wait_until_lesson_visibility(
        self, title: str, should_be_visible: bool, timeout: float = 12
    ) -> bool:
        """수업 공개 상태 변경 뒤 학습자 화면의 노출 결과를 기다린다."""
        locator = self._lesson_title_locator(title)

        def visibility_matches(driver: WebDriver) -> bool:
            visible = False
            for element in driver.find_elements(*locator):
                try:
                    if element.is_displayed():
                        visible = True
                        break
                except StaleElementReferenceException:
                    continue
            return visible is should_be_visible

        return WebDriverWait(self.driver, timeout).until(
            visibility_matches
        )

    def is_direct_access_blocked(self, requested_url: str) -> bool:
        """직접 접근이 권한 안내 또는 다른 화면 리다이렉트로 차단됐는지 확인한다."""
        if self.find_optional_visible(self.ACCESS_DENIED_ALERT, timeout=5):
            return True

        requested_path = urlparse(requested_url).path.rstrip("/")
        current_path = urlparse(self.driver.current_url).path.rstrip("/")
        return current_path != requested_path
