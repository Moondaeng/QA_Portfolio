import pytest

from pages.login_page import LoginPage

def test_learner_login(driver, base_url, learner_account):
    """학습자 계정으로 정상 로그인을 수행하고 메인 페이지로 이동하는지 검증한다.

    1. 기본 URL로 이동하여 로그인 페이지로 리다이렉트 확인
    2. 학습자 이메일, 비밀번호 입력 후 로그인 버튼 클릭
    3. 로그인 완료 후 LXP 메인 화면으로 정상 이동 확인
    """
    login_page = LoginPage(driver)
    login_page.navigate(base_url)

    login_page.login(
        learner_account["user_id"],
        learner_account["password"],
    )

    is_logged_in = login_page.wait_until_logged_in(timeout=15)
    assert is_logged_in, "학습자 로그인 완료 후 페이지 전환에 실패했습니다."
