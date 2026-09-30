import re

import pytest

from pages.debug_helper import pause_for_debugging
from pages.learner.course_page import LearnCourse


pytestmark = pytest.mark.learner


def _open_course_list(learner_logged_in_with_learner_driver) -> LearnCourse:
    """학습 과목 목록을 열고 Page Object를 반환한다."""
    course = LearnCourse(learner_logged_in_with_learner_driver)
    course.open_course_list_from_menu()
    return course


def _open_status_by_continue_state(
    learner_logged_in_with_learner_driver,
    has_continue: bool,
) -> LearnCourse:
    """이어서 학습 버튼 유무에 맞는 첫 과목을 선택하고 학습 현황을 연다."""
    course = _open_course_list(learner_logged_in_with_learner_driver)
    course.select_first_course_by_continue_state(has_continue)
    course.open_learning_status()
    return course

@pytest.mark.smoke
def test_037_open_course_lesson_by_name(
    learner_logged_in_with_learner_driver,
):
    """[TC-037] 첫 번째 과목 상세의 탭 구성을 확인한다.

    1. 학습 과목 목록에서 첫 번째 과목 선택
    2. 과목 상세의 탭 이름 조회
    3. 수업 목록·학습 현황·학습맵·과목 소개 탭 순서 확인
    """
    course = _open_course_list(learner_logged_in_with_learner_driver)

    # 학습 과목 목록에서 첫 번째 과목을 선택한다.
    course.select_course(0)

    tab_names = course.get_course_detail_tab_names()
    assert tab_names == ["수업 목록", "학습 현황", "학습맵", "과목 소개"], (
        f"과목 상세 탭 구성이 다릅니다: {tab_names}"
    )

def test_051_learning_status_is_visible_in_course_list(
    learner_logged_in_with_learner_driver,
):
    """[TC-051] 과목 목록을 천천히 스크롤하며 학습 현황 표시를 확인한다.

    1. 학습 과목 목록으로 이동
    2. 목록을 스크롤하며 과목 항목 조회
    3. 항목이 표시되고 텍스트가 비어 있지 않은지 확인
    """
    course = _open_course_list(learner_logged_in_with_learner_driver)

    items = course.slowly_scroll_course_list(delay=0.5)

    assert items, "학습 과목 목록이 비어 있습니다."
    assert all(item.is_displayed() and item.text.strip() for item in items), (
        "표시되지 않거나 내용이 비어 있는 학습 과목이 있습니다."
    )

def test_054_055_058_practice_and_test_scores_are_visible(
    learner_logged_in_with_learner_driver,
):
    """[TC-054, TC-055, TC-058] 실습·테스트 점수 정보를 확인한다.

    1. 이어서 학습이 가능한 첫 과목의 학습 현황으로 이동
    2. 학습 현황을 스크롤하며 점수 영역 조회
    3. 실습 자료·테스트 점수 영역과 학습 현황 요약값 확인
    """
    course = _open_status_by_continue_state(
        learner_logged_in_with_learner_driver,
        True,
    )

    course.slowly_scroll_learning_status(delay=0.5)
    practice_section, test_section = course.wait_for_score_sections()
    summary = course.get_learning_status_summary()

    # TC-054: 실습 자료 점수 영역이 표시된다.
    assert practice_section.is_displayed(), "실습 자료 점수 영역이 표시되지 않았습니다."

    # TC-055: 테스트 점수 영역이 표시된다.
    assert test_section.is_displayed(), "테스트 점수 영역이 표시되지 않았습니다."

    # TC-058: 학습 진행률과 평균 점수에 숫자 또는 미응시 표시(-)가 표시된다.
    assert re.fullmatch(r"\d+(?:\.\d+)?%", summary["learning_progress"]), (
        f"학습 진행률 표시값이 올바르지 않습니다: {summary['learning_progress']!r}"
    )
    for label, key in (
        ("평균 실습 자료 점수", "average_practice_score"),
        ("평균 테스트 점수", "average_test_score"),
    ):
        value = summary[key]
        assert value == "-" or re.fullmatch(r"\d+(?:\.\d+)?(?:점|%)?", value), (
            f"{label} 표시값이 올바르지 않습니다: {value!r}"
        )

    pause_for_debugging(2)

def test_057_061_unstarted_course_status_is_visible(
    learner_logged_in_with_learner_driver,
):
    """[TC-057, TC-061] 미학습 과목의 점수 상태를 확인한다.

    1. 이어서 학습 버튼이 없는 첫 과목의 학습 현황으로 이동
    2. 학습 현황을 스크롤하며 정보 조회
    3. 점수 없음 표시와 대시 또는 0 표시 확인
    """
    course = _open_status_by_continue_state(
        learner_logged_in_with_learner_driver,
        False,
    )

    texts = course.slowly_scroll_learning_status(delay=0.5)

    # TC-057: 미입력 점수가 대시(-)로 표시된다.
    assert any("-" in text for text in texts), (
        "점수 없음 표시('-')를 찾지 못했습니다."
    )

    # TC-061: 미학습 현황 정보가 대시 또는 0으로 표시된다.
    assert texts, "학습 현황 정보가 표시되지 않습니다."
    assert any("-" in text or re.search(r"\b0(?:\.0+)?\b", text) for text in texts)
