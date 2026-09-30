import pytest

from pages.learner.course_page import LearnCourse
from tests.learner.test_data.course_data import (
    COURSE_DETAIL_SELECTION,
    LEARNING_START_SELECTION,
    CourseSelectionData,
)


pytestmark = pytest.mark.learner

def _open_course(
    learner_logged_in_with_learner_driver,
    selection: CourseSelectionData,
) -> LearnCourse:
    """학습 과목 목록을 열고 지정한 과목 상세로 이동한다.

    Args:
        learner_logged_in_with_learner_driver: 클래스 홈까지 진입한 학습자 WebDriver.
        selection: 과목과 수업 선택에 사용할 인덱스 데이터.

    Returns:
        LearnCourse: 과목 상세로 이동할 때 사용한 Page Object.
    """
    course = LearnCourse(learner_logged_in_with_learner_driver)
    course.open_course_list_from_menu()
    course.select_course(selection.course_index)
    return course

def test_022_open_assigned_course_list(learner_logged_in_with_learner_driver):
    """[TC-022] 배정되고 공개된 과목 목록 조회.

    1. 클래스 사이드바의 [학습 과목] 메뉴 선택
    2. 학습 과목 목록 제목과 과목 항목 노출 확인
    """
    course = LearnCourse(learner_logged_in_with_learner_driver)
    course.open_course_list_from_menu()
    heading, course_items = course.wait_for_course_list()

    assert heading.is_displayed(), "학습 과목 목록 제목이 표시되지 않았습니다."
    assert all(item.is_displayed() for item in course_items), (
        "학습 과목 목록에 표시되지 않은 과목 항목이 있습니다."
    )

def test_026_navigate_to_course_detail(learner_logged_in_with_learner_driver):
    """[TC-026] 과목 선택 시 상세 화면 이동.

    1. 학습 과목 메뉴로 이동
    2. 테스트 데이터에 지정된 인덱스의 과목 선택
    3. 과목 상세 화면의 필수 탭 노출 확인
    """
    course = _open_course(
        learner_logged_in_with_learner_driver,
        COURSE_DETAIL_SELECTION,
    )
    expected_tabs = {"수업 목록", "학습 현황", "학습맵", "과목 소개"}
    visible_tabs = set(course.wait_for_course_detail_tabs())

    assert expected_tabs <= visible_tabs, (
        "과목 상세 화면의 필수 탭이 모두 표시되지 않았습니다. "
        f"missing={sorted(expected_tabs - visible_tabs)}, "
        f"visible={sorted(visible_tabs)}"
    )

def test_038_start_learning(learner_logged_in_with_learner_driver):
    """[TC-038] 학습 화면 진입.

    1. 학습 과목 목록에서 테스트 데이터에 지정된 과목 선택
    2. [이어서 학습] 버튼 클릭
    3. 학습 화면 진입 결과 확인
    """
    course = _open_course(
        learner_logged_in_with_learner_driver,
        LEARNING_START_SELECTION,
    )
    course.continue_learning()
    learning_end_link = course.wait_for_learning_end_link()

    assert learning_end_link.is_displayed(), "[학습 종료] 링크가 표시되지 않았습니다."
    assert learning_end_link.is_enabled(), "[학습 종료] 링크가 활성화되지 않았습니다."
