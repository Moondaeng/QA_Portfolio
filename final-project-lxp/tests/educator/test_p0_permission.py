"""교육자 전용 과목 관리 기능의 학습자 권한 차단 TC."""

import os

import pytest

from pages.learner.content_page import LearnerContentPage


def _required_url(variable_name: str) -> str:
    """QA 전용 권한 검증 URL을 가져오고, 없으면 테스트를 건너뛴다."""
    url = os.getenv(variable_name, "").strip()
    if not url:
        pytest.skip(f"{variable_name} 환경 변수가 설정되지 않았습니다.")
    return url


@pytest.mark.educator
@pytest.mark.learner
def test_tc011_learner_blocked_from_educator_course_management(learner_logged_in):
    """[TC-011] 학습자의 교육자 과목 편집 접근 차단을 확인한다.

    1. 학습자 세션으로 교육자 과목 편집 URL 접근
    2. 학습자 화면에서 과목 편집 제어 표시 여부 조회
    3. 과목 편집 제어가 노출되지 않는지 확인
    """
    educator_edit_url = _required_url("EDUCATOR_COURSE_EDIT_URL")
    learner_page = LearnerContentPage(learner_logged_in)

    learner_page.navigate(educator_edit_url)
    current_url = learner_logged_in.current_url

    edit_control_visible = learner_page.is_edit_mode_control_visible()

    assert not edit_control_visible, (
        "학습자 화면에 교육자 전용 과목 편집 기능이 노출되었습니다. "
        f"current_url={current_url}, requested_url={educator_edit_url}, "
        f"edit_control_visible={edit_control_visible}"
    )
