import logging
import os
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


def get_classroom_id() -> str:
    """환경변수에서 QA6_2 클래스룸 ID를 가져온다."""
    cid = os.getenv("CLASSROOM_ID") or os.getenv("API_CLASSROOM_ID")
    if cid and cid.strip():
        return cid.strip()

    # EDUCATOR_CLASSROOM_URL, EDUCATOR_COURSE_EDIT_URL, CLASS_HOME_URL 등에서 추출
    for env_key in (
        "EDUCATOR_CLASSROOM_URL",
        "EDUCATOR_COURSE_EDIT_URL",
        "CLASS_HOME_URL",
        "LEARNER_COURSE_URL",
    ):
        url = os.getenv(env_key, "").strip()
        if "/classrooms/" in url:
            parts = url.split("/classrooms/")[1].split("/")
            if parts and parts[0]:
                return parts[0]

    raise ValueError(
        "클래스룸 ID를 확인할 수 없습니다. CLASSROOM_ID, API_CLASSROOM_ID 또는 "
        "클래스룸 경로를 포함한 URL 환경 변수를 설정해야 합니다."
    )


def get_classroom_url() -> str:
    """QA6_2 클래스룸 기본 URL을 반환한다."""
    custom_url = os.getenv("EDUCATOR_CLASSROOM_URL", "").strip()
    if custom_url:
        return custom_url

    base = os.getenv("BASE_URL", "").strip().rstrip("/")
    if not base:
        raise ValueError(
            "EDUCATOR_CLASSROOM_URL 또는 BASE_URL 환경 변수를 설정해야 합니다."
        )
    if base.endswith("/lxp"):
        base = base[:-4]

    return f"{base}/classrooms/{get_classroom_id()}"


