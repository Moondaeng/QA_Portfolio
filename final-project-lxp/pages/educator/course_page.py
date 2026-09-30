import logging
import re
from urllib.parse import urlparse

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, Locator

logger = logging.getLogger(__name__)


class EducatorCoursePage(BasePage):
    """교육자 과목 목록 및 상세 페이지 Object.

    과목 목록 조회, 활성 과목 진입 및 과목 상세 정보/수업 목록 확인을 제공한다.
    """

    # 과목 목록 및 카드 Locators
    COURSE_LIST_HEADING: Locator = (
        By.XPATH,
        "//main//h4[normalize-space()='학습 과목 목록']",
    )
    COURSE_CARD: Locator = (
        By.XPATH,
        "//main//button[not(@disabled)]"
        "[.//*[self::h6 or self::p or contains(@class, 'MuiTypography-subtitle')]]",
    )
    # 과목 상세 화면 Locators
    COURSE_DETAIL_CONTAINER: Locator = (
        By.CSS_SELECTOR,
        "main",
    )

    # 교육자 수업 순서 관리 Locators
    COURSE_EDIT_CONTROL: Locator = (
        By.XPATH,
        "//label[contains(@class, 'MuiFormControlLabel-root') and .//*[contains(normalize-space(), '과목 편집')]]"
        " | //button[contains(normalize-space(), '과목 편집') or .//*[contains(normalize-space(), '과목 편집')]]",
    )
    REORDER_MODE_INDICATOR: Locator = (
        By.XPATH,
        "//*[contains(normalize-space(), '순서 변경') "
        "or contains(normalize-space(), '순서 저장') "
        "or contains(normalize-space(), '순서 편집') "
        "or contains(normalize-space(), '순서 편집 완료')]",
    )

    def __init__(self, driver: WebDriver, timeout: float = 15) -> None:
        """EducatorCoursePage를 초기화한다."""
        super().__init__(driver, timeout)

    def get_course_cards(self) -> list[WebElement]:
        """과목 목록 화면에서 클릭 가능한 과목 카드 요소를 가져온다."""
        return self.find_elements_visible(self.COURSE_CARD, timeout=10)

    def get_course_count(self) -> int:
        """현재 화면에 표시된 과목 개수를 반환한다."""
        try:
            cards = self.get_course_cards()
            return len(cards)
        except TimeoutException:
            return 0

    def is_course_list_displayed(self) -> bool:
        """학습 과목 목록 제목과 하나 이상의 과목 행이 보이는지 확인한다."""
        try:
            self.wait_for_visible(self.COURSE_LIST_HEADING, timeout=10)
            return self.get_course_count() > 0
        except TimeoutException:
            return False

    def select_first_active_course(self) -> WebElement:
        """목록에서 첫 번째 표시·활성 과목을 클릭하여 상세 화면으로 진입한다."""
        logger.info("첫 번째 표시 과목 선택")
        return self.click(self.COURSE_CARD, timeout=10)

    def is_course_detail_loaded(self, previous_url: str) -> bool:
        """과목 목록에서 개별 과목 상세 경로로 이동했는지 확인한다."""
        try:
            def detail_route_loaded(driver: WebDriver) -> bool:
                current_url = driver.current_url
                path = urlparse(current_url).path
                return (
                    current_url != previous_url
                    and re.search(r"/courses/[^/]+(?:/|$)", path) is not None
                )

            WebDriverWait(self.driver, 10).until(detail_route_loaded)
            return self.find_optional_visible(self.COURSE_DETAIL_CONTAINER, timeout=5) is not None
        except TimeoutException:
            return False

    def navigate_to_course_edit_page(self, url: str) -> None:
        """과목 편집 화면으로 이동하고 늦게 뜨는 재인증을 1회 처리한다."""
        self.open_url(url)
        destination = self._wait_for_course_edit_or_reauth(timeout=15)
        if destination != "reauth":
            return

        logger.info("과목 편집 URL 이동 후 재인증 화면 감지")
        from pages.login_page import LoginPage

        LoginPage(self.driver).handle_reauth_if_present(
            source="pages.educator.course_page",
            reason="course_edit_direct_navigation",
        )
        destination = self._wait_for_course_edit_or_reauth(timeout=15)
        if destination == "reauth":
            raise RuntimeError("과목 편집 URL 이동 후 재인증 화면이 계속 표시됩니다.")

    def _wait_for_course_edit_or_reauth(self, timeout: float) -> str:
        """과목 편집 제어 또는 재인증 화면 중 먼저 도착한 상태를 반환한다."""
        def destination(driver: WebDriver) -> str | bool:
            current_url = driver.current_url.lower()
            if "accounts" in current_url or "signin" in current_url:
                return "reauth"
            if any(
                element.is_displayed()
                for element in driver.find_elements(*self.COURSE_EDIT_CONTROL)
            ):
                return "course_edit"
            return False

        return WebDriverWait(self.driver, timeout).until(destination)

    def enter_course_edit_mode(self) -> WebElement | None:
        """교육자용 과목 편집 제어(스위치)를 클릭해 순서 변경 모드로 진입한다."""
        if self.is_reorder_mode_displayed():
            logger.info("이미 과목 편집 모드 상태입니다.")
            return self.find_optional_visible(self.COURSE_EDIT_CONTROL)
        logger.info("과목 편집 스위치 클릭")
        control = self.wait_for_present(self.COURSE_EDIT_CONTROL, timeout=10)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", control)
        try:
            control.click()
        except ElementClickInterceptedException:
            self.click_with_javascript(control)
        try:
            WebDriverWait(self.driver, 5).until(lambda _: self.is_reorder_mode_displayed())
        except TimeoutException:
            pass
        return control

    def is_reorder_mode_displayed(self) -> bool:
        """수업 순서 변경 모드의 표시 또는 활성 편집 제어를 확인한다."""
        # 1. 보조 근거: 순서 변경 관련 UI 인디케이터 확인
        if self.find_optional_visible(self.REORDER_MODE_INDICATOR, timeout=1):
            return True

        # 2. 주 근거: 과목 편집 제어 컨테이너 내부의 체크/선택 상태 확인
        control = self.find_optional_visible(self.COURSE_EDIT_CONTROL, timeout=2)
        if control is None:
            return False

        # ARIA 기반 switch/button 속성 확인
        aria_checked = control.get_attribute("aria-checked")
        if aria_checked == "true":
            return True

        aria_pressed = control.get_attribute("aria-pressed")
        if aria_pressed == "true":
            return True

        # input[type='checkbox']의 실제 선택 상태 확인
        checkboxes = control.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        if checkboxes:
            checkbox = checkboxes[0]
            if checkbox.is_selected():
                return True
            if checkbox.get_attribute("aria-checked") == "true":
                return True

        return False
