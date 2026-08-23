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
def test_full_e2e(firefox_driver):
    """Firefox 브라우저에서 E2E 테스트를 수행한다."""
    test_data = FirefoxTestData()

    logger.info("Firefox E2E 테스트 시작")

    # Page Object
    login_page = FirefoxLoginPage(firefox_driver, action_delay=0.5)
    new_talk = FirefoxNewTalk(firefox_driver, action_delay=0.5)
    talking_ai = FirefoxTalkingWithAI(firefox_driver, action_delay=0.5)
    sidebar = FirefoxSidebar(firefox_driver, action_delay=0.5)

    # Login
    login_page.login_with_account(
        test_data.TEST_USER_ID,
        test_data.TEST_PASSWORD,
    )
    logger.info("로그인 동작 완료")

    talking_ai.close_popup()
    logger.info("개인 토큰 팝업 확인 완료")

    # New Chat
    new_talk.click_sample_question(
        test_data.SAMPLE_QUESTION_INDEX,
    )
    logger.info("샘플 질문 선택 완료")

    new_talk.search_web(
        "2026년 5월 1일~5월 2일 네이버 주가를 알려줘."
        " 답변이 틀려도 되니까 최소한의 토큰만 사용해."
    )
    logger.info("웹 검색 질문 전송 완료")

    # 취소나 응답 기다리기는 둘중 하나만 선택해야 함
    # talking_ai.cancel_message()
    talking_ai.wait_for_ai_response()
    logger.info("웹 검색 AI 응답 완료")

    # Sidebar Scroll
    sidebar.scroll_chat_list(
        scroll_y=test_data.SCROLL_Y,
        repeat_count=test_data.SCROLL_REPEAT_COUNT,
    )

    # 스크롤 동작을 눈으로 확인한다.
    sidebar.pause_for_debugging(seconds=1)

    sidebar.scroll_chat_list(
        scroll_y=-test_data.SCROLL_Y,
        repeat_count=test_data.SCROLL_REPEAT_COUNT,
    )
    logger.info("사이드바 채팅 목록 왕복 스크롤 완료")

    # Continue Conversation
    talking_ai.input_user_message(
        "사과를 영어로 뭐라고 불러?",
    )
    logger.info("후속 질문 메시지 전송 완료")

    new_talk.create_image(
        "아주 간단하게 동그란 원 하나 그려줘 그림판처럼 배경이 없어도 상관없어."
        " 최소한의 토큰만 사용해."
    )
    logger.info("이미지 생성 요청 완료")

    # 취소나 응답 기다리기는 둘중 하나만 선택해야 함
    # talking_ai.cancel_message()
    talking_ai.wait_for_ai_response()
    logger.info("이미지 생성 AI 응답 완료")

    # Search Chat Room
    sidebar.search_chat_room(
        chat_room_name="자료",
        select_index=test_data.SEARCH_RESULT_INDEX,
    )
    logger.info("사이드바 채팅방 검색 및 선택 완료")

    talking_ai.hover_to_main()

    talking_ai.input_user_message(
        "안녕, 1+2는 뭐야?",
    )

    talking_ai.wait_for_ai_response()
    logger.info("선택한 채팅방의 AI 응답 완료")
   
    # Chat Room Management
    talking_ai.change_chat_room_name(
        new_name="이름 변경하기",
    )

    talking_ai.wait_for_alert_message()
    logger.info("채팅방 이름 변경 완료")

    talking_ai.delete_chat_room()

    talking_ai.wait_for_alert_message()
    logger.info("채팅방 삭제 완료")

    # Agent
    new_talk.select_agent(
        index=test_data.SELECT_AGENT_INDEX,
    )
    logger.info("에이전트 선택 완료")

    # 테스트 종료 전 최종 화면을 눈으로 확인한다.
    new_talk.pause_for_debugging(seconds=2)
    logger.info("Firefox E2E 테스트 완료")