class ClassroomHomePage(BasePage):
    """교육자 클래스룸 메인 및 홈 화면 Page Object.

    1. 메인 대시보드에서 [QA6_2팀] 최종프로젝트 클래스 선택 및 진입
    2. 클래스룸 4개 핵심 메뉴(클래스 홈, 학습 과목, 수업 일정, 게시판) 진입
    3. 클래스 홈 내의 수업 일정, 학습 과목 영역 바로가기 동작 제공
    """

    # 메인 사이드바 및 대시보드의 클래스룸 선택 Locators
    CLASSROOM_QA6_2_LINK: Locator = (
        By.XPATH,
        f"//a[contains(@href, '{get_classroom_id()}') or contains(., 'QA6_2') or .//span[contains(., 'QA6_2')]]",
    )

    # [1순위: CSS_SELECTOR] 클래스룸 4개 핵심 메뉴 (좌측 사이드바 고유 href 기반)
    NAV_CLASSROOM_HOME: Locator = (
        By.CSS_SELECTOR,
        f"aside a[href$='{get_classroom_id()}']",
    )
    NAV_COURSES: Locator = (
        By.CSS_SELECTOR,
        "aside a[href*='/courses']",
    )
    NAV_SCHEDULE: Locator = (
        By.CSS_SELECTOR,
        "aside a[href*='/schedules']",
    )
    NAV_BOARD: Locator = (
        By.CSS_SELECTOR,
        "aside a[href*='/articles']",
    )

    # [카드 컨텍스트 기반] 수업 일정 섹션 바로가기 Locators
    SCHEDULE_VIEW_ALL_BTN: Locator = (
        By.XPATH,
        "//main//div[contains(@class, 'MuiCard-root') or contains(@class, 'card') or self::section]"
        "[.//*[contains(normalize-space(), '수업 일정')]]"
        "//button[normalize-space(.)='전체 보기' or normalize-space(.)='전체보기']",
    )
    CREATE_SCHEDULE_BTN: Locator = (
        By.XPATH,
        "//main//div[contains(@class, 'MuiCard-root') or contains(@class, 'card') or self::section]"
        "[.//*[contains(normalize-space(), '수업 일정')]]"
        "//button[contains(., '새 일정 만들기') or contains(., '새 일정')]",
    )

    # [카드 컨텍스트 기반] 학습 과목 섹션 바로가기 Locators
    COURSE_VIEW_ALL_BTN: Locator = (
        By.XPATH,
        "//main//div[contains(@class, 'MuiCard-root') or contains(@class, 'card') or self::section]"
        "[.//*[contains(normalize-space(), '학습 과목')]]"
        "//button[normalize-space(.)='전체 보기' or normalize-space(.)='전체보기']",
    )
    COURSE_MORE_BTN: Locator = (
        By.XPATH,
        "//main//div[contains(@class, 'MuiCard-root') or contains(@class, 'card') or self::section]"
        "[.//*[contains(normalize-space(), '학습 과목')]]"
        "//button[normalize-space(.)='더보기']",
    )

    SCHEDULE_PAGE_HEADING: Locator = (
        By.XPATH,
        "//main//*[self::h1 or self::h2 or self::h3 or self::h4]"
        "[normalize-space()='수업 일정']",
    )
    SCHEDULE_CREATE_FORM: Locator = (
        By.XPATH,
        "//div[@role='dialog'][.//*[contains(normalize-space(), '일정')]]"
        "//input[@name='summary' or not(@type='hidden')]"
        " | //main//form[.//*[contains(normalize-space(), '일정')]]"
        "//input[@name='summary' or not(@type='hidden')]",
    )
    COURSE_LIST_HEADING: Locator = (
        By.XPATH,
        "//main//*[self::h1 or self::h2 or self::h3 or self::h4]"
        "[normalize-space()='학습 과목 목록']",
    )
    HOME_COURSE_ITEM: Locator = (
        By.XPATH,
        "//main//div[contains(@class, 'MuiCard-root') or contains(@class, 'card') or self::section]"
        "[.//*[normalize-space()='학습 과목']]//ul/li",
    )

    def __init__(self, driver: WebDriver, timeout: float = 15) -> None:
        """ClassroomHomePage를 초기화한다."""
        super().__init__(driver, timeout)

    def _wait_for_classroom_or_reauth(self, timeout: float) -> str:
        """클래스룸 메뉴 또는 재인증 화면 중 먼저 도착한 상태를 반환한다."""
        cid = get_classroom_id()

        def destination(driver: WebDriver) -> str | bool:
            current_url = driver.current_url.lower()
            if "accounts" in current_url or "signin" in current_url:
                return "reauth"
            if cid in current_url and any(
                element.is_displayed()
                for element in driver.find_elements(*self.NAV_COURSES)
            ):
                return "classroom"
            return False

        return WebDriverWait(self.driver, timeout).until(destination)

    def select_qa6_2_classroom(self) -> str:
        """메인 대시보드 좌측 메뉴 또는 목록에서 [QA6_2팀] 최종프로젝트 클래스를 선택하여 진입한다."""
        logger.info("[QA6_2팀] 최종프로젝트 클래스 선택")
        cid = get_classroom_id()
        if cid in self.driver.current_url:
            return self._wait_for_classroom_or_reauth(self.default_timeout)

        try:
            element = self.wait_for_visible(self.CLASSROOM_QA6_2_LINK, timeout=10)
            self.saved_classroom_href = element.get_attribute("href")
            self.scroll_element_into_view(element, block="center", timeout=2)
            try:
                element.click()
            except ElementClickInterceptedException:
                self.click_with_javascript(element)
            return self._wait_for_classroom_or_reauth(self.default_timeout)
        except TimeoutException as e:
            logger.info("클래스룸 선택 후 화면 전환 시간 초과(%s)로 URL 이동 1회 보완", e)
            self.open_classroom_url()
            return self._wait_for_classroom_or_reauth(self.default_timeout)

    def open_classroom_url(self) -> None:
        """클래스룸 기본 URL로 이동한다."""
        target_url = getattr(self, "saved_classroom_href", None) or get_classroom_url()
        logger.info("클래스룸 URL로 이동: %s", target_url)
        self.open_url(target_url)

    def wait_for_classroom_loaded(self, timeout: float = 15) -> bool:
        """클래스룸 홈 URL 및 주요 네비게이션 요소(학습 과목 등) 렌더링을 확인한다."""
        try:
            return self._wait_for_classroom_or_reauth(timeout) == "classroom"
        except TimeoutException:
            return False

    def navigate_to_classroom(self, classroom_url: str) -> None:
        """클래스룸 URL로 이동하고 늦게 뜨는 재인증을 1회 처리한다."""
        logger.info("클래스룸 URL로 이동: url=%s", classroom_url)
        self.open_url(classroom_url)
        destination = self._wait_for_classroom_or_reauth(self.default_timeout)
        if destination != "reauth":
            return

        logger.info("클래스룸 URL 이동 후 재인증 화면 감지")
        from pages.login_page import LoginPage

        LoginPage(self.driver).handle_reauth_if_present(
            source="pages.educator.classroom_home_page",
            reason="classroom_direct_navigation",
        )
        destination = self._wait_for_classroom_or_reauth(self.default_timeout)
        if destination == "reauth":
            raise RuntimeError("클래스룸 URL 이동 후 재인증 화면이 계속 표시됩니다.")

    def is_menu_visible(self, menu_name: str) -> bool:
        """지정한 메뉴가 화면에 노출되는지 확인한다.

        Args:
            menu_name: '클래스 홈', '학습 과목', '수업 일정', '게시판' 또는 '홈', '과목', '일정'
        """
        menu_locators = {
            "클래스 홈": self.NAV_CLASSROOM_HOME,
            "홈": self.NAV_CLASSROOM_HOME,
            "학습 과목": self.NAV_COURSES,
            "과목": self.NAV_COURSES,
            "수업 일정": self.NAV_SCHEDULE,
            "일정": self.NAV_SCHEDULE,
            "게시판": self.NAV_BOARD,
        }
        locator = menu_locators.get(menu_name)
        if not locator:
            raise ValueError(f"유효하지 않은 메뉴 이름입니다: {menu_name}")

        try:
            def _check_displayed(driver: WebDriver) -> bool:
                elements = driver.find_elements(*locator)
                if any(el.is_displayed() for el in elements):
                    return True
                keyword = menu_name.replace(" ", "")
                aside_elements = driver.find_elements(By.XPATH, f"//aside//*[contains(normalize-space(.), '{menu_name}') or contains(normalize-space(.), '{keyword}')]")
                return any(el.is_displayed() for el in aside_elements)

            return WebDriverWait(self.driver, 10).until(_check_displayed)
        except TimeoutException:
            return False

    def click_menu(self, menu_name: str) -> WebElement:
        """좌측 네비게이션에서 지정한 메뉴를 클릭한다."""
        menu_locators = {
            "클래스 홈": self.NAV_CLASSROOM_HOME,
            "홈": self.NAV_CLASSROOM_HOME,
            "학습 과목": self.NAV_COURSES,
            "과목": self.NAV_COURSES,
            "수업 일정": self.NAV_SCHEDULE,
            "일정": self.NAV_SCHEDULE,
            "게시판": self.NAV_BOARD,
        }
        locator = menu_locators.get(menu_name)
        if not locator:
            raise ValueError(f"유효하지 않은 메뉴 이름입니다: {menu_name}")

        logger.info("메뉴 클릭: %s", menu_name)
        return self.click(locator)

    def click_schedule_view_all(self) -> WebElement:
        """수업 일정 영역의 [전체 보기]를 클릭한다."""
        logger.info("수업 일정 [전체 보기] 클릭")
        return self.click(self.SCHEDULE_VIEW_ALL_BTN)

    def click_create_schedule(self) -> WebElement:
        """클래스 홈의 [새 일정 만들기] 버튼을 클릭한다."""
        logger.info("[새 일정 만들기] 버튼 클릭")
        return self.click(self.CREATE_SCHEDULE_BTN)

    def click_course_view_all(self) -> WebElement:
        """학습 과목 영역의 [전체 보기]를 클릭한다."""
        logger.info("학습 과목 [전체 보기] 클릭")
        return self.click(self.COURSE_VIEW_ALL_BTN)

    def click_course_more(self) -> WebElement:
        """학습 과목 [더보기]를 화면 안으로 스크롤하고 위치 안정 후 클릭한다."""
        logger.info("학습 과목 [더보기] 클릭")
        return self.click_when_position_stable(self.COURSE_MORE_BTN)

    def wait_for_url_contains(self, keyword: str, timeout: float | None = None) -> bool:
        """현재 URL에 특정 키워드가 포함될 때까지 대기한다."""
        selected_timeout = self._get_timeout(timeout)
        try:
            def _check(driver: WebDriver) -> bool:
                return keyword.lower() in driver.current_url.lower()

            return WebDriverWait(self.driver, selected_timeout).until(_check)
        except TimeoutException:
            return False

    def is_course_list_displayed(self, timeout: float = 10) -> bool:
        """학습 과목 목록 화면의 제목이 표시되는지 확인한다."""
        try:
            if not self.wait_for_url_contains("courses", timeout=timeout):
                return False

            def _check(driver: WebDriver) -> bool:
                elements = driver.find_elements(*self.COURSE_LIST_HEADING)
                return any(e.is_displayed() for e in elements) if elements else False

            return WebDriverWait(self.driver, timeout).until(_check)
        except TimeoutException:
            return False

    def is_schedule_page_displayed(self, timeout: float = 10) -> bool:
        """수업 일정 화면의 일정 목록 또는 캘린더 영역이 표시되는지 확인한다."""
        try:
            if not self.wait_for_url_contains("schedules", timeout=timeout):
                return False

            return self.find_optional_visible(
                self.SCHEDULE_PAGE_HEADING,
                timeout=timeout,
            ) is not None
        except TimeoutException:
            return False

    def is_schedule_create_form_displayed(self, timeout: float = 10) -> bool:
        """수업 일정 작성 모달 또는 작성 폼이 표시되는지 확인한다."""
        try:
            return self.find_optional_visible(
                self.SCHEDULE_CREATE_FORM,
                timeout=timeout,
            ) is not None
        except TimeoutException:
            return False

    def is_classroom_context_preserved(self) -> bool:
        """현재 URL이 QA6_2 전용 클래스룸 컨텍스트를 유지하는지 확인한다."""
        return get_classroom_id() in self.driver.current_url

    def get_visible_home_course_count(self) -> int:
        """클래스 홈 학습 과목 카드에서 현재 보이는 과목 항목 수를 반환한다."""
        return len(self.find_elements_visible(self.HOME_COURSE_ITEM, timeout=10))

    def wait_for_home_course_count_increase(
        self,
        previous_count: int,
        timeout: float = 10,
    ) -> int:
        """더보기 클릭 뒤 클래스 홈의 표시 과목 수가 증가할 때까지 기다린다."""
        def course_count_increased(_: WebDriver) -> int | bool:
            visible_items = self.driver.find_elements(*self.HOME_COURSE_ITEM)
            current_count = sum(
                item.is_displayed()
                for item in visible_items
            )
            return current_count if current_count > previous_count else False

        return WebDriverWait(self.driver, timeout).until(course_count_increased)
