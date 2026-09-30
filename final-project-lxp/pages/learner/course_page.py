import logging
import time

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, Locator

logger = logging.getLogger(__name__)


class LearnCourse(BasePage):
    """학습자의 과목 목록/상세 화면 조작을 담당한다."""

    # 학습 과목 메뉴, 목록 및 수업 동작 Locators
    COURSE_MENU_LINK: Locator = (By.CSS_SELECTOR, "a[aria-label='학습 과목']")
    COURSE_LIST_BUTTON: Locator = (
        By.XPATH,
        "//button[@type='button' and normalize-space()='과목 목록']",
    )
    COURSE_LIST_HEADING: Locator = (
        By.XPATH,
        "//h4[normalize-space()='학습 과목 목록']",
    )
    COURSE_ITEMS: Locator = (
        By.XPATH,
        "//button[.//h6[@aria-rowcount='1']]",
    )
    LESSON_ITEMS: Locator = (
        By.XPATH,
        "//button[.//*[@data-testid='book-open-coverIcon'] "
        "and .//h6[@aria-rowcount='2']]",
    )
    CONTINUE_LEARNING_BUTTON: Locator = (
        By.XPATH,
        "//button[@type='button' and normalize-space()='이어서 학습']",
    )
    LEARNING_END_LINK: Locator = (
        By.XPATH,
        "//main//a[normalize-space()='학습 종료' and contains(@href, '/lectures/')]",
    )
    LEARNING_STATUS_TAB: Locator = (
        By.XPATH,
        "//button[@type='button' and @role='tab'"
        " and normalize-space()='학습 현황']",
    )
    COURSE_DETAIL_TABS: Locator = (
        By.XPATH,
        "//section[.//*[@role='tablist']]//*[@role='tab']",
    )
    STATUS_LABELS: Locator = (
        By.XPATH,
        "//*[contains(normalize-space(), '진행률') or contains(normalize-space(), '실습 자료') "
        "or contains(normalize-space(), '테스트 점수') or contains(normalize-space(), '클래스 평균')]",
    )
    LEARNING_PROGRESS_VALUE: Locator = (
        By.XPATH,
        "//*[normalize-space()='학습 진행률']/parent::div"
        "/following-sibling::div[1]//h6[normalize-space()]",
    )
    AVERAGE_PRACTICE_SCORE_VALUE: Locator = (
        By.XPATH,
        "//*[normalize-space()='평균 실습 자료 점수']/parent::div"
        "/following-sibling::div[1]//h6[normalize-space()]",
    )
    AVERAGE_TEST_SCORE_VALUE: Locator = (
        By.XPATH,
        "//*[normalize-space()='평균 테스트 점수']/parent::div"
        "/following-sibling::div[1]//h6[normalize-space()]",
    )
    PRACTICE_SCORE_SECTION: Locator = (
        By.XPATH,
        "//*[normalize-space()='실습 자료 점수']"
        "/ancestor::div[.//*[contains(@class, 'recharts-responsive-container')]][1]",
    )
    TEST_SCORE_SECTION: Locator = (
        By.XPATH,
        "//*[normalize-space()='테스트 점수']"
        "/ancestor::div[.//*[contains(@class, 'recharts-responsive-container')]][1]",
    )

    def __init__(self, driver: WebDriver, timeout: float = 15) -> None:
        """LearnCourse를 초기화한다.

        Args:
            driver: pytest fixture에서 생성한 학습자 WebDriver.
            timeout: 요소를 기다릴 기본 최대 시간(초).
        """
        super().__init__(driver, timeout)

    @staticmethod
    def _xpath_literal(value: str) -> str:
        """동적 이름을 안전한 XPath 문자열 리터럴로 변환한다."""
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        return "concat(" + ", \"'\", ".join(
            f"'{piece}'" for piece in value.split("'")
        ) + ")"

    def _course_card_locator(self, course_name: str) -> Locator:
        """표시 과목명이 정확히 일치하는 과목 카드 locator를 만든다."""
        return (
            By.XPATH,
            "//button[@type='button' and .//h6[@aria-rowcount='1'"
            f" and normalize-space()={self._xpath_literal(course_name)}]]",
        )

    def _lesson_card_locator(self, lesson_name: str) -> Locator:
        """표시 수업명이 정확히 일치하는 수업 카드 locator를 만든다."""
        return (
            By.XPATH,
            "//button[@type='button'"
            " and .//*[@data-testid='book-open-coverIcon']"
            " and .//h6[@aria-rowcount='2' and normalize-space()="
            f"{self._xpath_literal(lesson_name)}]]",
        )

    def enter_course_menu(self):
        """클래스 사이드바의 [학습 과목] 메뉴를 클릭한다.

        Returns:
            WebElement: 클릭한 학습 과목 메뉴 요소.
        """
        logger.info("클래스 메뉴에서 [학습 과목] 클릭")
        return self.click(self.COURSE_MENU_LINK)

    def _select_item_by_index(
        self,
        locator: Locator,
        index: int,
        item_name: str,
    ) -> WebElement:
        """화면에 표시된 목록에서 지정한 인덱스의 요소를 클릭한다.

        Args:
            locator: 목록 요소를 조회할 Selenium locator.
            index: 선택할 요소의 0부터 시작하는 인덱스. 음수 인덱스도 허용한다.
            item_name: 인덱스 오류 메시지에 표시할 목록 이름.

        Returns:
            WebElement: 클릭한 목록 요소.

        Raises:
            TypeError: index가 정수가 아닌 경우.
            IndexError: index가 표시 요소 목록의 범위를 벗어난 경우.
        """
        if not isinstance(index, int):
            raise TypeError("index는 정수여야 합니다.")

        items = self.find_elements_visible(locator)
        try:
            element = items[index]
        except IndexError as error:
            raise IndexError(
                f"{item_name} 인덱스 범위 초과: "
                f"index={index}, item_count={len(items)}"
            ) from error

        self.scroll_element_into_view(element)
        element.click()
        return element

    def select_course(self, index: int = 0) -> WebElement:
        """학습 과목 목록에서 지정한 인덱스의 과목을 선택한다.

        Args:
            index: 선택할 과목의 0부터 시작하는 인덱스.

        Returns:
            WebElement: 클릭한 과목 카드 요소.
        """
        logger.info("학습 과목 선택: index=%s", index)
        return self._select_item_by_index(
            self.COURSE_ITEMS,
            index,
            "학습 과목",
        )

    def get_course_names(self) -> list[str]:
        """학습 과목 목록에 표시된 비어 있지 않은 과목명을 반환한다."""
        logger.info("학습 과목명 목록 조회")
        names = []
        for item in self.find_elements_visible(self.COURSE_ITEMS):
            heading = item.find_element(By.XPATH, ".//h6[@aria-rowcount='1']")
            name = heading.text.strip()
            if name:
                names.append(name)
        return names

    def select_course_by_name(self, course_name: str) -> WebElement:
        """표시 과목명이 일치하는 과목 카드를 선택한다."""
        logger.info("과목명으로 학습 과목 선택: name=%s", course_name)
        normalized_name = course_name.strip()
        if not normalized_name:
            raise ValueError("course_name은 비어 있을 수 없습니다.")

        return self.click(self._course_card_locator(normalized_name))

    def slowly_scroll_course_list(self, delay: float = 0.5) -> list[WebElement]:
        """학습 과목 목록의 모든 표시 카드를 천천히 순회한다."""
        logger.info("학습 과목 목록 끝까지 스크롤")
        items = self.find_elements_visible(self.COURSE_ITEMS)
        for item in items:
            self.scroll_element_into_view(item)
            time.sleep(delay)
        return items

    def select_first_course_by_continue_state(
        self,
        has_continue: bool,
    ) -> WebElement:
        """[이어서 학습] 노출 여부를 기준으로 첫 번째 과목을 선택한다."""
        logger.info("첫 번째 학습 과목 선택: 이어서 학습 노출=%s", has_continue)
        continue_button = (
            ".//button[@type='button' and normalize-space()='이어서 학습']"
        )
        condition = continue_button if has_continue else f"not({continue_button})"
        locator: Locator = (
            By.XPATH,
            "//button[@type='button' and .//h6[@aria-rowcount='1']"
            f" and {condition}]",
        )
        return self.click(locator)

    def open_learning_status(self) -> WebElement:
        """과목 상세의 [학습 현황] 탭을 연다."""
        logger.info("과목 상세에서 [학습 현황] 열기")
        return self.click(self.LEARNING_STATUS_TAB)

    def get_course_detail_tab_names(self) -> list[str]:
        """과목 상세 상단에 표시된 탭 이름을 DOM 순서로 반환한다."""
        logger.info("과목 상세 탭 이름 조회")
        return [
            tab.text.strip()
            for tab in self.find_elements_visible(self.COURSE_DETAIL_TABS)
            if tab.text.strip()
        ]

    def wait_for_course_list(self) -> tuple[WebElement, list[WebElement]]:
        """학습 과목 목록 제목과 한 개 이상의 과목 항목 노출을 확인한다."""
        logger.info("학습 과목 목록 컨테이너 노출 확인")
        heading = self.wait_for_first_visible(self.COURSE_LIST_HEADING)
        items = WebDriverWait(self.driver, self.default_timeout).until(
            lambda driver: self.find_elements_visible(self.COURSE_ITEMS),
            "학습 과목 목록에 표시된 과목이 없습니다.",
        )
        return heading, items

    def wait_for_course_detail_tabs(self) -> list[str]:
        """과목 상세 탭이 표시될 때까지 기다리고 탭 이름을 반환한다."""
        logger.info("과목 상세 탭 노출 확인")
        return WebDriverWait(self.driver, self.default_timeout).until(
            lambda driver: self.get_course_detail_tab_names() or False,
            "과목 상세 탭이 표시되지 않았습니다.",
        )

    def wait_for_learning_end_link(self) -> WebElement:
        """학습 화면의 [학습 종료] 링크가 표시될 때까지 기다린다."""
        logger.info("학습 화면 [학습 종료] 링크 노출 확인")
        return self.wait_for_first_visible(self.LEARNING_END_LINK)

    def get_learning_status_summary(self) -> dict[str, str]:
        """학습 진행률과 평균 실습·테스트 점수의 표시값을 반환한다."""
        logger.info("학습 현황 요약 값 조회")
        progress = self.wait_for_first_visible(self.LEARNING_PROGRESS_VALUE)
        practice = self.wait_for_first_visible(
            self.AVERAGE_PRACTICE_SCORE_VALUE
        )
        test = self.wait_for_first_visible(self.AVERAGE_TEST_SCORE_VALUE)
        return {
            "learning_progress": progress.text.strip(),
            "average_practice_score": practice.text.strip(),
            "average_test_score": test.text.strip(),
        }

    def wait_for_score_sections(self) -> tuple[WebElement, WebElement]:
        """실습 자료 점수와 테스트 점수 영역이 표시될 때까지 기다린다."""
        logger.info("실습 자료 점수 및 테스트 점수 영역 노출 확인")
        practice = self.wait_for_first_visible(self.PRACTICE_SCORE_SECTION)
        test = self.wait_for_first_visible(self.TEST_SCORE_SECTION)
        return practice, test

    def slowly_scroll_learning_status(self, delay: float = 0.5) -> list[str]:
        """학습 현황의 점수·평균 영역을 천천히 내려가며 표시 텍스트를 수집한다."""
        logger.info("학습 현황 끝까지 스크롤하며 정보 조회")
        status_element = self.wait_for_first_visible(self.STATUS_LABELS)
        scroll_container = self.driver.execute_script(
            """
            let current = arguments[0].parentElement;

            while (current) {
                if (current.scrollHeight > current.clientHeight + 1) {
                    return current;
                }

                current = current.parentElement;
            }

            const candidates = Array.from(
                document.querySelectorAll("body, main, section, div")
            ).filter((element) => {
                const rect = element.getBoundingClientRect();
                return (
                    rect.width > 0 &&
                    rect.height > 0 &&
                    element.scrollHeight > element.clientHeight + 1
                );
            });

            candidates.sort(
                (left, right) =>
                    (right.scrollHeight - right.clientHeight) -
                    (left.scrollHeight - left.clientHeight)
            );

            return (
                candidates[0] ||
                document.scrollingElement ||
                document.documentElement ||
                document.body
            );
            """,
            status_element,
        )
        container_info = self.driver.execute_script(
            """
            return {
                tag: arguments[0].tagName,
                id: arguments[0].id || "",
                className: String(arguments[0].className || ""),
                scrollHeight: arguments[0].scrollHeight,
                clientHeight: arguments[0].clientHeight
            };
            """,
            scroll_container,
        )
        logger.info(
            "학습 현황 스크롤 컨테이너 선택: tag=%s, id=%s, "
            "scrollHeight=%s, clientHeight=%s",
            container_info["tag"],
            container_info["id"],
            container_info["scrollHeight"],
            container_info["clientHeight"],
        )
        self.driver.execute_script(
            "arguments[0].scrollTop = 0;",
            scroll_container,
        )
        previous_height = 0

        for _ in range(100):
            metrics = self.driver.execute_script(
                """
                return {
                    scrollHeight: arguments[0].scrollHeight,
                    clientHeight: arguments[0].clientHeight,
                    scrollTop: arguments[0].scrollTop
                };
                """,
                scroll_container,
            )
            bottom_position = max(
                0,
                metrics["scrollHeight"] - metrics["clientHeight"],
            )
            next_position = min(
                metrics["scrollTop"] + 400,
                bottom_position,
            )

            self.driver.execute_script(
                "arguments[0].scrollTop = arguments[1];",
                scroll_container,
                next_position,
            )
            time.sleep(delay)

            updated_metrics = self.driver.execute_script(
                """
                return {
                    scrollHeight: arguments[0].scrollHeight,
                    clientHeight: arguments[0].clientHeight,
                    scrollTop: arguments[0].scrollTop
                };
                """,
                scroll_container,
            )

            if (
                updated_metrics["scrollTop"]
                >= updated_metrics["scrollHeight"]
                - updated_metrics["clientHeight"]
                and updated_metrics["scrollHeight"] == previous_height
            ):
                break

            previous_height = updated_metrics["scrollHeight"]

        logger.info(
            "학습 현황 스크롤 완료: position=%s, max=%s",
            updated_metrics["scrollTop"],
            updated_metrics["scrollHeight"]
            - updated_metrics["clientHeight"],
        )
        body_text = self.driver.find_element(By.TAG_NAME, "body").text
        return [line.strip() for line in body_text.splitlines() if line.strip()]

    def open_course_list_from_menu(self) -> WebElement:
        """사이드바 [학습 과목]을 클릭하고 과목 목록을 연다.

        사이드바 메뉴 클릭 후 이전 과목 상세가 복원된 경우에만
        [과목 목록]을 클릭해 목록 화면으로 이동한다.

        Returns:
            WebElement: 학습 과목 메뉴 또는 목록 전환에 사용한 요소.
        """
        menu = self.enter_course_menu()
        return self._open_course_list_after_menu(menu)

    def _open_course_list_after_menu(
        self,
        menu: WebElement,
    ) -> WebElement:
        """[학습 과목] 메뉴 클릭 직후 목록 화면을 보장한다.

        이미 과목 목록이면 첫 번째 과목 카드를 반환하고, 과목 상세 화면이면
        [과목 목록] 버튼을 클릭한다.

        Returns:
            WebElement: 메뉴, 목록 제목 또는 클릭한 과목 목록 버튼 요소.
        """
        logger.info("학습 과목 목록 열기")

        def course_page_state(
            driver: WebDriver,
        ) -> tuple[str, WebElement] | bool:
            try:
                list_headings = [
                    element
                    for element in driver.find_elements(
                        *self.COURSE_LIST_HEADING
                    )
                    if element.is_displayed()
                ]
                if list_headings:
                    return "list", list_headings[0]

                course_items = [
                    element
                    for element in driver.find_elements(*self.COURSE_ITEMS)
                    if element.is_displayed()
                ]
                if course_items:
                    return "list", course_items[0]

                list_buttons = [
                    element
                    for element in driver.find_elements(
                        *self.COURSE_LIST_BUTTON
                    )
                    if element.is_displayed()
                ]
                if list_buttons:
                    return "detail", list_buttons[0]

                return False
            except StaleElementReferenceException:
                return False

        page_state, _ = WebDriverWait(
            self.driver,
            self.default_timeout,
        ).until(course_page_state)

        if page_state == "list":
            logger.info("현재 화면이 이미 학습 과목 목록임")
            return menu

        def course_list_is_ready(driver: WebDriver) -> bool:
            try:
                headings_are_visible = any(
                    heading.is_displayed()
                    for heading in driver.find_elements(
                        *self.COURSE_LIST_HEADING
                    )
                )
                items_are_visible = any(
                    item.is_displayed()
                    for item in driver.find_elements(*self.COURSE_ITEMS)
                )
                return headings_are_visible or items_are_visible
            except StaleElementReferenceException:
                return False

        logger.info("과목 상세 화면에서 [과목 목록] 클릭")
        clicked_button = self.click(self.COURSE_LIST_BUTTON)
        try:
            WebDriverWait(
                self.driver,
                min(5, self.default_timeout),
            ).until(course_list_is_ready)
        except TimeoutException:
            list_button_remains = self.find_optional_visible(
                self.COURSE_LIST_BUTTON,
                timeout=1,
            )
            if list_button_remains is not None:
                logger.warning(
                    "첫 클릭 후 과목 목록이 열리지 않아 한 번 재클릭합니다."
                )
                clicked_button = self.click(self.COURSE_LIST_BUTTON)

            WebDriverWait(self.driver, self.default_timeout).until(
                course_list_is_ready
            )

        return clicked_button

    def select_lesson(self, index: int = 0) -> WebElement:
        """수업 목록에서 지정한 인덱스의 수업을 선택한다.

        Args:
            index: 선택할 수업의 0부터 시작하는 인덱스.

        Returns:
            WebElement: 클릭한 수업 요소.
        """
        logger.info("과목 상세에서 수업 선택: index=%s", index)
        return self._select_item_by_index(
            self.LESSON_ITEMS,
            index,
            "수업",
        )

    def select_lesson_by_name(self, lesson_name: str) -> WebElement:
        """과목 상세에서 표시 수업명이 정확히 일치하는 수업을 선택한다.

        Args:
            lesson_name: 선택할 수업의 표시 명칭.

        Returns:
            WebElement: 클릭한 수업 요소.

        Raises:
            ValueError: 수업명이 비어 있는 경우.
            LookupError: 일치하는 표시 수업을 찾지 못한 경우.
        """
        logger.info("수업명으로 수업 선택: name=%s", lesson_name)
        normalized_name = lesson_name.strip()
        if not normalized_name:
            raise ValueError("lesson_name은 비어 있을 수 없습니다.")

        return self.click(self._lesson_card_locator(normalized_name))

    def get_visible_lessons(self) -> list[WebElement]:
        """현재 과목 상세에 표시된 수업 콘텐츠 목록을 반환한다."""
        logger.info("과목 상세의 표시 수업 목록 조회")
        return self.find_elements_visible(self.LESSON_ITEMS)

    def continue_learning(self) -> WebElement:
        """과목 상세의 [이어서 학습] 버튼을 클릭한다."""
        logger.info("이어서 학습 실행")
        return self.click(self.CONTINUE_LEARNING_BUTTON)
