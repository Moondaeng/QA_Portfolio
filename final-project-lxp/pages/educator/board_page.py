import logging
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
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.base_page import BasePage, Locator

logger = logging.getLogger(__name__)


class EducatorBoardPage(BasePage):
    """교육자 클래스룸 게시판 Page Object.

    게시글 목록 조회, 일반/공지 게시글 작성, 게시글 상세 조회 및 수정 동작을 제공한다.
    """

    # 게시판 목록 및 버튼 Locators
    # 화면 전체가 아닌 main 영역의 게시판 요소를 기준으로 탐색한다.
    WRITE_POST_BUTTON: Locator = (
        By.XPATH,
        "//main//button[contains(., '글쓰기') or contains(., '새 글')]"
        " | //main//a[contains(., '글쓰기')]",
    )
    POST_ITEM: Locator = (
        By.XPATH,
        "//main//table//tbody//tr//td[1]//*[self::li or contains(@class, 'MuiListItemText') or self::a or @role='button']"
        " | //main//table//tbody//tr//td[1]"
        " | //main//ul[contains(@class, 'MuiList-root')]//div[@role='button']",
    )
    # 게시글 작성 및 수정 입력창 Locators
    TITLE_INPUT: Locator = (
        By.CSS_SELECTOR,
        "main input[name='title'][type='text']",
    )
    CONTENT_INPUT: Locator = (
        By.CSS_SELECTOR,
        "main [role='textbox'][data-lexical-editor='true'][contenteditable='true']",
    )
    INSTITUTION_EDUCATOR_ONLY_CHECKBOX: Locator = (
        By.CSS_SELECTOR,
        "main input[name='isSecret'][type='checkbox']",
    )
    SUBMIT_BUTTON: Locator = (
        By.XPATH,
        "//main//button[contains(., '등록') or contains(., '저장') "
        "or contains(., '게시')]",
    )
    EDIT_BUTTON: Locator = (
        By.XPATH,
        "//ul[@role='menu']//li[@role='menuitem'][contains(., '수정')] | //ul[@role='menu']//button[@role='menuitem'][contains(., '수정')]",
    )
    DELETE_BUTTON: Locator = (
        By.XPATH,
        "//ul[@role='menu']//li[@role='menuitem'][contains(., '삭제')] | //ul[@role='menu']//button[@role='menuitem'][contains(., '삭제')]",
    )
    DELETE_CONFIRM_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-dialog') or contains(@class, 'MuiDialog') or contains(@class, 'MuiModal') or @role='dialog']"
        "[.//*[contains(normalize-space(), '삭제')]]"
        "//button[(contains(@class, 'contained') or contains(@class, 'MuiButton-root') or contains(@class, 'eb-button') or @type='button') "
        "and (normalize-space()='삭제' or normalize-space()='확인' or contains(., '삭제') or contains(., '확인')) "
        "and not(contains(., '취소'))]",
    )

    # 게시글 상세 화면 Locators
    DETAIL_TITLE: Locator = (
        By.CSS_SELECTOR,
        "#boardArticleContent h4",
    )
    DETAIL_CONTENT: Locator = (
        By.CSS_SELECTOR,
        "#boardArticleContent #markdown",
    )
    ARTICLE_MENU_BUTTON: Locator = (
        By.CSS_SELECTOR,
        "#boardArticleContent #boardMenu button[aria-label='more']",
    )

    def __init__(self, driver: WebDriver, timeout: float = 15) -> None:
        """EducatorBoardPage를 초기화한다."""
        super().__init__(driver, timeout)

    def click_write_button(self) -> WebElement:
        """[글쓰기] 버튼을 클릭하여 작성 폼으로 이동한다."""
        logger.info("게시판 [글쓰기] 버튼 클릭")
        return self.click(self.WRITE_POST_BUTTON)

    def enter_title(self, title: str) -> WebElement:
        """게시글 제목을 입력한다."""
        from selenium.webdriver.common.keys import Keys

        logger.info("게시글 제목 입력: %s", title)
        element = self.wait_for_clickable(self.TITLE_INPUT)
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.BACKSPACE)
        element.send_keys(title)
        WebDriverWait(self.driver, self.default_timeout).until(
            lambda _: element.get_attribute("value") == title,
            message="게시글 제목 입력값이 반영되지 않았습니다.",
        )
        element.send_keys(Keys.TAB)
        return element

    def enter_content(self, content: str) -> WebElement:
        """게시글 본문을 입력한다."""
        from selenium.webdriver.common.keys import Keys

        logger.info("게시글 본문 입력: %s", content)
        element = self.wait_for_clickable(self.CONTENT_INPUT)
        try:
            element.click()
        except ElementClickInterceptedException:
            logger.info("본문 입력 요소 클릭 가림 발생으로 JavaScript 클릭 시도")
            self.click_with_javascript(element)
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.BACKSPACE)
        element.send_keys(content)
        WebDriverWait(self.driver, self.default_timeout).until(
            lambda _: content in (element.get_attribute("textContent") or "").strip(),
            message="게시글 본문 입력값이 편집기에 반영되지 않았습니다.",
        )
        element.send_keys(Keys.TAB)
        return element

    def enable_institution_educator_only(self) -> None:
        """게시글을 기관교육자 전용으로 설정한다."""
        checkbox = self.wait_for_present(self.INSTITUTION_EDUCATOR_ONLY_CHECKBOX)
        if not checkbox.is_selected():
            logger.info("기관교육자 전용 공개 설정")
            try:
                label = checkbox.find_element(By.XPATH, "./ancestor::label")
                label.click()
            except (ElementClickInterceptedException, StaleElementReferenceException):
                self.click_with_javascript(checkbox)

    def click_submit_button(self) -> WebElement:
        """[등록 / 저장] 버튼을 클릭한다."""
        logger.info("게시글 [등록/저장] 버튼 클릭")
        return self.click(self.SUBMIT_BUTTON)

    def write_post(self, title: str, content: str) -> None:
        """일반 게시글을 작성하고 등록한다."""
        self.click_write_button()
        self.enter_title(title)
        self.enter_content(content)
        self.click_submit_button()

    def get_post_count(self) -> int:
        """게시판 목록의 게시글 수를 반환한다."""
        return len(self.find_elements_visible(self.POST_ITEM, timeout=5))

    def get_first_post_title(self) -> str:
        """첫 번째 게시글 목록 항목의 제목을 반환한다."""
        post_item = self.find_elements_visible(self.POST_ITEM, timeout=5)[0]
        return post_item.text.strip()

    def select_first_post(self) -> WebElement:
        """목록에서 첫 번째 게시글을 클릭하여 상세 화면으로 진입한다."""
        logger.info("첫 번째 게시글 선택")
        post_item = self.find_elements_visible(self.POST_ITEM, timeout=5)[0]
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", post_item
        )
        try:
            post_item.click()
        except (ElementClickInterceptedException, StaleElementReferenceException):
            self.click_with_javascript(post_item)
        return post_item

    def get_detail_title(self) -> str:
        """상세 화면의 제목 텍스트를 반환한다."""
        return self.get_text(self.DETAIL_TITLE)

    def get_detail_content(self) -> str:
        """상세 화면의 본문 텍스트를 반환한다."""
        return self.get_text(self.DETAIL_CONTENT)

    def wait_for_detail_title(self, expected_title: str) -> str:
        """상세 화면에 기대한 제목이 표시될 때까지 기다린다."""
        def detail_title_matches(_: WebDriver) -> str | bool:
            title = self.get_detail_title()
            return title if expected_title in title else False

        from selenium.webdriver.support.ui import WebDriverWait

        return WebDriverWait(self.driver, self.default_timeout).until(
            detail_title_matches
        )

    def wait_for_detail_content(self, expected_content: str, timeout: float | None = None) -> str:
        """상세 화면에 기대한 본문이 표시될 때까지 대기한다."""
        selected_timeout = self._get_timeout(timeout)

        def detail_content_matches(_: WebDriver) -> str | bool:
            content = self.get_detail_content()
            return content if expected_content in content else False

        return WebDriverWait(self.driver, selected_timeout).until(
            detail_content_matches,
            message=f"상세 화면 본문에 기대 문구가 표시되지 않았습니다: {expected_content}",
        )

    def click_edit_button(self) -> WebElement:
        """게시글 상세 화면에서 [수정] 버튼을 클릭한다."""
        logger.info("게시글 [수정] 버튼 클릭")
        self.click(self.ARTICLE_MENU_BUTTON)
        return self.click(self.EDIT_BUTTON)

    def select_post_by_title(self, title: str) -> WebElement:
        """목록에서 지정한 제목의 게시글을 열어 상세 화면으로 이동한다."""
        for post_item in self.find_elements_visible(self.POST_ITEM, timeout=5):
            if title not in post_item.text:
                continue

            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", post_item
            )
            try:
                post_item.click()
            except (ElementClickInterceptedException, StaleElementReferenceException):
                self.click_with_javascript(post_item)
            return post_item

        raise AssertionError(f"정리 대상 게시글을 목록에서 찾지 못했습니다: {title}")

    def delete_current_post(self) -> None:
        """현재 상세 화면의 게시글을 삭제하고 확인 절차를 처리한다."""
        logger.info("현재 게시글 삭제")
        article_url = self.driver.current_url
        self.click(self.ARTICLE_MENU_BUTTON)
        self.click(self.DELETE_BUTTON)

        try:
            alert = WebDriverWait(self.driver, 2).until(EC.alert_is_present())
            alert.accept()
        except TimeoutException:
            confirm_button = self.find_optional_visible(
                self.DELETE_CONFIRM_BUTTON, timeout=5
            )
            if confirm_button:
                try:
                    confirm_button.click()
                except (ElementClickInterceptedException, StaleElementReferenceException):
                    self.click_with_javascript(confirm_button)

        WebDriverWait(self.driver, self.default_timeout).until(
            lambda driver: driver.current_url != article_url
            and not driver.find_elements(By.CSS_SELECTOR, "#boardArticleContent")
        )

    def is_post_title_visible(self, title: str) -> bool:
        """게시판 목록의 보이는 제목 중 지정한 제목이 있는지 확인한다."""
        try:
            return any(
                title in post_item.text
                for post_item in self.find_elements_visible(self.POST_ITEM, timeout=3)
            )
        except (TimeoutException, NoSuchElementException):
            return False

    def is_institution_educator_only_selected(self) -> bool:
        """글쓰기/수정 화면의 기관교육자 전용 설정 상태를 반환한다."""
        checkbox = self.wait_for_present(self.INSTITUTION_EDUCATOR_ONLY_CHECKBOX)
        return checkbox.is_selected()

    def _log_board_load_failure(
        self,
        stage: str,
        level: int = logging.ERROR,
    ) -> None:
        """게시판 진입 실패 당시 화면 상태를 민감정보 없이 기록한다."""
        reauth_password = (By.NAME, "password")
        classroom_links = (
            By.CSS_SELECTOR,
            "a[href*='/classrooms/'], a[href*='/courses/']",
        )

        def element_state(locator: Locator) -> tuple[int, int]:
            try:
                elements = self.driver.find_elements(*locator)
                visible_count = 0
                for element in elements:
                    try:
                        if element.is_displayed():
                            visible_count += 1
                    except StaleElementReferenceException:
                        continue
                return len(elements), visible_count
            except WebDriverException:
                return -1, -1

        try:
            current_url = self.driver.current_url
        except WebDriverException:
            current_url = "<unavailable>"

        try:
            page_title = self.driver.title
        except WebDriverException:
            page_title = "<unavailable>"

        reauth_total, reauth_visible = element_state(reauth_password)
        classroom_total, classroom_visible = element_state(classroom_links)
        write_total, write_visible = element_state(self.WRITE_POST_BUTTON)
        logger.log(
            level,
            "게시판 로드 실패 상태: stage=%s, current_url=%s, page_title=%s, "
            "reauth_password=%s/%s, classroom_links=%s/%s, write_button=%s/%s",
            stage,
            current_url,
            page_title,
            reauth_visible,
            reauth_total,
            classroom_visible,
            classroom_total,
            write_visible,
            write_total,
        )

    def wait_for_board_loaded(
        self,
        timeout: float = 15,
        failure_log_level: int = logging.ERROR,
    ) -> None:
        """게시판 메인 영역 및 글쓰기 버튼이 준비될 때까지 대기한다."""
        selected_timeout = self._get_timeout(timeout)
        try:
            WebDriverWait(self.driver, selected_timeout).until(
                lambda driver: "/articles" in driver.current_url
            )
        except TimeoutException:
            self._log_board_load_failure(
                "articles_url",
                level=failure_log_level,
            )
            raise

        try:
            self.wait_for_visible(self.WRITE_POST_BUTTON, timeout=selected_timeout)
        except TimeoutException:
            self._log_board_load_failure(
                "write_button",
                level=failure_log_level,
            )
            raise
