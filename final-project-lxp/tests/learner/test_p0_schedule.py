import pytest

from pages.learner.schedule_page import LearnerSchedulePage


pytestmark = pytest.mark.learner

def test_078_open_schedule_from_class_menu(
    learner_logged_in_with_learner_driver,
):
    """[TC-078] 클래스 메뉴를 통한 수업 일정 화면 이동.

    1. 클래스 사이드바 메뉴 확인
    2. [수업 일정] 메뉴 선택
    3. 로딩이 완료된 일정 컨테이너 노출 확인
    """
    schedule = LearnerSchedulePage(learner_logged_in_with_learner_driver)
    schedule.open_schedule_from_menu()
    schedule_container = schedule.wait_for_schedule_container()

    assert schedule_container.is_displayed(), "수업 일정 영역이 표시되지 않았습니다."
