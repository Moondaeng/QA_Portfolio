import logging

import pytest

from src.firefoxPages.firefox_login_page import FirefoxLoginPage
from src.firefoxPages.firefox_make_agent import FirefoxMakeAgent
from src.firefoxPages.firefox_new_talk import FirefoxNewTalk
from src.firefoxPages.firefox_talking_withAI import FirefoxTalkingWithAI
from tests.firefox.firefox_test_data import FirefoxTestData

logger = logging.getLogger(__name__)

# @pytest.mark.skip
@pytest.mark.firefox
def test_firefox_make_agent(firefox_driver):
    """에이전트 만들기 기능을 테스트한다.

    추가 메뉴, 이름, 설명, 카테고리, 규칙, 시작 대화,
    미리보기 및 만들기 동작을 확인한다.
    """
    test_data = FirefoxTestData()

    logger.info("에이전트 만들기 테스트 시작")

    login = FirefoxLoginPage(firefox_driver, action_delay=0.5)
    new_talk = FirefoxNewTalk(firefox_driver, action_delay=0.5)
    talking_ai = FirefoxTalkingWithAI(firefox_driver, action_delay=0.5)
    make_agent = FirefoxMakeAgent(firefox_driver, action_delay=0.5)

    login.login_with_account(
        test_data.TEST_USER_ID,
        test_data.TEST_PASSWORD,
    )
    logger.info("로그인 동작 완료")

    talking_ai.close_popup()
    logger.info("개인 토큰 팝업 확인 완료")

    new_talk.select_agent(create_new_agent=True)
    logger.info("새 에이전트 만들기 화면 진입 완료")

    make_agent.click_agent_plus_menu()
    logger.info("에이전트 만들기 메뉴 선택 완료")

    make_agent.hover_to_main()
    make_agent.input_agent_name("에이전트이름")

    make_agent.hover_to_main()
    make_agent.input_agent_description("에이전트 설명 TEST")

    make_agent.select_agent_category(test_data.AGENT_CATEGORY_INDEX)

    make_agent.hover_to_main()
    make_agent.input_agent_rule("에이전트 규칙 test")

    make_agent.input_agent_conversation_starters("시작 대화 test")
    logger.info("에이전트 기본 정보 입력 완료")

    make_agent.scroll_make_agent_page()
    make_agent.hover_to_main()

    make_agent.send_preview_message("test")
    logger.info("에이전트 미리보기 메시지 전송 완료")

    make_agent.click_make_agent()
    logger.info("에이전트 만들기 완료")

    # 테스트 종료 전 최종 화면을 눈으로 확인한다.
    make_agent.pause_for_debugging(seconds=2)
    logger.info("에이전트 만들기 테스트 완료")
