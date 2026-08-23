import logging

import pytest

from src.firefoxPages.firefox_login_page import FirefoxLoginPage
from src.firefoxPages.firefox_new_talk import FirefoxNewTalk
from src.firefoxPages.firefox_sidebar import FirefoxSidebar
from src.firefoxPages.firefox_talking_withAI import FirefoxTalkingWithAI
from tests.firefox.firefox_test_data import FirefoxTestData

logger = logging.getLogger(__name__)

# @pytest.mark.skip
@pytest.mark.firefox
def test_ai_response(firefox_driver):
    """AI 응답 메시지의 복사 및 재생성 기능을 테스트한다."""
    test_data = FirefoxTestData()

    logger.info("AI 응답 기능 테스트 시작")

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

    sidebar.search_chat_room(
        "자료",
        test_data.SEARCH_CHAT_ROOM_INDEX,
    )
    logger.info("사이드바 채팅방 키워드 검색 완료")

    talking_ai.hover_to_main()

    clicked = talking_ai.click_scroll_bottom_button()

    if clicked:
        logger.info("맨 아래로 스크롤 버튼 클릭")

    talking_ai.input_user_message("호랑이는 고양이과야?")
    logger.info("질문 메시지 전송 완료")

    talking_ai.click_ai_recommended_question(
        test_data.RECOMMEND_QUESTION_INDEX
    )
    logger.info("AI 추천 질문 선택 완료")

    talking_ai.copy_ai_response_message(
        test_data.AI_MESSAGE_INDEX
    )
    logger.info("AI 응답 복사 버튼 클릭 완료")

    talking_ai.regenerate_ai_response_message(
        test_data.AI_MESSAGE_INDEX
    )
    logger.info("AI 응답 재생성 버튼 클릭 완료")

    # 테스트 종료 전 최종 화면을 눈으로 확인한다.
    talking_ai.pause_for_debugging(seconds=2)
    logger.info("AI 응답 기능 테스트 완료")
