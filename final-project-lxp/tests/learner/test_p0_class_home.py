import pytest
from selenium.webdriver.support.ui import WebDriverWait

from pages.debug_helper import pause_for_debugging
from pages.learner.class_home import LearnClassHome
from tests.learner.support import (
    normalized_url_path,
    required_url,
    wait_for_login_destination,
)


pytestmark = pytest.mark.learner

def test_001_enter_class_home(learner_logged_in_with_learner_driver):
    """[TC-001] 학습자의 클래스 홈 접근 성공.

    1. 학습자 계정으로 로그인
    2. 클래스 목록에서 소속 클래스 선택
    """
    expected_path = normalized_url_path(required_url("CLASS_HOME_URL"))
    WebDriverWait(learner_logged_in_with_learner_driver, 15).until(
        lambda driver: normalized_url_path(driver.current_url)
        == expected_path,
        message="지정된 클래스 홈으로 이동하지 않았습니다.",
    )
    actual_path = normalized_url_path(
        learner_logged_in_with_learner_driver.current_url
    )

    assert actual_path == expected_path, (
        "지정된 클래스 홈 경로와 현재 경로가 다릅니다: "
        f"expected={expected_path}, actual={actual_path}"
    )

    pause_for_debugging(3)

def test_003_enter_class_home_without_login(
    learner_logged_out_with_learner_driver,
):
    """[TC-003] 로그인하지 않은 사용자의 클래스 홈 접근.

    1. 로그인하지 않은 브라우저 준비
    2. 클래스 홈 URL에 직접 접근
    """
    class_home_url = required_url("CLASS_HOME_URL")

    class_home = LearnClassHome(learner_logged_out_with_learner_driver)
    class_home.open_url(class_home_url)
    login_url, email_input = wait_for_login_destination(
        learner_logged_out_with_learner_driver
    )

    assert "accounts" in login_url.lower() or "signin" in login_url.lower(), (
        f"로그인 페이지로 이동하지 않았습니다: current_url={login_url}"
    )
    assert email_input.get_attribute("name") == "loginId", (
        "일반 로그인 화면의 이메일 입력란을 확인하지 못했습니다."
    )
