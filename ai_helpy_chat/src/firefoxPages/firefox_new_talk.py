from selenium.webdriver.common.by import By

from src.firefoxPages.base_page import BasePage
import logging

logger = logging.getLogger(__name__)


class FirefoxNewTalk(BasePage):
    """새 대화 페이지 Page Object.

    메인 페이지 이동, 사용자 메시지 입력,
    샘플 질문 선택 기능을 제공한다.
    """

    URL = "https://dev-qaproject-helpy-chat.dev.elicer.io/"

    def __init__(self, driver, timeout=None, action_delay=0):
        super().__init__(driver, timeout, action_delay)

    def click_elice_logo(self):
        """엘리스 로고를 클릭하여 메인 페이지로 이동한다."""
        logo_locator = (
            By.XPATH,
            "//a[.//img[@alt='Default Organization']]",
        )

        self.click(logo_locator)

    def input_user_message(self, message, stop_after_send=False):
        """사용자 메시지를 입력하고 전송한다.

        Args:
            message: 입력할 메시지.
            stop_after_send: True이면 전송 직후 응답 생성을 중지한다.
        """
        message_input_locator = (
            By.XPATH,
            "//textarea[@name='input']",
        )

        self.fill_text(message_input_locator, message)

        self.pause_for_debugging()

        # 포커스 문제 발생 해결용
        self.hover_to_main()

        send_button_locator = (
            By.XPATH,
            "//button[@aria-label='보내기' and @tabindex='0']",
        )

        self.click(send_button_locator)

        if stop_after_send:
            cancel_button_locator = (
                By.XPATH,
                "//*[@aria-label='취소']",
            )

            self.click(cancel_button_locator)

    def click_sample_question(self, index):
        """샘플 질문 목록에서 지정한 질문을 클릭한다.

        Args:
            index: 선택할 샘플 질문의 인덱스.
        """
        sample_question_locator = (
            By.CLASS_NAME,
            "css-19yq8xv",
        )

        self.pause_for_debugging()

        self.click_from_list(
            sample_question_locator,
            index,
            timeout=3,
        )
    
    def select_plus_menu(self, menu_name):
        """플러스 메뉴를 열고 지정한 메뉴를 선택한다.

        Args:
            menu_name: 선택할 메뉴 이름.
        """
        plus_button_locator = (
            By.XPATH,
            "//*[@data-testid='plusIcon']",
        )

        self.click(plus_button_locator)

        self.pause_for_debugging()

        menu_locator = (
            By.XPATH,
            f"//li[.//*[normalize-space()='{menu_name}']]",
        )

        self.click(menu_locator)

        self.pause_for_debugging()

    def create_image(self, keyword):
        """이미지 생성 메뉴를 선택한 뒤 프롬프트를 전송한다.

        Args:
            keyword: 이미지 생성에 사용할 프롬프트.
        """
        self.select_plus_menu("이미지 생성")
        self.input_user_message(keyword)

    def search_web(self, keyword):
        """웹 검색 메뉴를 선택한 뒤 검색어를 전송한다.

        Args:
            keyword: 검색에 사용할 키워드.
        """
        self.select_plus_menu("웹 검색")
        self.input_user_message(keyword)
    
    def click_sidebar_button(self):
        """사이드바 토글 버튼을 클릭한다."""
        sidebar_button_locator = (
            By.XPATH,
            "//button[.//*[@data-icon='bars']]",
        )

        self.pause_for_debugging()

        self.click(sidebar_button_locator)

    def _click_agent(self, agent_locator, index):
        """에이전트 목록에서 지정한 인덱스의 에이전트를 클릭한다."""
        agent_list = self.wait_for_all_present(agent_locator)

        if index >= len(agent_list):
            raise IndexError(
                f"Agent index({index}) is out of range. "
                f"Total agents: {len(agent_list)}"
            )

        self.pause_for_debugging()

        self.click_from_list(
            agent_locator,
            index,
            timeout=3,
        )

    def select_agent(
        self,
        is_private=True,
        category="전체",
        index=0,
        create_new_agent=False,
    ):
        """에이전트를 선택하거나 새 에이전트를 생성한다.

        Args:
            is_private: True이면 '내 에이전트' 탭을 선택한다.
            category: 선택할 카테고리 이름(현재 미사용).
            index: 선택할 에이전트의 인덱스.
            create_new_agent: True이면 '에이전트 만들기'를 클릭한다.
        """
        if is_private:
            private_tab_locator = (
                By.XPATH,
                "//button[@role='tab' and contains(@id, 'agents-private')]",
            )

            self.click(private_tab_locator)

            if create_new_agent:
                create_agent_locator = (
                    By.PARTIAL_LINK_TEXT,
                    "에이전트 만들기",
                )

                self.click(create_agent_locator)
                return

            category_locator = (
                By.XPATH,
                "//div[contains(@class,'swiper-horizontal')]"
                "//div[@role='button']",
            )

            self.click_from_list(
                category_locator,
                0,
                timeout=3,
            )

        else:
            organization_tab_locator = (
                By.XPATH,
                "//button[@role='tab' and "
                "contains(@id, 'agents-organization')]",
            )

            self.click(organization_tab_locator)

            category_locator = (
                By.XPATH,
                "//div[contains(@class,'swiper-horizontal')]"
                "//div[@role='button']",
            )

            self.click_from_list(
                category_locator,
                1,
                timeout=3,
            )

            self.pause_for_debugging()

            self.click_from_list(
                category_locator,
                0,
                timeout=3,
            )

        agent_locator = (
            By.XPATH,
            "//a[contains(@href,'/agents/') "
            "and .//div[contains(@class,'MuiAvatar-circular')]]",
        )

        self._click_agent(
            agent_locator,
            index,
        )






