from selenium.webdriver.common.by import By

from src.firefoxPages.base_page import BasePage
from src.firefoxPages.firefox_new_talk import FirefoxNewTalk
import logging

logger = logging.getLogger(__name__)

class FirefoxTalkingWithAI(BasePage):
    """AI 대화 페이지 Page Object.

    메시지 전송 취소, 추천 질문 선택,
    대화 이름 변경 및 삭제 기능을 제공한다.
    """

    RESPONSE_WAIT_TIME = 100

    def __init__(self, driver, timeout=None, action_delay=0):
        super().__init__(driver, timeout, action_delay)
        self.new_talk = FirefoxNewTalk(driver, timeout, action_delay)

    def input_user_message(self, message, stop_after_send=False):
        """사용자 메시지를 입력하고 전송한다."""
        self.new_talk.input_user_message(
            message,
            stop_after_send,
        )

    def cancel_message(self):
        """응답 생성 중인 메시지를 취소한다."""
        cancel_button_locator = (
            By.XPATH,
            "//*[@aria-label='취소']",
        )

        self.pause_for_debugging()

        self.click(cancel_button_locator)

    def close_popup(self):
        """개인 토큰 한도 안내 팝업을 닫는다."""
        
        close_button_locator = (
            By.XPATH,
            "//*[name()='svg' and @data-testid='xmark-largeIcon']",
        )

        popup = self.find_optional_visible(close_button_locator, timeout=10)

        if popup is not None:
            popup.click()
    
    def click_scroll_bottom_button(self):
        """맨 아래로 스크롤 버튼을 클릭한다.
        
        Returns:
            스크롤 버튼을 못 찾을 시 False 반환
        """
        scroll_bottom_button_locator = (
            By.XPATH,
            "//button[@aria-label='맨 아래로 스크롤']"
        )

        return self.click_if_present(
            scroll_bottom_button_locator, 
            timeout=2,
            )

    def click_ai_recommended_question(self, index):
        """AI 추천 질문을 클릭한다.

        Args:
            index: 선택할 추천 질문의 인덱스.
        """
        recommended_question_text_locator = (
            By.XPATH,
            "//p[normalize-space()='AI헬피 추천 질문']"
        )
        recommended_question_locator = (
            By.XPATH,
            "//button[contains(@class, 'MuiCardActionArea-root')]"
        )

        # AI헬피 추천 질문 텍스트가 노출돼야 추천 질문이 나온다.
        self.wait_for_first_visible(recommended_question_text_locator)

        self.pause_for_debugging(seconds=2)

        self.click_from_list(
            recommended_question_locator,
            index,
            timeout=10
        )

    def _open_right_more_menu(self):
        """대화방의 더보기 메뉴를 클릭한다."""
        more_menu_locator = (
            By.XPATH,
            "//button[.//*[@data-testid='ellipsis-verticalIcon']]"
            "[not(ancestor::div[contains(@class, 'menu-button')])]",
        )

        self.click(more_menu_locator)

        self.pause_for_debugging()

    def change_chat_room_name(
        self,
        new_name,
        cancel_change=False,
    ):
        """더 보기 메뉴에서 대화방 이름을 변경한다.

        Args:
            new_name: 변경할 대화방 이름.
            cancel_change: True이면 저장하지 않고 취소한다.
        """
        self._open_right_more_menu()

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
            self.pause_for_debugging()

            self.click(cancel_button_locator)
        else:
            save_button_locator = (
                By.XPATH,
                "//button[normalize-space()='저장']",
            )

            self.click(save_button_locator)

    def delete_chat_room(
        self,
        cancel_delete=False,
    ):
        """더 보기 메뉴에서 대화방을 삭제한다.

        Args:
            cancel_delete: True이면 삭제하지 않고 취소한다.
        """
        self._open_right_more_menu()

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
            self.pause_for_debugging()

            self.click(cancel_button_locator)
            return

        delete_button_locator = (
            By.XPATH,
            "//button[normalize-space()='삭제']",
        )

        self.click(delete_button_locator)

    def _get_ai_action_button(self, label, response_index):
        """ai의 응답 메시지에 있는 복사, 다시 생성 버튼을 가져온다.
           여러 응답 메시지중에 원하는 index를 선택할 수 있다.

        Args:
            label: 선택할 버튼의 라벨
            response_index = 선택할 응답 메시지 인덱스    
        Returns:
             WebElement: 지정한 응답 인덱스의 aria-label을 가진 버튼
        """
        # 사용자 응답에도 동일한 복사 요소가 존재하여 구분하기 위함
        action_area_locator = (
            By.XPATH,
            "//div[button[@aria-label='다시 생성']]"
        )

        button_locator = (
            By.XPATH,
            f".//button[@aria-label='{label}']"
        )

        action_areas = self.wait_for_all_present(action_area_locator)

        action_area = action_areas[response_index]

        return action_area.find_element(*button_locator)
     
    def copy_ai_response_message(self, response_index = -1):
        """ai의 응답 메시지를 복사한다.
           "복사" 팝업 확인을 위해 잠깐 호버하는 기능을 추가.

        Args:
            response_index: 선택할 응답 메시지 인덱스  
        Returns:
            복사된 텍스트 
        """

        # pyperclip.copy("")   # 기존 클립보드 초기화

        copy_button = self._get_ai_action_button("복사", response_index)

        self.scroll_element_into_view(copy_button)
     
        # 팝업을 위한 호버
        self.hover_element(copy_button)

        self.pause_for_debugging(seconds=2)

        copy_button.click()

        
        self.pause_for_debugging()
        
        # return pyperclip.paste()

    def regenerate_ai_response_message(self, response_index = -1):
        """ai의 응답 메시지를 재생성한다.
           "다시 생성" 팝업 확인을 위해 잠깐 호버하는 기능을 추가.

        Args:
            response_index: 선택할 응답 메시지 인덱스  
        """
        regenerate_button = self._get_ai_action_button("다시 생성", response_index)

        # 팝업을 위한 호버
        self.hover_element(regenerate_button)

        self.scroll_element_into_view(regenerate_button)

        self.pause_for_debugging(seconds=2)

        regenerate_button.click()
        
        self.pause_for_debugging()

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