"""교육자의 수업 생성 화면을 다루는 Page Object."""

from datetime import datetime
import logging

from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, Locator

logger = logging.getLogger(__name__)


class EducatorLessonPage(BasePage):
    """과목 편집 모드의 일반 수업 생성 다이얼로그 동작을 제공한다."""

    # main(과목 화면) > MUI 버튼 > 수업 추가 > 활성 상태
    LESSON_ADD_BUTTON: Locator = (
        By.XPATH,
        "//main//button[contains(@class, 'MuiButton-root') and @type='button' "
        "and not(@disabled) and normalize-space()='수업 추가']",
    )
    # MUI 포털의 dialog paper > 일반 수업의 제목 input
    LESSON_CREATE_DIALOG: Locator = (
        By.XPATH,
        "//div[contains(@class, 'MuiDialog-paper') and @role='dialog']"
        "[.//input[@name='title' and @type='text']]",
    )
    LESSON_TITLE_INPUT: Locator = (
        By.CSS_SELECTOR,
        "div.MuiDialog-paper[role='dialog'] input[name='title'][type='text']",
    )
    LESSON_DESCRIPTION_INPUT: Locator = (
        By.CSS_SELECTOR,
        "div.MuiDialog-paper[role='dialog'] textarea[name='description']",
    )
    # 다이얼로그(영역) > MUI 저장 버튼(컴포넌트) > button/type/text > disabled 상태
    LESSON_SAVE_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'MuiDialog-paper') and @role='dialog']"
        "[.//input[@name='title' and @type='text']]"
        "//button[contains(@class, 'MuiButton-root') and @type='button' "
        "and normalize-space()='저장']",
    )
    # 수업 목록(main) > 수업 링크(href) > 목록 제목(p) 조합. 제목은 QA 생성 항목 식별에만 사용한다.
    LESSON_STATUS_CHIP: Locator = (
        By.CSS_SELECTOR,
        "span.MuiChip-label",
    )
    # 현재 수업 상세(main) > 제품 표준 button > settings iconname
    CURRENT_LESSON_SETTINGS_BUTTON: Locator = (
        By.XPATH,
        "//main//button[@type='button' and contains(@class, 'eb-button')]"
        "[.//*[@iconname='settings']]",
    )
    # MUI menu(영역) > menuitem(컴포넌트/role) > 삭제 항목
    DELETE_MENU_ITEM: Locator = (
        By.XPATH,
        "//ul[@role='menu']//li[@role='menuitem'][normalize-space()='삭제']",
    )
    DELETE_CONFIRM_DIALOG: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-dialog')]"
        "[.//*[normalize-space()='수업을 삭제하시겠습니까?']]",
    )
    DELETE_CONFIRM_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-dialog')]"
        "[.//*[normalize-space()='수업을 삭제하시겠습니까?']]"
        "//button[contains(@class, 'eb-button') and not(@disabled) "
        "and normalize-space()='확인']",
    )
    # 수업 상세 헤더 > 상태 배지 (공개 / 비공개)
    LESSON_HEADER_STATUS_BADGE: Locator = (
        By.CSS_SELECTOR,
        "main div.eb-course-lecture-header__status__badges div.eb-badge-next",
    )
    # 수업 상세 헤더 > 공개/비공개 전환 버튼
    LESSON_VISIBILITY_TOGGLE_BUTTON: Locator = (
        By.CSS_SELECTOR,
        "main div.eb-course-lecture-header-lecture__action-dropdown button:not([disabled])",
    )
    LESSON_VISIBILITY_CONFIRM_DIALOG: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-dialog') or @role='dialog']"
        "[.//*[contains(normalize-space(), '공개하시겠습니까') or contains(normalize-space(), '비공개하시겠습니까') "
        "or (contains(normalize-space(), '수업') and (contains(normalize-space(), '공개') or contains(normalize-space(), '비공개')))]]",
    )
    LESSON_VISIBILITY_CONFIRM_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-dialog') or @role='dialog']"
        "[.//*[contains(normalize-space(), '공개하시겠습니까') or contains(normalize-space(), '비공개하시겠습니까') "
        "or (contains(normalize-space(), '수업') and (contains(normalize-space(), '공개') or contains(normalize-space(), '비공개')))]]"
        "//button[(contains(@class, 'eb-button') or @type='button') and not(@disabled) and (normalize-space()='확인' or contains(., '확인'))]",
    )
    # 수업 상세 헤더 > 수정하기 버튼
    LESSON_HEADER_EDIT_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-course-lecture-header')]//button[contains(., '수정하기')]",
    )
    # 수업 수정 다이얼로그
    LESSON_EDIT_DIALOG: Locator = (
        By.CSS_SELECTOR,
        "div.MuiDialog-paper[role='dialog']",
    )
    # 수업 수정 > 수업 날짜 input
    LESSON_DATE_INPUT: Locator = (
        By.CSS_SELECTOR,
        "div.MuiDialog-paper[role='dialog'] input[placeholder*='수업 시작일']",
    )
    LESSON_DATE_PICKER_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'MuiDialog-paper') and @role='dialog']"
        "//button[@type='button' and @aria-label='날짜를 선택하세요']"
        "[.//*[@data-testid='CalendarIcon']]",
    )
    LESSON_DATE_PICKER_DIALOG: Locator = (
        By.CSS_SELECTOR,
        "div.MuiDateCalendar-root",
    )
    LESSON_DATE_PICKER_NEXT_MONTH_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'MuiDateCalendar-root')]"
        "//button[.//*[@data-testid='ArrowRightIcon' or @data-testid='ChevronRightIcon'] or "
        "contains(@aria-label, '다음') or contains(@aria-label, 'Next') or "
        "contains(@title, '다음') or contains(@title, 'Next')]",
    )
    LESSON_EDIT_CANCEL_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'MuiDialog-paper') and @role='dialog']"
        "[.//input[contains(@placeholder, '수업 시작일')]]"
        "//button[@type='button' and normalize-space()='취소']",
    )

    def __init__(self, driver: WebDriver, timeout: float = 15) -> None:
        """교육자 수업 생성 화면 객체를 초기화한다."""
        super().__init__(driver, timeout)

    def open_lesson_create_dialog(self) -> WebElement:
        """과목 편집 화면에서 일반 수업 생성 다이얼로그를 연다."""
        self.click(self.LESSON_ADD_BUTTON)
        try:
            return self.wait_for_visible(self.LESSON_CREATE_DIALOG)
        except TimeoutException:
            if not self.find_optional_visible(self.LESSON_ADD_BUTTON, timeout=2):
                raise

            logger.warning("수업 생성 다이얼로그 미표시로 수업 추가 버튼 클릭 재시도")
            self.click_when_position_stable(self.LESSON_ADD_BUTTON, timeout=5)
            return self.wait_for_visible(self.LESSON_CREATE_DIALOG)

    def is_lesson_create_dialog_displayed(self) -> bool:
        """일반 수업 생성 다이얼로그와 제목 입력 필드가 보이는지 확인한다."""
        return self.find_optional_visible(self.LESSON_TITLE_INPUT, timeout=5) is not None

    def is_create_submit_disabled(self) -> bool:
        """필수값이 비어 있을 때 수업 저장 버튼이 비활성인지 반환한다."""
        return not self.wait_for_present(self.LESSON_SAVE_BUTTON).is_enabled()

    @staticmethod
    def _xpath_literal(value: str) -> str:
        """동적 제목을 안전한 XPath 문자열 리터럴로 변환한다."""
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        pieces = value.split("'")
        return "concat(" + ", \"'\", ".join(
            f"'{piece}'" for piece in pieces
        ) + ")"

    def _lesson_link_by_title(self, title: str) -> Locator:
        """수업 목록 안에서 정확한 제목을 가진 수업 링크 locator를 만든다."""
        title_literal = self._xpath_literal(title)
        return (
            By.XPATH,
            "//main//a[contains(@href, '/courses/') and contains(@href, '/lectures/')]"
            f"[.//p[contains(@class, 'MuiTypography') and normalize-space()={title_literal}]]",
        )

    def create_lesson(self, title: str, description: str) -> WebElement:
        """일반 수업을 만들고 저장 완료 후 목록의 생성 항목을 반환한다."""
        self.open_lesson_create_dialog()
        self.fill_text(self.LESSON_TITLE_INPUT, title)
        self.fill_text(self.LESSON_DESCRIPTION_INPUT, description)
        self.click(self.LESSON_SAVE_BUTTON)
        self.wait_for_invisible(self.LESSON_CREATE_DIALOG)
        return self.wait_for_visible(self._lesson_link_by_title(title), timeout=10)

    def is_lesson_listed(self, title: str) -> bool:
        """수업 목록에 정확한 제목의 수업이 보이는지 반환한다."""
        return self.find_optional_visible(self._lesson_link_by_title(title), timeout=5) is not None

    def open_lesson_by_title(self, title: str) -> None:
        """과목 편집 화면의 수업 목록에서 제목이 일치하는 수업을 연다.

        상위 수업을 먼저 열어 하위 수업 목록을 표시한 뒤 호출하면, 직접 URL 접근으로
        과목 편집 상태가 풀리는 문제 없이 하위 수업의 자료 관리 화면으로 진입할 수 있다.
        """
        self.wait_for_visible(self._lesson_link_by_title(title), timeout=10)
        self.click(self._lesson_link_by_title(title))

    def open_nested_lesson_by_titles(self, parent_title: str, child_title: str) -> None:
        """상위 수업을 필요할 때만 연 뒤 지정 하위 수업으로 진입한다."""
        self.wait_for_visible(self._lesson_link_by_title(parent_title), timeout=10)
        if not self.is_lesson_listed(child_title):
            self.open_lesson_by_title(parent_title)
            self.wait_for_visible(self._lesson_link_by_title(child_title), timeout=10)
        self.open_lesson_by_title(child_title)

    def get_lesson_status(self, title: str) -> str:
        """목록의 지정 수업 카드에서 공개 상태 라벨을 반환한다."""
        lesson_link = self.wait_for_visible(self._lesson_link_by_title(title), timeout=10)
        return lesson_link.find_element(*self.LESSON_STATUS_CHIP).text.strip()

    def delete_current_lesson(self) -> None:
        """현재 수업의 설정 메뉴에서 삭제를 실행하고 필요 시 확인한다.

        호출자는 반드시 이 메서드 전에 생성한 QA 전용 수업의 상세 화면에 있어야 한다.
        """
        self.click(self.CURRENT_LESSON_SETTINGS_BUTTON)
        self.click(self.DELETE_MENU_ITEM)
        if self.find_optional_visible(self.DELETE_CONFIRM_DIALOG, timeout=3):
            self.click(self.DELETE_CONFIRM_BUTTON)

    def wait_until_lesson_removed(self, title: str) -> bool:
        """목록에서 지정한 QA 수업이 사라질 때까지 기다린다."""
        locator = self._lesson_link_by_title(title)

        def _check_removed(_: WebDriver) -> bool:
            for element in self.driver.find_elements(*locator):
                try:
                    if element.is_displayed():
                        return False
                except StaleElementReferenceException:
                    continue
            return True

        return WebDriverWait(self.driver, 10).until(_check_removed)

    def get_current_lesson_visibility_badge_text(self) -> str:
        """현재 열려 있는 수업의 상세 헤더 상태 배지 텍스트(공개/비공개)를 반환한다."""
        badge = self.wait_for_visible(self.LESSON_HEADER_STATUS_BADGE, timeout=10)
        return badge.text.strip()

    def _lesson_visibility_menu_item(self, current_status: str) -> Locator:
        """현재 상태와 반대되는 화면 표시 메뉴 항목 locator를 만든다."""
        normalized_status = current_status.strip()
        if normalized_status == "비공개":
            keyword = "공개"
        elif normalized_status == "공개":
            keyword = "비공개"
        else:
            raise ValueError(f"알 수 없는 수업 공개 상태입니다: {current_status!r}")
        return (
            By.XPATH,
            f"//ul[contains(@class, 'ant-menu')]//li[contains(@class, 'ant-menu-item') and contains(., '{keyword}')]",
        )

    def toggle_current_lesson_visibility(self) -> str:
        """현재 수업의 공개/비공개 상태를 전환하고 전환 후 배지 텍스트를 반환한다."""
        previous_status = self.get_current_lesson_visibility_badge_text()
        self.click(self.LESSON_VISIBILITY_TOGGLE_BUTTON)
        self.click(self._lesson_visibility_menu_item(previous_status), timeout=5)
        if self.find_optional_visible(self.LESSON_VISIBILITY_CONFIRM_DIALOG, timeout=3):
            self.click(self.LESSON_VISIBILITY_CONFIRM_BUTTON)
            self.wait_for_invisible(self.LESSON_VISIBILITY_CONFIRM_DIALOG, timeout=5)
        return WebDriverWait(self.driver, 10).until(
            lambda _: (
                status
                if (status := self.get_current_lesson_visibility_badge_text())
                and status != previous_status
                else False
            )
        )

    def open_lesson_edit_dialog(self) -> WebElement:
        """현재 수업의 수정 다이얼로그를 연다."""
        self.click(self.LESSON_HEADER_EDIT_BUTTON)
        return self.wait_for_visible(self.LESSON_EDIT_DIALOG, timeout=10)

    def is_lesson_edit_dialog_displayed(self) -> bool:
        """수업 수정 다이얼로그가 화면에 보이는지 확인한다."""
        return self.find_optional_visible(self.LESSON_EDIT_DIALOG, timeout=5) is not None

    def enter_lesson_date(self, date_str: str) -> WebElement:
        """읽기 전용 날짜 필드를 열어 달력에서 목표 날짜를 선택한다."""
        digits_only = "".join(filter(str.isdigit, date_str))
        target = datetime.strptime(digits_only, "%Y%m%d")
        today = datetime.now()
        month_delta = (target.year - today.year) * 12 + target.month - today.month
        if month_delta < 0:
            raise ValueError("수업 날짜는 현재 달보다 이전일 수 없습니다.")

        elem = self.wait_for_visible(self.LESSON_DATE_INPUT, timeout=10)
        logger.info(
            "수업 날짜 선택기 열기: target=%s, readonly=%s, disabled=%s",
            target.strftime("%Y.%m.%d"),
            elem.get_attribute("readonly"),
            elem.get_attribute("disabled"),
        )
        self.click_when_position_stable(self.LESSON_DATE_PICKER_BUTTON, timeout=10)
        self.wait_for_visible(self.LESSON_DATE_PICKER_DIALOG, timeout=10)

        for _ in range(month_delta):
            self.click(self.LESSON_DATE_PICKER_NEXT_MONTH_BUTTON, timeout=5)

        target_day_button: Locator = (
            By.XPATH,
            "//div[contains(@class, 'MuiDateCalendar-root')]"
            "//button[@role='gridcell' and contains(@class, 'MuiPickersDay-root') "
            f"and not(@disabled) and normalize-space()='{target.day}']",
        )
        self.click(target_day_button, timeout=10)
        self.wait_for_invisible(self.LESSON_DATE_PICKER_DIALOG, timeout=10)
        logger.info("수업 날짜 달력 선택 완료: target=%s", target.strftime("%Y.%m.%d"))
        return elem

    def get_lesson_date_value(self) -> str:
        """수업 수정 다이얼로그의 수업 날짜 입력값을 반환한다."""
        elem = self.wait_for_visible(self.LESSON_DATE_INPUT, timeout=10)
        return elem.get_attribute("value") or ""

    def save_lesson_edit(self) -> None:
        """수업 수정 다이얼로그의 저장 버튼을 클릭하고 모달이 닫힐 때까지 대기한다."""
        self.click(self.LESSON_SAVE_BUTTON)
        self.wait_for_invisible(self.LESSON_EDIT_DIALOG, timeout=10)

    def close_lesson_edit_dialog(self) -> None:
        """열린 수업 수정 다이얼로그를 취소하고 닫힌 상태까지 기다린다."""
        if self.find_optional_visible(self.LESSON_DATE_PICKER_DIALOG, timeout=2):
            self.click(self.LESSON_DATE_PICKER_BUTTON, timeout=5)
            self.wait_for_invisible(self.LESSON_DATE_PICKER_DIALOG, timeout=5)
        if self.is_lesson_edit_dialog_displayed():
            self.click(self.LESSON_EDIT_CANCEL_BUTTON)
            self.wait_for_invisible(self.LESSON_EDIT_DIALOG, timeout=10)
