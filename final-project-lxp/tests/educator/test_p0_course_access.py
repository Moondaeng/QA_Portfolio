import pytest
from pages.educator.classroom_home_page import ClassroomHomePage
from pages.educator.course_page import EducatorCoursePage


def _open_qa6_2_course_list(driver) -> EducatorCoursePage:
    """공유 교육자 세션을 QA6_2 클래스룸의 학습 과목 목록으로 초기화한다."""
    home_page = ClassroomHomePage(driver)
    home_page.select_qa6_2_classroom()
    home_page.click_menu("학습 과목")
    return EducatorCoursePage(driver)


@pytest.mark.educator
def test_tc009_educator_course_list_access(educator_logged_in):
    """[TC-009] 교육자의 배정된 과목 목록 조회 성공 검증.

    1. 교육자 계정으로 로그인 후 과목 메뉴로 이동
    2. 교육자에게 배정된 과목 목록이 1개 이상 정상 로드되는지 확인
    """
    course_page = _open_qa6_2_course_list(educator_logged_in)
    assert course_page.is_course_list_displayed(), (
        "교육자 클래스룸의 학습 과목 목록 제목 또는 과목 항목이 표시되지 않았습니다."
    )

@pytest.mark.educator
def test_tc015_active_course_detail_entry(educator_logged_in):
    """[TC-015] 활성 과목 선택 및 상세 화면 진입 확인.

    1. 교육자 계정으로 과목 목록 페이지 진입
    2. 과목 목록에서 활성화된 과목 선택
    3. 선택한 과목의 상세 화면(수업 목록 등)으로 이동하는지 확인
    """
    course_page = _open_qa6_2_course_list(educator_logged_in)
    list_url = educator_logged_in.current_url
    course_page.select_first_active_course()

    is_detail_loaded = course_page.is_course_detail_loaded(list_url)
    assert is_detail_loaded, "과목 카드 클릭 후 과목 상세 화면으로 진입하지 못했습니다."
