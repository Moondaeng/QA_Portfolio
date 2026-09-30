import pytest

from pages.learner.schedule_page import LearnerSchedulePage


pytestmark = pytest.mark.learner

def test_100_confirm_schedule_detail_is_visible(
    learner_logged_in_with_learner_driver,
):
    """[TC-100] 현재 달력의 첫 번째 표시 일정 상세 정보를 확인한다.

    1. 수업 일정 메뉴로 이동
    2. 일정 컨테이너에서 첫 번째 표시 일정을 선택하고 제목 보관
    3. 선택한 일정과 상세 제목 일치 확인
    """
    schedule = LearnerSchedulePage(learner_logged_in_with_learner_driver)
    schedule.open_schedule_from_menu()
    schedule_container = schedule.wait_for_schedule_container()
    assert schedule_container.is_displayed(), "수업 일정 영역이 표시되지 않았습니다."

    selected_title = schedule.open_first_schedule()
    detail_title, _ = schedule.get_schedule_detail()

    assert detail_title == selected_title, (
        f"선택한 일정과 상세 제목 불일치: selected={selected_title!r}, detail={detail_title!r}"
    )
