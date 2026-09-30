"""교육자 수업 일정 관리 화면을 담당하는 Page Object."""

import logging
import os

from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, Locator

logger = logging.getLogger(__name__)


class EducatorSchedulePage(BasePage):
    """교육자의 수업 일정 생성, 수정, 삭제 및 캘린더 반영 화면을 제어한다."""

    # 메인 헤더 영역 > 만들기 버튼
    SCHEDULE_CREATE_BUTTON: Locator = (
        By.XPATH,
        "//main//button[contains(@class, 'MuiButton-contained') and normalize-space()='만들기']",
    )
    # 일정 생성/수정 다이얼로그 (role='dialog')
    SCHEDULE_DIALOG: Locator = (
        By.XPATH,
        "//div[@role='dialog'][.//input[@name='summary']]",
    )
    SCHEDULE_EDITOR: Locator = (
        By.XPATH,
        "//div[@role='dialog'][.//input[@name='summary']]"
        " | //div[contains(@class, 'MuiPopover-paper')]"
        "[.//h2[normalize-space()='수업 일정 수정'] and .//input[@name='summary']]",
    )
    # 생성 다이얼로그와 수정 팝오버의 제목 input을 각각 컨테이너로 한정한다.
    SCHEDULE_CREATE_TITLE_INPUT: Locator = (
        By.XPATH,
        "//div[@role='dialog'][.//input[@name='summary']]"
        "//input[@name='summary']",
    )
    SCHEDULE_EDIT_POPOVER: Locator = (
        By.XPATH,
        "//div[contains(@class, 'MuiPopover-paper')]"
        "[.//h2[normalize-space()='수업 일정 수정'] and .//input[@name='summary']]",
    )
    SCHEDULE_EDIT_TITLE_INPUT: Locator = (
        By.XPATH,
        "//div[contains(@class, 'MuiPopover-paper')]"
        "[.//h2[normalize-space()='수업 일정 수정']]"
        "//input[@name='summary']",
    )
    # 일정 다이얼로그 > 저장/만들기 버튼
    SCHEDULE_EDITOR_SAVE_BUTTON: Locator = (
        By.XPATH,
        "//div[@role='dialog'][.//input[@name='summary']]"
        "//button[normalize-space()='만들기' or normalize-space()='저장']"
        " | //div[contains(@class, 'MuiPopover-paper')]"
        "[.//h2[normalize-space()='수업 일정 수정'] and .//input[@name='summary']]"
        "//button[normalize-space()='저장']",
    )
    SCHEDULE_EDITOR_CANCEL_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'MuiPopover-paper')]"
        "[.//h2[normalize-space()='수업 일정 수정']]"
        "//button[normalize-space()='취소']",
    )
    # 캘린더 일정 클릭 시 나타나는 팝오버
    SCHEDULE_POPOVER: Locator = (
        By.CSS_SELECTOR,
        "div.MuiPopover-paper",
    )
    POPOVER_EDIT_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'MuiPopover-paper')]"
        "//button[@aria-label='수정' or contains(@aria-label, '수정') "
        "or .//*[contains(@data-testid, 'pen') or contains(@data-icon, 'pen') or contains(@class, 'edit')]]",
    )
    # 팝오버 > 삭제 버튼 (trash 아이콘)
    POPOVER_DELETE_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'MuiPopover-paper')]"
        "//button[@aria-label='삭제' or contains(@aria-label, '삭제') "
        "or .//*[contains(@data-testid, 'trash') or contains(@data-icon, 'trash') or contains(@class, 'delete')]]",
    )
    # 삭제 확인 다이얼로그 확인 버튼
    DELETE_CONFIRM_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-dialog') or contains(@class, 'MuiDialog') or @role='dialog']"
        "[.//*[contains(normalize-space(), '일정 삭제') or contains(normalize-space(), '삭제')]]"
        "//button[(contains(@class, 'contained') or contains(@class, 'MuiButton-root') or contains(@class, 'eb-button') or @type='button') "
        "and (normalize-space()='삭제' or normalize-space()='확인' or contains(., '삭제')) "
        "and not(contains(., '취소'))]",
    )

    def __init__(self, driver: WebDriver, timeout: float = 15) -> None:
        super().__init__(driver, timeout)

    def _schedule_event_locator(self, title: str) -> Locator:
        """보이는 캘린더 그리드에서 정확한 제목의 일정 카드를 찾는다.

        일정 화면은 ``main`` 밖에 렌더링되는 경우가 있어, main 범위로 한정하면
        사람이 보는 캘린더 항목을 놓칠 수 있다. 대신 시맨틱 grid 영역과 FullCalendar
        이벤트 구조를 조합하고, 내부 제목 span의 완전 일치로 다른 QA 일정을 배제한다.
        """
        title_literal = self._xpath_literal(title)
        return (
            By.XPATH,
            "//*[contains(concat(' ', normalize-space(@class), ' '), ' fc-event ')]"
            "[normalize-space()="
            f"{title_literal} or .//*[normalize-space()={title_literal}] "
            f"or @data-event-title={title_literal}]",
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

    def _get_visible_dialog_save_button(self) -> WebElement:
        """현재 열린 생성/수정 편집기의 표시·활성 저장 버튼을 반환한다."""
        def _find_displayed_save(_: WebDriver):
            for b in self.driver.find_elements(*self.SCHEDULE_EDITOR_SAVE_BUTTON):
                if b.is_displayed() and b.is_enabled():
                    return b
            return False
        return WebDriverWait(self.driver, 10).until(_find_displayed_save)

    def _fill_schedule_title(
        self,
        input_locator: Locator,
        title: str,
        editor_name: str,
    ) -> WebElement:
        """지정한 생성/수정 편집기 안의 제목 input에 실제 키보드 입력을 수행한다.

        수정 팝오버는 기존 입력값을 React 상태로 유지하므로, Selenium의 일반
        ``send_keys`` 대신 ActionChains로 실제 클릭과 키 조합을 한 번에 전달한다.
        JavaScript로 값만 주입하지 않고 사람이 수행하는 전체 선택·삭제·입력
        동작을 그대로 사용한다.
        """
        from selenium.webdriver.common.action_chains import ActionChains
        from selenium.webdriver.common.keys import Keys

        element = self.wait_for_visible(input_locator, timeout=self.default_timeout)
        self.scroll_element_into_view(element, block="center", timeout=2)
        ActionChains(self.driver).move_to_element(element).click().key_down(
            Keys.CONTROL
        ).send_keys("a").key_up(Keys.CONTROL).send_keys(
            Keys.BACKSPACE
        ).send_keys(title).perform()

        def title_applied(_: WebDriver) -> bool:
            return any(
                candidate.is_displayed()
                and candidate.is_enabled()
                and candidate.get_attribute("value") == title
                for candidate in self.driver.find_elements(*input_locator)
            )

        try:
            WebDriverWait(self.driver, self.default_timeout).until(
                title_applied,
                message=f"{editor_name} 일정 제목 입력값이 반영되지 않았습니다.",
            )
        except TimeoutException as error:
            visible_values = [
                candidate.get_attribute("value")
                for candidate in self.driver.find_elements(*input_locator)
                if candidate.is_displayed()
            ]
            logger.error(
                "일정 제목 입력 확인 실패: editor=%s, expected=%r, visible_values=%r, url=%s",
                editor_name,
                title,
                visible_values,
                self.driver.current_url,
            )
            raise TimeoutException(
                f"{editor_name} 일정 제목 입력값이 반영되지 않았습니다."
            ) from error

        return element

    def _click_visible_element(self, element: WebElement) -> WebElement:
        """현재 화면에 보이는 요소를 중앙으로 옮긴 뒤 일반 클릭한다."""
        self.scroll_element_into_view(element, block="center", timeout=2)
        try:
            element.click()
        except ElementClickInterceptedException:
            logger.info("일정 요소 클릭 가림 발생으로 JavaScript 클릭 fallback 수행")
            self.click_with_javascript(element)
        return element

    def _wait_for_schedule_or_reauth(self, timeout: float) -> str:
        """일정 화면 또는 재인증 화면 중 먼저 도착한 상태를 반환한다."""
        def destination(driver: WebDriver) -> str | bool:
            current_url = driver.current_url.lower()
            if "accounts" in current_url or "signin" in current_url:
                return "reauth"
            if any(
                element.is_displayed()
                for element in driver.find_elements(*self.SCHEDULE_CREATE_BUTTON)
            ):
                return "schedule"
            return False

        return WebDriverWait(self.driver, timeout).until(destination)

    def navigate_to_schedule_page(self, url: str) -> None:
        """일정 관리 페이지로 이동하고 늦게 뜨는 재인증을 1회 처리한다."""
        self.open_url(url)
        destination = self._wait_for_schedule_or_reauth(timeout=15)
        if destination != "reauth":
            return

        logger.info("일정 URL 이동 후 재인증 화면 감지")
        from pages.login_page import LoginPage

        LoginPage(self.driver).handle_reauth_if_present(
            source="pages.educator.schedule_page",
            reason="schedule_direct_navigation",
        )
        destination = self._wait_for_schedule_or_reauth(timeout=15)
        if destination == "reauth":
            raise RuntimeError("일정 URL 이동 후 재인증 화면이 계속 표시됩니다.")

    def open_schedule_create_dialog(self) -> WebElement:
        """상단 '만들기' 버튼을 클릭해 일정 생성 다이얼로그를 연다."""
        logger.info("일정 생성 다이얼로그 열기")
        self.click(self.SCHEDULE_CREATE_BUTTON)
        return self.wait_for_visible(self.SCHEDULE_DIALOG, timeout=10)

    def create_schedule(self, title: str) -> WebElement:
        """새 일정을 생성하고 캘린더에 표시될 때까지 대기한다."""
        self.open_schedule_create_dialog()
        self._fill_schedule_title(
            self.SCHEDULE_CREATE_TITLE_INPUT,
            title,
            editor_name="생성",
        )
        save_btn = self._get_visible_dialog_save_button()
        self._click_visible_element(save_btn)
        self.wait_for_invisible(self.SCHEDULE_EDITOR, timeout=10)
        return self.wait_for_visible(
            self._schedule_event_locator(title),
            timeout=self.default_timeout,
        )

    def open_schedule_popover(self, title: str) -> WebElement:
        """캘린더에서 지정한 일정 항목을 클릭하여 상세 팝오버를 연다."""
        logger.info("일정 상세 팝오버 열기: title=%s", title)
        event_el = self.wait_for_visible(self._schedule_event_locator(title), timeout=10)
        self.click_with_javascript(event_el)
        return self.wait_for_visible(self.SCHEDULE_POPOVER, timeout=10)

    def edit_schedule_title(self, current_title: str, new_title: str) -> None:
        """캘린더에서 지정한 일정을 선택하고 제목을 수정한 뒤 저장한다."""
        self.open_schedule_popover(current_title)
        edit_btn = self.wait_for_visible(self.POPOVER_EDIT_BUTTON, timeout=10)
        self._click_visible_element(edit_btn)
        self.wait_for_visible(self.SCHEDULE_EDIT_POPOVER, timeout=10)
        self._fill_schedule_title(
            self.SCHEDULE_EDIT_TITLE_INPUT,
            new_title,
            editor_name="수정",
        )
        save_btn = self._get_visible_dialog_save_button()
        self._click_visible_element(save_btn)
        self.wait_for_invisible(self.SCHEDULE_EDITOR, timeout=10)
        self.wait_for_visible(
            self._schedule_event_locator(new_title),
            timeout=self.default_timeout,
        )

    def close_schedule_editor_if_present(self) -> None:
        """실패 복구 시 보이는 수정 팝오버만 취소한다."""
        cancel_button = self.find_optional_visible(
            self.SCHEDULE_EDITOR_CANCEL_BUTTON,
            timeout=2,
        )
        if cancel_button is not None:
            self._click_visible_element(cancel_button)
            self.wait_for_invisible(self.SCHEDULE_EDITOR, timeout=5)

    def delete_schedule(self, title: str) -> None:
        """캘린더에서 지정한 일정을 찾아 삭제한다."""
        logger.info("일정 삭제 시작: title=%s", title)
        self.open_schedule_popover(title)
        self.click(self.POPOVER_DELETE_BUTTON, timeout=10)
        confirm_button = self.find_optional_visible(
            self.DELETE_CONFIRM_BUTTON,
            timeout=3,
        )
        if confirm_button is not None:
            self._click_visible_element(confirm_button)
        self.wait_until_schedule_removed(title, timeout=10)

    def is_schedule_listed(self, title: str) -> bool:
        """캘린더/목록에 해당 제목의 일정이 표시되는지 확인한다."""
        return self.find_optional_visible(self._schedule_event_locator(title), timeout=5) is not None

    def wait_until_schedule_removed(self, title: str, timeout: float = 10) -> bool:
        """캘린더/목록에서 지정한 제목의 일정이 완전히 사라질 때까지 대기한다."""
        return self.wait_for_invisible(self._schedule_event_locator(title), timeout=timeout)
