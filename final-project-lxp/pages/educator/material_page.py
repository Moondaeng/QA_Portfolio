"""교육자의 수업 자료 생성 화면을 다루는 Page Object."""

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from pages.base_page import BasePage, Locator, logger


class EducatorMaterialPage(BasePage):
    """일반 수업 안의 텍스트 자료 생성 동작을 제공한다."""

    # 수업 상세(main) > MUI 활성 버튼 > 수업 자료 추가
    MATERIAL_ADD_BUTTON: Locator = (
        By.XPATH,
        "//main//button[contains(@class, 'MuiButton-root') and @type='button' "
        "and not(@disabled) and (contains(normalize-space(), '수업 자료 추가') or contains(normalize-space(), '수업자료 추가'))]",
    )
    # MUI 메뉴 > menuitem 역할 > 새로 만들기
    CREATE_NEW_MENU_ITEM: Locator = (
        By.XPATH,
        "//ul[@role='menu']//li[@role='menuitem' and "
        "normalize-space()='새로 만들기']",
    )
    # 자료 유형 모달 > 제품 표준 카드 > 텍스트 에디터 label
    TEXT_EDITOR_TYPE_CARD: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-borderless-dialog') and "
        "contains(@class, 'course-lectures-material-new')]"
        "//div[contains(@class, 'eb-radio-card')]"
        "[.//p[contains(@class, 'MuiTypography') and "
        "normalize-space()='텍스트 에디터']]",
    )
    # 자료 유형 모달 > 제품 표준 카드 > 퀴즈 label
    QUIZ_TYPE_CARD: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-borderless-dialog') and "
        "contains(@class, 'course-lectures-material-new')]"
        "//div[contains(@class, 'eb-radio-card')]"
        "[.//*[contains(@data-testid, 'MaterialTypeQuiz') or contains(normalize-space(), '퀴즈')]]",
    )
    # 자료 유형 모달 > 제품 표준 카드 > Youtube / 동영상 label
    VIDEO_TYPE_CARD: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-borderless-dialog') and "
        "contains(@class, 'course-lectures-material-new')]"
        "//div[contains(@class, 'eb-radio-card')]"
        "[.//*[contains(@data-testid, 'MaterialTypeLiveLink') or contains(normalize-space(), 'Youtube') or contains(normalize-space(), '동영상')]]",
    )
    # 유형 선택 모달 > 활성 다음 버튼. 배경 화면의 비활성 pagination 버튼을 배제한다.
    MATERIAL_TYPE_NEXT_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-borderless-dialog') and "
        "contains(@class, 'course-lectures-material-new')]"
        "[.//div[contains(@class, 'eb-radio-card')]]"
        "//button[not(@disabled) and normalize-space()='다음']",
    )
    # 텍스트 에디터 모달 > title input / 편집기 / 활성 저장 버튼
    TEXT_EDITOR_FORM: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-borderless-dialog') or contains(@class, 'eb-dialog') or @role='dialog']"
        "[.//input[contains(@placeholder, '수업 자료 제목')]]",
    )
    TEXT_EDITOR_TITLE_INPUT: Locator = (
        By.CSS_SELECTOR,
        "input.eb-textbox__input[type='text'][placeholder*='수업 자료 제목'], "
        "div[role='dialog'] input[type='text'][placeholder*='수업 자료 제목'], "
        "div.eb-borderless-dialog input[placeholder*='수업 자료 제목']",
    )
    TEXT_EDITOR_CONTENT_INPUT: Locator = (
        By.CSS_SELECTOR,
        "div.eb-borderless-dialog [contenteditable='true'], "
        "div[role='dialog'] [contenteditable='true'], "
        "[role='textbox'][contenteditable='true']",
    )
    TEXT_EDITOR_SAVE_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-borderless-dialog') or contains(@class, 'eb-dialog') or @role='dialog']"
        "[.//input[contains(@placeholder, '수업 자료 제목')]]"
        "//button[(contains(@class, 'eb-button') or contains(@class, 'MuiButton-root') or @type='button' or @type='submit') and "
        "(normalize-space()='저장' or normalize-space()='수정' or normalize-space()='확인' "
        "or contains(., '저장') or contains(., '수정'))]",
    )
    TEXT_EDITOR_CANCEL_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-borderless-dialog') or contains(@class, 'eb-dialog') or @role='dialog']"
        "[.//input[contains(@placeholder, '수업 자료 제목')]]"
        "//button[normalize-space()='취소' or contains(., '취소')]",
    )
    # 퀴즈 모달 > title input / 저장 버튼
    QUIZ_EDITOR_FORM: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-borderless-dialog') or contains(@class, 'eb-modal')]"
        "[.//*[normalize-space()='수업 자료 제목']]",
    )
    QUIZ_TITLE_INPUT: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-borderless-dialog') or contains(@class, 'eb-modal')]"
        "//input[@placeholder='수업 자료 제목을 입력하세요.']",
    )
    QUIZ_SAVE_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-borderless-dialog') or contains(@class, 'eb-modal')]"
        "//button[normalize-space()='저장']",
    )
    # 동영상 모달 > title input / url input / 저장 버튼
    VIDEO_EDITOR_FORM: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-borderless-dialog') or contains(@class, 'eb-modal')]"
        "[.//*[normalize-space()='비디오 파일'] or .//*[contains(normalize-space(), 'Youtube')]]",
    )
    VIDEO_TITLE_INPUT: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-borderless-dialog') or contains(@class, 'eb-modal')]"
        "//input[@placeholder='수업 자료 제목을 입력하세요.']",
    )
    VIDEO_URL_INPUT: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-borderless-dialog') or contains(@class, 'eb-modal')]"
        "//input[contains(@placeholder, 'youtube') or contains(@placeholder, 'embed')]",
    )
    VIDEO_SAVE_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-borderless-dialog') or contains(@class, 'eb-modal')]"
        "//button[normalize-space()='저장']",
    )
    DROPDOWN_DELETE_ITEM: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-button-dropdown__menu')]"
        "//li[contains(@class, 'ant-menu-item') and normalize-space()='삭제']",
    )
    DROPDOWN_EDIT_ITEM: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-button-dropdown__menu')]"
        "//li[contains(@class, 'ant-menu-item') and (normalize-space()='수정' or .//*[normalize-space()='수정'])]",
    )
    DELETE_CONFIRM_BUTTON: Locator = (
        By.XPATH,
        "//div[contains(@class, 'eb-dialog') or @role='dialog']"
        "//button[contains(@class, 'eb-button--role-warning') or normalize-space()='확인']",
    )

    def __init__(self, driver: WebDriver, timeout: float = 15) -> None:
        """교육자 자료 관리 화면 객체를 초기화한다."""
        super().__init__(driver, timeout)

    def _material_title_locator(self, title: str) -> Locator:
        """자료 목록에서 제목 요소의 locator를 반환한다."""
        title_literal = self._xpath_literal(title)
        return (
            By.XPATH,
            "//main//p[contains(@class, 'eb-course-lecture-page__title') and "
            f"normalize-space()={title_literal}]",
        )

    def _material_more_button_locator(self, title: str) -> Locator:
        """자료 카드의 더보기(...) 버튼 locator를 반환한다."""
        title_literal = self._xpath_literal(title)
        return (
            By.XPATH,
            f"//main//p[contains(@class, 'eb-course-lecture-page__title') and normalize-space()={title_literal}]"
            "/following::button[contains(@class, 'eb-button-dropdown__single__button') or .//i[contains(@class, 'icon-more')]][1]",
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

    def open_text_editor_form(self) -> WebElement:
        """수업 자료 추가 메뉴에서 텍스트 에디터 입력 폼을 연다."""
        self.click(self.MATERIAL_ADD_BUTTON)
        self.click(self.CREATE_NEW_MENU_ITEM)
        self.click(self.TEXT_EDITOR_TYPE_CARD)
        self.click(self.MATERIAL_TYPE_NEXT_BUTTON)
        return self.wait_for_visible(self.TEXT_EDITOR_FORM)

    def is_text_editor_form_displayed(self) -> bool:
        """텍스트 자료 제목·본문 입력 폼이 보이는지 반환한다."""
        return self.find_optional_visible(self.TEXT_EDITOR_FORM, timeout=5) is not None

    def is_text_editor_save_disabled(self) -> bool:
        """필수값이 비어 있을 때 자료 저장 버튼이 비활성인지 반환한다."""
        return not self.wait_for_present(self.TEXT_EDITOR_SAVE_BUTTON).is_enabled()

    def enter_text_material_title(self, title: str) -> WebElement:
        """텍스트 자료 제목을 입력한다."""
        element = self.wait_for_clickable(self.TEXT_EDITOR_TITLE_INPUT)
        element.send_keys(Keys.CONTROL + "a")
        element.send_keys(Keys.BACKSPACE)
        element.send_keys(title)
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));"
            "arguments[0].dispatchEvent(new Event('change', { bubbles: true }));",
            element,
        )
        return element

    def enter_text_material_content(self, content: str) -> WebElement:
        """텍스트 에디터 본문에 일반 텍스트를 입력한다."""
        editor = self.wait_for_visible(self.TEXT_EDITOR_CONTENT_INPUT)
        editor.send_keys(Keys.CONTROL + "a")
        editor.send_keys(Keys.BACKSPACE)
        editor.send_keys(content)
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
            editor,
        )
        editor.send_keys(Keys.TAB)
        return editor

    def save_text_material(self) -> None:
        """입력된 텍스트 자료를 저장하고 편집 폼이 닫힐 때까지 기다린다."""
        self.wait_for_clickable(self.TEXT_EDITOR_SAVE_BUTTON, timeout=10)
        self.click(self.TEXT_EDITOR_SAVE_BUTTON)
        self.wait_for_invisible(self.TEXT_EDITOR_FORM, timeout=10)

    def create_text_material(self, title: str, content: str) -> None:
        """텍스트 자료를 생성한다. 호출자는 이후 생성 항목을 반드시 정리해야 한다."""
        self.open_text_editor_form()
        self.enter_text_material_title(title)
        self.enter_text_material_content(content)
        self.save_text_material()
        self.wait_for_visible(self._material_title_locator(title), timeout=10)

    def open_quiz_editor_form(self) -> WebElement:
        """수업 자료 추가 메뉴에서 퀴즈 입력 폼을 연다."""
        self.click(self.MATERIAL_ADD_BUTTON)
        self.click(self.CREATE_NEW_MENU_ITEM)
        self.click(self.QUIZ_TYPE_CARD)
        self.click(self.MATERIAL_TYPE_NEXT_BUTTON)
        return self.wait_for_visible(self.QUIZ_EDITOR_FORM)

    def is_quiz_editor_form_displayed(self) -> bool:
        """퀴즈 자료 제목 입력 폼이 보이는지 반환한다."""
        return self.find_optional_visible(self.QUIZ_EDITOR_FORM, timeout=5) is not None

    def is_quiz_editor_save_disabled(self) -> bool:
        """필수값이 비어 있을 때 퀴즈 저장 버튼이 비활성인지 반환한다."""
        return not self.wait_for_present(self.QUIZ_SAVE_BUTTON).is_enabled()

    def enter_quiz_material_title(self, title: str) -> WebElement:
        """퀴즈 자료 제목을 입력한다."""
        return self.fill_text(self.QUIZ_TITLE_INPUT, title)

    def save_quiz_material(self) -> None:
        """입력된 퀴즈 자료를 저장하고 모달이 닫힐 때까지 기다린다."""
        self.click(self.QUIZ_SAVE_BUTTON)
        self.wait_for_invisible(self.QUIZ_EDITOR_FORM, timeout=10)

    def create_quiz_material(self, title: str) -> None:
        """퀴즈 자료를 생성한다. 호출자는 이후 생성 항목을 반드시 정리해야 한다."""
        self.open_quiz_editor_form()
        self.enter_quiz_material_title(title)
        self.save_quiz_material()
        self.wait_for_visible(self._material_title_locator(title), timeout=10)

    def open_video_editor_form(self) -> WebElement:
        """수업 자료 추가 메뉴에서 동영상 입력 폼을 연다."""
        self.click(self.MATERIAL_ADD_BUTTON)
        self.click(self.CREATE_NEW_MENU_ITEM)
        self.click(self.VIDEO_TYPE_CARD)
        self.click(self.MATERIAL_TYPE_NEXT_BUTTON)
        return self.wait_for_visible(self.VIDEO_EDITOR_FORM)

    def is_video_editor_form_displayed(self) -> bool:
        """동영상 자료 입력 폼이 보이는지 반환한다."""
        return self.find_optional_visible(self.VIDEO_EDITOR_FORM, timeout=5) is not None

    def is_video_editor_save_disabled(self) -> bool:
        """필수값/URL이 유효하지 않을 때 동영상 저장 버튼이 비활성인지 반환한다."""
        return not self.wait_for_present(self.VIDEO_SAVE_BUTTON).is_enabled()

    def enter_video_material_title(self, title: str) -> WebElement:
        """동영상 자료 제목을 입력한다."""
        return self.fill_text(self.VIDEO_TITLE_INPUT, title)

    def enter_video_material_url(self, url: str) -> WebElement:
        """동영상 자료의 URL을 입력한다."""
        return self.fill_text(self.VIDEO_URL_INPUT, url)

    def save_video_material(self) -> None:
        """입력된 동영상 자료를 저장하고 모달이 닫힐 때까지 기다린다."""
        self.click(self.VIDEO_SAVE_BUTTON)
        self.wait_for_invisible(self.VIDEO_EDITOR_FORM, timeout=10)

    def create_video_material(self, title: str, url: str) -> None:
        """동영상 자료를 생성한다. 호출자는 이후 생성 항목을 반드시 정리해야 한다."""
        self.open_video_editor_form()
        self.enter_video_material_title(title)
        self.enter_video_material_url(url)
        self.save_video_material()
        self.wait_for_visible(self._material_title_locator(title), timeout=10)

    def is_material_listed(self, title: str) -> bool:
        """지정한 제목의 자료가 목록에 표시되는지 확인한다."""
        return self.find_optional_visible(self._material_title_locator(title), timeout=5) is not None

    def wait_until_material_listed(
        self, title: str, timeout: float = 15
    ) -> WebElement:
        """새로고침 뒤에도 지정한 제목의 자료가 목록에 표시될 때까지 기다린다."""
        return self.wait_for_visible(self._material_title_locator(title), timeout=timeout)

    def delete_material_by_title(self, title: str) -> None:
        """목록에서 지정한 제목의 자료를 찾아 삭제한다."""
        logger.info("자료 삭제 시작: title=%s", title)
        more_btn = self.wait_for_clickable(self._material_more_button_locator(title), timeout=10)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_btn)
        logger.info("더보기 버튼 클릭")
        more_btn.click()
        delete_btn = self.wait_for_clickable(self.DROPDOWN_DELETE_ITEM, timeout=5)
        logger.info("드롭다운 삭제 항목 클릭: text=%s", delete_btn.text)
        delete_btn.click()
        confirm_btn = self.wait_for_clickable(self.DELETE_CONFIRM_BUTTON, timeout=5)
        logger.info("확인 다이얼로그 버튼 클릭: text=%s", confirm_btn.text)
        confirm_btn.click()
        self.wait_for_invisible(self.DELETE_CONFIRM_BUTTON, timeout=10)
        self.driver.refresh()

    def wait_until_material_removed(self, title: str, timeout: float = 15) -> bool:
        """지정한 제목의 자료가 목록에서 완전히 사라질 때까지 기다린다."""
        return self.wait_for_invisible(self._material_title_locator(title), timeout=timeout)

    def open_material_edit_form(self, title: str) -> WebElement:
        """목록에서 지정한 제목의 자료 카드의 더보기 메뉴를 열고 '수정'을 클릭해 수정 폼을 연다."""
        logger.info("자료 수정 폼 열기: title=%s", title)
        more_btn = self.wait_for_clickable(self._material_more_button_locator(title), timeout=10)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", more_btn)
        more_btn.click()
        edit_btn = self.wait_for_clickable(self.DROPDOWN_EDIT_ITEM, timeout=5)
        edit_btn.click()
        return self.wait_for_visible(self.TEXT_EDITOR_FORM, timeout=10)

    def edit_text_material(
        self, current_title: str, new_title: str, new_content: str | None = None
    ) -> None:
        """기존 텍스트 자료의 제목 및 내용을 수정하고 저장한다."""
        self.open_material_edit_form(current_title)
        self.enter_text_material_title(new_title)
        if new_content is not None:
            self.enter_text_material_content(new_content)
        self.save_text_material()
        self.wait_until_material_listed(new_title, timeout=10)

    def get_text_material_content(self, title: str) -> str:
        """자료 수정 폼에서 텍스트 본문을 읽고 취소로 원래 화면에 돌아온다."""
        self.open_material_edit_form(title)
        editor = self.wait_for_visible(self.TEXT_EDITOR_CONTENT_INPUT, timeout=10)
        content = (editor.get_attribute("innerText") or editor.text or "").strip()
        self.click(self.TEXT_EDITOR_CANCEL_BUTTON)
        self.wait_for_invisible(self.TEXT_EDITOR_FORM, timeout=10)
        return content
