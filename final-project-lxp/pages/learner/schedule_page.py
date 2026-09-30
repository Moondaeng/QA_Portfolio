import logging

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import StaleElementReferenceException

from pages.base_page import BasePage, Locator

logger = logging.getLogger(__name__)


class LearnerSchedulePage(BasePage):
    """학습자의 수업 일정 화면 조작을 담당한다."""

    # 수업 일정 메뉴 Locator
    SCHEDULE_MENU: Locator = (By.CSS_SELECTOR, "a[aria-label='수업 일정']")
    SCHEDULE_CONTAINER: Locator = (
        By.CSS_SELECTOR,
        "[data-view][data-loading='false'] .fc .fc-view-harness",
    )
    TARGET_SCHEDULE: Locator = (
        By.CSS_SELECTOR,
        ".fc a.fc-event",
    )
    SCHEDULE_DETAIL: Locator = (
        By.XPATH,
        "//button[@type='button'"
        " and normalize-space()='라이브 강의실 참여하기']"
        "/ancestor::div[.//h6][1]",
    )

    def __init__(self, driver: WebDriver, timeout: float = 15) -> None:
        """LearnerSchedulePage를 초기화한다.

        Args:
            driver: pytest fixture에서 생성한 학습자 WebDriver.
            timeout: 요소를 기다릴 기본 최대 시간(초).
        """
        super().__init__(driver, timeout)

    def open_schedule_from_menu(self):
        """클래스 사이드바의 [수업 일정] 메뉴를 클릭한다.

        Returns:
            WebElement: 클릭한 수업 일정 메뉴 요소.
        """
        logger.info("클래스 메뉴에서 수업 일정 열기")
        return self.click(self.SCHEDULE_MENU)

    def wait_for_schedule_container(self) -> WebElement:
        """로딩이 끝난 FullCalendar 일정 영역이 표시될 때까지 기다린다."""
        logger.info("수업 일정 컨테이너 노출 확인")
        return self.wait_for_first_visible(self.SCHEDULE_CONTAINER)

    def open_first_schedule(self) -> str:
        """현재 달력의 첫 번째 표시 일정을 열고 선택한 제목을 반환한다."""
        logger.info("현재 달력의 첫 번째 표시 일정 열기")

        def first_visible(driver):
            for element in driver.find_elements(*self.TARGET_SCHEDULE):
                if element.is_displayed() and element.is_enabled():
                    title = element.find_element(By.CSS_SELECTOR, "div[event] span").get_attribute("textContent").strip()
                    if title:
                        return element, title
            return False

        element, title = WebDriverWait(
            self.driver, self.default_timeout,
            ignored_exceptions=(StaleElementReferenceException,),
        ).until(first_visible, "현재 달력에 클릭 가능한 일정이 없습니다.")
        element.click()
        WebDriverWait(self.driver, self.default_timeout).until(
            lambda driver: any(
                panel.is_displayed()
                for panel in driver.find_elements(*self.SCHEDULE_DETAIL)
            )
        )
        return title

    def get_schedule_detail(self) -> tuple[str, list[str]]:
        """표시된 상세 패널의 제목과 정보 행을 반환한다."""
        logger.info("선택한 일정 상세 정보 조회")
        panel = self.wait_for_first_visible(self.SCHEDULE_DETAIL)
        lines = [line.strip() for line in panel.text.splitlines() if line.strip()]
        title = panel.find_element(By.TAG_NAME, "h6").get_attribute("textContent").strip()
        return title, lines
