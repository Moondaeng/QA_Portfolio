
import logging

import pytest

from src.firefoxPages.firefox_login_page import FirefoxLoginPage
from src.firefoxPages.firefox_sidebar import FirefoxSidebar
from src.firefoxPages.firefox_talking_withAI import FirefoxTalkingWithAI
from tests.firefox.firefox_test_data import FirefoxTestData

logger = logging.getLogger(__name__)

# @pytest.mark.skip
@pytest.mark.firefox
def test_sidebar_more_menu(firefox_driver):
    """사이드바 더보기 메뉴 기능을 테스트한다.

    채팅방 이름 변경 및 삭제 동작을 확인한다.
    """
    test_data = FirefoxTestData()

    logger.info("사이드바 더보기 메뉴 테스트 시작")

    login = FirefoxLoginPage(firefox_driver, action_delay=0.5)
    sidebar = FirefoxSidebar(firefox_driver, action_delay=0.5)
    talking_ai = FirefoxTalkingWithAI(firefox_driver, action_delay=0.5)

    login.login_with_account(
        test_data.TEST_USER_ID,
        test_data.TEST_PASSWORD,
    )
    logger.info("로그인 동작 완료")

    talking_ai.close_popup()
    logger.info("개인 토큰 팝업 확인 완료")

    sidebar.change_chat_room_name(
        "변경할이름",
        test_data.CHAT_ROOM_INDEX,
        test_data.CANCEL_BUTTON_NO,
    )
    sidebar.wait_for_alert_message()
    logger.info("사이드바에서 채팅방 이름 변경 완료")

    sidebar.hover_to_main()
    sidebar.delete_chat_room(
        test_data.CHAT_ROOM_INDEX,
        test_data.CANCEL_BUTTON_NO,
    )
    sidebar.wait_for_alert_message()
    logger.info("사이드바에서 채팅방 삭제 완료")

    # 테스트 종료 전 최종 화면을 눈으로 확인한다.
    sidebar.pause_for_debugging(seconds=2)
    logger.info("사이드바 더보기 메뉴 테스트 완료")
