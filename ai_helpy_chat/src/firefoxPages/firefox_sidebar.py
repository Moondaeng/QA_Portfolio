from selenium.webdriver.common.by import By

from src.firefoxPages.base_page import BasePage
import logging

logger = logging.getLogger(__name__)

class FirefoxSidebar(BasePage):
    """사이드바 영역 Page Object.

    새 대화 이동, 대화 목록 스크롤,
    대화 검색 및 에이전트 검색 기능을 제공한다.
    """
    RESPONSE_WAIT_TIME = 100

    def __init__(self, driver, timeout=None, action_delay=0):
        super().__init__(driver, timeout, action_delay)

    def wait_for_ai_response(self):
        """AI 응답이 완료될 때까지 대기한다."""

        response_locator = (By.XPATH, "//*[@aria-label='취소']")
        self.wait_for_present(response_locator, self.RESPONSE_WAIT_TIME )
        self.wait_for_invisible(response_locator, self.RESPONSE_WAIT_TIME)

    def wait_for_alert_message(self):
        """알림 메시지가 사라질 때까지 대기한다."""
        alert_locator = (
            By.XPATH,
            "//div[.//*[@data-testid='circle-checkIcon']]"
        )

        self.wait_for_present(alert_locator, self.RESPONSE_WAIT_TIME )
        self.wait_for_invisible(alert_locator, self.RESPONSE_WAIT_TIME)

    def click_new_chat(self):
        """새 대화 페이지로 이동한다."""
        new_chat_locator = (
            By.XPATH,
            "//a[contains(@class,'MuiListItemButton-gutters') and @href='/']",
        )

        self.click(new_chat_locator)

    def scroll_chat_list(
        self,
        scroll_y,
        repeat_count=1,
    ):
        """사이드바 대화 목록을 스크롤한다.

        Args:
            scroll_y: 스크롤 이동 거리.
            repeat_count: 스크롤 반복 횟수.
        """
        chat_list_locator = (
            By.XPATH,
            "//*[@data-testid='virtuoso-scroller']",
        )

        for _ in range(repeat_count):
            self.pause_for_debugging()

            self.scroll_element_by(
                chat_list_locator,
                pos_y=scroll_y,
            )

            self.pause_for_debugging()

    def search_chat_room(
        self,
        chat_room_name,
        select_index,
    ):
        """대화방을 검색하고 선택한다.

        Args:
            chat_room_name: 검색할 대화방 이름.
            select_index: 선택할 검색 결과 인덱스.
        """
        search_button_locator = (
            By.XPATH,
            "//div[@role='button' and "
            ".//*[@data-testid='magnifying-glassIcon']]",
        )

        self.click(search_button_locator)

        self.pause_for_debugging()

        search_input_locator = (
            By.XPATH,
            "//div[@role='dialog']//input[@placeholder='검색']",
        )

        self.fill_text(
            search_input_locator,
            chat_room_name,
        )

        self.pause_for_debugging()

        search_result_locator = (
            By.XPATH,
            "//div[@data-fullscreen='false']//li/a",
        )

        search_results = self.wait_for_all_present(
            search_result_locator
        )

        if select_index >= len(search_results):
            # raise IndexError(
            print(
                f"Chat room index({select_index}) "
                f"is out of range. "
                f"Total results: {len(search_results)}"
            )
            x_button_locator = (
                By.XPATH,
                "//button[.//*[@data-testid='xmark-largeIcon']]"
            )

            self.pause_for_debugging()

            self.click(x_button_locator)
            return

        self.click_from_list(
            search_result_locator,
            select_index,
            timeout=10,
        )

    def search_agent_market(
        self,
        keyword,
    ):
        """에이전트 마켓플레이스에서 에이전트를 검색한다.

        Args:
            keyword: 검색할 에이전트 이름 또는 키워드.
        """
        agent_market_locator = (
            By.XPATH,
            "//a[@href='/agents']",
        )
        self.pause_for_debugging()

        self.click(agent_market_locator)

        search_input_locator = (
            By.XPATH,
            "//div[contains(@class,'MuiTextField-root')]"
            "//input[@placeholder='AI 에이전트 검색']",
        )

        self.pause_for_debugging()

        self.fill_text(
            search_input_locator,
            keyword,
        )
    
    def _open_more_menu(
        self,
        chat_room_index,
        ):
        """대화방의 더보기 메뉴를 클릭한다.
        
        Args:
            chat_room_index: 선택할 대화방 인덱스
        """
        chat_list_locator = (
            By.XPATH,
            "//ul[@data-testid='virtuoso-item-list']"
            "//a[contains(@href,'/chats/')]"
        )

        more_menu_list_locator = (
            By.XPATH,
            "//div[contains(@class, 'menu-button')]"
            "//button[.//*[@data-testid='ellipsis-verticalIcon']]"
        )

        chat_list = self.wait_for_all_present(chat_list_locator)

        chat = chat_list[chat_room_index]

        # 숨겨진 메뉴를 찾기위해 호버
        self.hover_element(chat)

        more_menu_list = self.wait_for_all_present(more_menu_list_locator)

        more_menu = more_menu_list[chat_room_index]

        self.pause_for_debugging()

        more_menu.click()

    def change_chat_room_name(
        self,
        new_name,
        chat_room_index = 0,
        cancel_change=False,
    ):
        """더 보기 메뉴에서 대화방 이름을 변경한다.

        Args:
            new_name: 변경할 대화방 이름.
            cancel_change: True이면 저장하지 않고 취소한다.
            chat_room_index: 선택할 대화방 인덱스
        """
        self._open_more_menu(chat_room_index)

        change_name_locator = (
            By.XPATH,
            "//li[.//*[normalize-space()='이름 변경']]",
        )

        self.click(change_name_locator)

        self.pause_for_debugging()

        name_input_locator = (
            By.NAME,
            "name",
        )

        self.fill_text(
            name_input_locator,
            new_name,
        )

        self.pause_for_debugging()

        if cancel_change:
            cancel_button_locator = (
                By.XPATH,
                "//button[normalize-space()='취소']",
            )

            self.click(cancel_button_locator)
        else:
            save_button_locator = (
                By.XPATH,
                "//button[normalize-space()='저장']",
            )

            self.click(save_button_locator)

    def delete_chat_room(
        self,
        chat_room_index = 0,
        cancel_delete=False,
    ):
        """더 보기 메뉴에서 대화방을 삭제한다.

        Args:
            cancel_delete: True이면 삭제하지 않고 취소한다.
            chat_room_index: 선택할 대화방 인덱스
        """
        self._open_more_menu(chat_room_index)

        delete_menu_locator = (
            By.XPATH,
            "//li[.//*[normalize-space()='삭제']]",
        )

        self.click(delete_menu_locator)

        self.pause_for_debugging()

        if cancel_delete:
            cancel_button_locator = (
                By.XPATH,
                "//button[normalize-space()='취소']",
            )

            self.click(cancel_button_locator)
            return

        delete_button_locator = (
            By.XPATH,
            "//button[normalize-space()='삭제']",
        )

        self.click(delete_button_locator)