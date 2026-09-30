import logging
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, Locator

logger = logging.getLogger(__name__)


class LearnClassHome(BasePage):
    """학습자가 클래스룸에 진입할 때 사용하는 Page Object."""

    ENTER_TEAM_PROJECT: Locator = (
        By.XPATH,
        "//a[.//span[normalize-space()='[QA6_2팀] 최종프로젝트']]",
    )
    CLASSROOM_NAVIGATION: Locator = (
        By.CSS_SELECTOR,
        "a[aria-label='학습 과목']",
    )
    COURSE_SECTION: Locator = (
        By.XPATH,
        "//span[normalize-space()='학습 과목']"
        "/ancestor::div[.//ul/li/button[.//h6[@aria-rowcount='2']]][1]",
    )
    COURSE_PREVIEW_ITEMS: Locator = (
        By.XPATH,
        "//span[normalize-space()='학습 과목']"
        "/ancestor::div[.//ul/li/button[.//h6[@aria-rowcount='2']]][1]"
        "//ul/li[./button[.//h6[@aria-rowcount='2']]]",
    )
    COURSE_MORE_BUTTON: Locator = (
        By.XPATH,
        "//span[normalize-space()='학습 과목']"
        "/ancestor::div[.//ul/li/button[.//h6[@aria-rowcount='2']]"
        " and .//button[@type='button' and normalize-space()='더보기']][1]"
        "//button[@type='button' and normalize-space()='더보기']",
    )
    COURSE_VIEW_ALL: Locator = (
        By.XPATH,
        "//span[normalize-space()='학습 과목']"
        "/ancestor::div[.//button[@type='button'"
        " and normalize-space()='전체 보기']][1]"
        "//button[@type='button' and normalize-space()='전체 보기']",
    )
    SCHEDULE_VIEW_ALL: Locator = (
        By.XPATH,
        "//button[(normalize-space()='전체 보기') "
        "and ancestor::*[2][.//*[normalize-space()='수업 일정']]]",
    )
    BOARD_VIEW_ALL: Locator = (
        By.XPATH,
        "//span[contains(@class, 'MuiCardHeader-title') "
        "and normalize-space()='게시판']"
        "/ancestor::div[contains(@class, 'MuiCard-root')][1]"
        "//div[contains(@class, 'MuiCardHeader-action')]"
        "//button[@type='button' and normalize-space()='전체 보기']",
    )

    def __init__(self, driver: WebDriver, timeout: float = 15) -> None:
        """LearnClassHome을 초기화한다.

        Args:
            driver: pytest fixture에서 생성한 학습자 WebDriver.
            timeout: 화면 이동을 기다릴 기본 최대 시간(초).
        """
        super().__init__(driver, timeout)
        self.team_project_url: str | None = None

    def _wait_for_classroom_or_reauth(self) -> str:
        """클래스룸 또는 재인증 화면 중 먼저 도착한 상태를 반환한다.

        Returns:
            str: 클래스룸이면 ``classroom``, 재인증이면 ``reauth``.
        """
        def destination(driver: WebDriver) -> str | bool:
            current_url = driver.current_url.lower()
            if "accounts" in current_url or "signin" in current_url:
                return "reauth"
            navigation_is_visible = any(
                element.is_displayed()
                for element in driver.find_elements(*self.CLASSROOM_NAVIGATION)
            )
            if (
                self.team_project_url
                and self.team_project_url in driver.current_url
                and navigation_is_visible
            ):
                return "classroom"
            return False

        return WebDriverWait(self.driver, self.default_timeout).until(
            destination
        )

    def enter_team_project(self):
        """목록에서 최종프로젝트 클래스를 선택한다.

        Returns:
            WebElement: 클릭한 최종프로젝트 클래스 요소.
        """
        logger.info("[QA6_2팀] 최종프로젝트 클래스 선택")
        element = self.wait_for_first_visible(self.ENTER_TEAM_PROJECT)
        self.team_project_url = element.get_attribute("href")
        element.click()

        try:
            self._wait_for_classroom_or_reauth()
        except TimeoutException:
            # 아직 원래 화면에 머문 경우에만 링크 URL로 한 번 보완 이동한다.
            # 재인증 URL은 위 대기 조건에서 먼저 감지하므로 덮어쓰지 않는다.
            self.open_team_project_url()
            self._wait_for_classroom_or_reauth()
        return element

    def open_team_project_url(self) -> None:
        """마지막으로 선택한 최종프로젝트 클래스 URL로 이동한다.

        Raises:
            RuntimeError: 클래스 링크를 아직 조회하지 않은 경우.
        """
        logger.info("최종프로젝트 클래스 URL로 이동")
        if not self.team_project_url:
            raise RuntimeError("최종프로젝트 클래스 URL이 준비되지 않았습니다.")
        self.open_url(self.team_project_url)

    def wait_until_team_project_open(self, timeout: float = 10) -> bool:
        """재인증이 아닌 최종프로젝트 클래스 URL 진입을 기다린다.

        Args:
            timeout: 클래스룸 진입을 기다릴 최대 시간(초).

        Returns:
            bool: 제한 시간 안에 선택한 클래스룸에 진입하면 True.
        """
        logger.info("최종프로젝트 클래스 진입 완료 대기")
        if not self.team_project_url:
            return False

        try:
            WebDriverWait(self.driver, timeout).until(
                lambda driver: self.team_project_url in driver.current_url
                and "accounts" not in driver.current_url.lower()
                and "signin" not in driver.current_url.lower()
                and any(
                    element.is_displayed()
                    for element in driver.find_elements(
                        *self.CLASSROOM_NAVIGATION
                    )
                )
            )
            return True
        except TimeoutException:
            return False

    def _find_visible_course_previews(self) -> list:
        """현재 DOM에서 화면에 표시된 과목 미리보기를 조회한다."""
        try:
            return [
                item
                for item in self.driver.find_elements(
                    *self.COURSE_PREVIEW_ITEMS
                )
                if item.is_displayed()
            ]
        except StaleElementReferenceException:
            return []

    def get_visible_course_previews(self) -> list:
        """클래스 홈에 현재 표시된 학습 과목 미리보기 목록을 반환한다."""
        logger.info("클래스 홈의 표시 학습 과목 미리보기 조회")
        section = self.wait_for_first_visible(self.COURSE_SECTION)
        self.scroll_element_into_view(section, block="start")

        return self.find_elements_visible(self.COURSE_PREVIEW_ITEMS)

    def expand_all_course_previews(
        self,
        initial_items: list | None = None,
    ) -> list:
        """[더보기]가 사라질 때까지 과목 미리보기를 순차적으로 펼친다."""
        logger.info("학습 과목 [더보기]를 모두 펼치기")
        items = initial_items or self.get_visible_course_previews()

        while True:
            more_button = self.find_optional_visible(
                self.COURSE_MORE_BUTTON,
                timeout=1,
            )
            if more_button is None:
                return items

            previous_count = len(items)
            self.click(self.COURSE_MORE_BUTTON)

            def increased_items(_: WebDriver) -> list | bool:
                current_items = self._find_visible_course_previews()
                return (
                    current_items
                    if len(current_items) > previous_count
                    else False
                )

            items = WebDriverWait(
                self.driver,
                self.default_timeout,
            ).until(increased_items)

    def get_course_preview_texts(self) -> list[str]:
        """모든 과목 미리보기의 비어 있지 않은 표시 텍스트를 반환한다."""
        logger.info("모든 학습 과목 미리보기 텍스트 조회")
        return [
            item.text.strip()
            for item in self.expand_all_course_previews()
            if item.text.strip()
        ]

    def is_course_more_visible(self, scroll_to_section: bool = True) -> bool:
        """학습 과목 영역의 [더보기] 노출 여부를 반환한다."""
        logger.info("학습 과목 [더보기] 노출 여부 확인")
        if scroll_to_section:
            self.get_visible_course_previews()

        return self.find_optional_visible(self.COURSE_MORE_BUTTON, timeout=2) is not None

    def open_all_courses(self):
        """클래스 홈 학습 과목 영역의 [전체 보기]를 클릭한다."""
        logger.info("학습 과목 [전체 보기] 클릭")
        button = self.click(self.COURSE_VIEW_ALL)
        WebDriverWait(self.driver, self.default_timeout).until(
            lambda driver: "courses" in driver.current_url.lower()
        )
        return button

    def open_all_schedules(self):
        """클래스 홈 수업 일정 영역의 [전체 보기]를 클릭한다."""
        logger.info("수업 일정 [전체 보기] 클릭")
        button = self.click(self.SCHEDULE_VIEW_ALL)
        WebDriverWait(self.driver, self.default_timeout).until(
            lambda driver: "schedules" in driver.current_url.lower()
        )
        return button

    def open_all_board_posts(self):
        """클래스 홈 게시판 영역의 [전체 보기]를 클릭한다."""
        logger.info("게시판 [전체 보기] 클릭")
        button = self.click(self.BOARD_VIEW_ALL)
        WebDriverWait(self.driver, self.default_timeout).until(
            lambda driver: "articles" in driver.current_url.lower()
        )
        return button
