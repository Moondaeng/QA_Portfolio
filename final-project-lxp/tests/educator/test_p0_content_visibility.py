import os

import pytest

from pages.educator.course_page import EducatorCoursePage
from pages.learner.content_page import LearnerContentPage


def _required_url(variable_name: str) -> str:
    """QA 전용 URL 환경변수를 가져오고, 없으면 테스트 데이터를 준비하도록 건너뛴다."""
    url = os.getenv(variable_name, "").strip()
    if not url:
        pytest.skip(f"{variable_name} 환경 변수가 설정되지 않았습니다.")
    return url


@pytest.mark.educator
def test_tc038_educator_course_edit_switch_visible(educator_logged_in):
    """[TC-038] 교육자의 과목 편집 모드 진입과 수업 순서 변경 UI 노출을 검증한다.

    1. 지정된 QA 과목 편집 URL로 이동
    2. 과목 편집 모드 활성화
    3. 수업 순서 변경 UI 표시 확인
    """
    edit_url = _required_url("EDUCATOR_COURSE_EDIT_URL")
    course_page = EducatorCoursePage(educator_logged_in)

    course_page.navigate_to_course_edit_page(edit_url)
    course_page.enter_course_edit_mode()

    assert course_page.is_reorder_mode_displayed(), (
        "과목 편집 모드 진입 후 수업 순서 변경 UI가 표시되지 않았습니다."
    )


@pytest.mark.learner
def test_tc039_learner_blocked_from_lecture_reordering(learner_logged_in):
    """[TC-039] 학습자에게 교육자용 과목 편집 제어가 노출되지 않는지 검증한다.

    1. 학습자 세션으로 교육자 과목 편집 URL 접근
    2. 교육자 전용 편집 제어가 표시되지 않는지 확인
    """
    edit_url = _required_url("EDUCATOR_COURSE_EDIT_URL")
    learner_page = LearnerContentPage(learner_logged_in)

    learner_page.navigate(edit_url)

    assert not learner_page.is_edit_mode_control_visible(), (
        "학습자 화면에 교육자 전용 '과목 편집' 제어가 노출되었습니다."
    )


@pytest.mark.learner
def test_tc090_private_lecture_not_visible_to_learner(learner_logged_in):
    """[TC-090] 비공개 수업 링크가 학습자 수업 목록에 보이지 않는지 검증한다.

    1. 학습자 세션으로 지정된 과목 이동
    2. 비공개 수업 URL의 링크가 표시되지 않는지 확인
    """
    course_url = _required_url("LEARNER_COURSE_URL")
    private_lecture_url = _required_url("PRIVATE_LECTURE_URL")
    learner_page = LearnerContentPage(learner_logged_in)

    learner_page.navigate(course_url)

    assert not learner_page.is_target_link_visible(private_lecture_url), (
        "비공개 수업 링크가 학습자 화면에 노출되었습니다."
    )


@pytest.mark.learner
def test_tc091_private_lecture_direct_access_blocked(learner_logged_in):
    """[TC-091] 학습자의 비공개 수업 직접 접근이 차단되는지 검증한다.

    1. 학습자 세션으로 비공개 수업 URL 직접 접근
    2. 직접 접근 차단 여부 확인
    """
    private_lecture_url = _required_url("PRIVATE_LECTURE_URL")
    learner_page = LearnerContentPage(learner_logged_in)

    learner_page.navigate(private_lecture_url)

    assert learner_page.is_direct_access_blocked(private_lecture_url), (
        "비공개 수업 직접 접근이 차단되지 않았습니다."
    )


@pytest.mark.learner
def test_tc092_private_material_not_visible_to_learner(learner_logged_in):
    """[TC-092] 비공개 자료 링크가 학습자 화면에 보이지 않는지 검증한다.

    1. 학습자 세션으로 지정된 과목 이동
    2. 비공개 자료 URL의 링크가 표시되지 않는지 확인
    """
    course_url = _required_url("LEARNER_COURSE_URL")
    private_material_url = _required_url("PRIVATE_MATERIAL_URL")
    learner_page = LearnerContentPage(learner_logged_in)

    learner_page.navigate(course_url)

    assert not learner_page.is_target_link_visible(private_material_url), (
        "비공개 자료 링크가 학습자 화면에 노출되었습니다."
    )


@pytest.mark.learner
def test_tc093_private_material_direct_access_blocked(learner_logged_in):
    """[TC-093] 학습자의 비공개 자료 직접 접근이 차단되는지 검증한다.

    1. 학습자 세션으로 비공개 자료 URL 직접 접근
    2. 직접 접근 차단 여부 확인
    """
    private_material_url = _required_url("PRIVATE_MATERIAL_URL")
    learner_page = LearnerContentPage(learner_logged_in)

    learner_page.navigate(private_material_url)

    assert learner_page.is_direct_access_blocked(private_material_url), (
        "비공개 자료 직접 접근이 차단되지 않았습니다."
    )
