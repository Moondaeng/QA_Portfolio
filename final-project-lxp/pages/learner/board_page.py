import logging
from urllib.parse import urlparse

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, Locator

logger = logging.getLogger(__name__)


class LearnerBoardPage(BasePage):
    """학습자의 게시판 조회/작성 화면 조작을 담당한다."""

    # 게시판 메뉴, 글쓰기 및 게시글 입력 Locators
    BOARD_MENU: Locator = (By.CSS_SELECTOR, "a[aria-label='게시판']")
    HOME_NEW_POST_BUTTON: Locator = (
        By.XPATH,
        "//button[normalize-space()='새 게시글 쓰기']",
    )
    BOARD_WRITE_BUTTON: Locator = (
        By.XPATH,
        "//button[normalize-space()='글쓰기']",
    )
    TITLE_INPUT: Locator = (By.CSS_SELECTOR, "input[name='title']")
    CONTENT_INPUT: Locator = (By.CSS_SELECTOR, "[role='textbox'][contenteditable='true']")
    SUBMIT_BUTTON: Locator = (
        By.XPATH,
        "//button[@type='submit' and normalize-space()='저장']",
    )
    FIRST_POST_TITLE_CELL: Locator = (
        By.XPATH,
        "(//main//tbody/tr[td][1]/td[1])[1]",
    )
    BOARD_TABLE: Locator = (
        By.XPATH,
        "//main//table[.//thead//th[normalize-space()='제목']]",
    )
    POST_DETAIL_SECTION: Locator = (
        By.XPATH,
        "//section[.//h4[normalize-space()] and .//time[@datetime]]",
    )
    REQUIRED_TITLE_LABEL: Locator = (
        By.XPATH,
        "//label[contains(normalize-space(), '제목')"
        " and .//span[@aria-hidden='true' and contains(., '*')]]",
    )
    REQUIRED_CONTENT_LABEL: Locator = (
        By.XPATH,
        "//label[contains(normalize-space(), '내용')"
        " and .//span[@aria-hidden='true' and contains(., '*')]]",
    )

    def __init__(self, driver: WebDriver, timeout: float = 15) -> None:
        """LearnerBoardPage를 초기화한다.

        Args:
            driver: pytest fixture에서 생성한 학습자 WebDriver.
            timeout: 요소를 기다릴 기본 최대 시간(초).
        """
        super().__init__(driver, timeout)

    def open_board(self):
        """클래스 사이드바의 [게시판] 메뉴를 클릭한다.

        Returns:
            WebElement: 클릭한 게시판 메뉴 요소.
        """
        logger.info("클래스 메뉴에서 게시판 열기")
        return self.click(self.BOARD_MENU)

    def wait_for_board_url(self, expected_url: str) -> str:
        """게시판 이동 후 현재 URL 경로가 기대 경로와 일치할 때까지 기다린다."""
        expected_path = urlparse(expected_url).path.rstrip("/")
        logger.info("게시판 URL 이동 확인: expected_path=%s", expected_path)

        def board_path_matches(driver: WebDriver) -> str | bool:
            current_url = driver.current_url
            current_path = urlparse(current_url).path.rstrip("/")
            return current_url if current_path == expected_path else False

        return WebDriverWait(self.driver, self.default_timeout).until(
            board_path_matches,
            f"게시판 URL로 이동하지 않았습니다: expected_path={expected_path}",
        )

    def wait_for_board_table(self) -> WebElement:
        """제목 헤더가 있는 게시판 목록 테이블이 표시될 때까지 기다린다."""
        logger.info("게시판 목록 테이블 노출 확인")
        return self.wait_for_first_visible(self.BOARD_TABLE)

    def open_write_from_home(self):
        """버튼 위치로 이동한 뒤 클릭하고 게시글 작성 폼을 기다린다.

        Returns:
            WebElement: 클릭한 새 게시글 쓰기 버튼 요소.
        """
        logger.info("클래스 홈의 [새 게시글 쓰기] 위치로 이동 및 대기")

        button = self.click_when_position_stable(self.HOME_NEW_POST_BUTTON)
        logger.info("[새 게시글 쓰기] 클릭 완료, 작성 폼 대기")
        try:
            self.wait_for_first_visible(self.TITLE_INPUT)
            self.wait_for_first_visible(self.CONTENT_INPUT)
        except TimeoutException as error:
            raise TimeoutException(
                "[새 게시글 쓰기] 클릭 후 작성 폼이 표시되지 않았습니다."
            ) from error
        logger.info("게시글 작성 폼 준비 완료")
        return button

    def open_write_from_board(self):
        """게시판 목록의 [글쓰기] 버튼을 클릭한다.

        Returns:
            WebElement: 클릭한 글쓰기 버튼 요소.
        """
        logger.info("게시판 목록에서 [글쓰기] 클릭")
        return self.click(self.BOARD_WRITE_BUTTON)

    def open_write_from_board_if_available(
        self,
        timeout: float = 5,
    ):
        """게시판 목록에 [글쓰기] 버튼이 있을 때만 클릭한다.

        비로그인 사용자가 게시판 URL 접근 단계에서 로그인 화면으로
        리다이렉트되면 글쓰기 버튼이 없으므로 None을 반환한다.

        Args:
            timeout: 글쓰기 버튼을 기다릴 최대 시간(초).

        Returns:
            WebElement | None: 클릭한 글쓰기 버튼 또는 버튼이 없으면 None.
        """
        logger.info("게시판 [글쓰기] 버튼이 있으면 클릭")
        try:
            return self.click(self.BOARD_WRITE_BUTTON, timeout)
        except TimeoutException:
            logger.debug("게시판 [글쓰기] 버튼이 표시되지 않음")
            return None

    @staticmethod
    def _xpath_literal(value: str) -> str:
        """문자열을 XPath 리터럴로 변환한다."""
        if "'" not in value:
            return f"'{value}'"
        if '"' not in value:
            return f'"{value}"'
        return "concat(" + ", \"'\", ".join(
            f"'{part}'" for part in value.split("'")
        ) + ")"

    def _post_detail_locator(self, title: str, content: str) -> Locator:
        """제목과 본문이 정확히 일치하는 게시글 상세 영역 locator를 만든다."""
        return (
            By.XPATH,
            "//section["
            f".//h4[normalize-space()={self._xpath_literal(title)}]"
            " and .//*[@id='markdown']"
            f"//p[normalize-space()={self._xpath_literal(content)}]"
            "]",
        )

    def create_post(self, title: str, content: str) -> None:
        """게시글의 필수 정보를 입력하고 등록 버튼을 클릭한다.

        Args:
            title: 제목 입력란에 입력할 게시글 제목.
            content: 내용 입력란에 입력할 게시글 본문.

        """
        logger.info("게시글 필수 정보 입력 후 등록")
        self.fill_text(self.TITLE_INPUT, title)
        self.fill_text(self.CONTENT_INPUT, content)
        self.click(self.SUBMIT_BUTTON)

    def wait_for_post_detail(
        self,
        title: str,
        content: str,
    ) -> tuple[str, str]:
        """생성 후 상세 화면에서 정확히 일치하는 제목과 본문을 반환한다."""
        logger.info("생성한 게시글 상세 확인: title=%s", title)
        detail = self.wait_for_first_visible(
            self._post_detail_locator(title, content)
        )
        detail_title = detail.find_element(By.TAG_NAME, "h4").text.strip()
        detail_content = detail.find_element(
            By.CSS_SELECTOR,
            "#markdown p",
        ).text.strip()
        return detail_title, detail_content

    def open_first_post(self):
        """게시판 목록의 첫 번째 표시 게시글을 연다."""
        logger.info("게시판의 첫 번째 표시 게시글 열기")
        list_url = self.driver.current_url
        first_post = self.click(self.FIRST_POST_TITLE_CELL)
        WebDriverWait(self.driver, self.default_timeout).until(
            lambda driver: driver.current_url != list_url
        )
        return first_post

    def wait_for_post_detail_section(self) -> WebElement:
        """제목과 작성 시각을 포함한 게시글 상세 영역의 노출을 확인한다."""
        logger.info("게시글 상세 영역 노출 확인")
        return self.wait_for_first_visible(self.POST_DETAIL_SECTION)

    def prepare_missing_required_title(self, content: str) -> WebElement:
        """제목은 비우고 내용만 입력한 뒤 저장 버튼까지 이동한다."""
        logger.info("게시글 제목 누락 상태 준비")
        self.wait_for_first_visible(self.REQUIRED_TITLE_LABEL)
        self.wait_for_first_visible(self.REQUIRED_CONTENT_LABEL)
        title_input = self.wait_for_first_visible(self.TITLE_INPUT)
        title_input.clear()
        self.fill_text(self.CONTENT_INPUT, content)
        save_button = self.wait_for_first_visible(self.SUBMIT_BUTTON)
        self.scroll_element_into_view(save_button, block="end")
        return save_button
