import os

import pytest
from pages.educator.classroom_home_page import (
    ClassroomHomePage,
    get_classroom_id,
    get_classroom_url,
)


@pytest.fixture(autouse=True)
def reset_to_classroom_home(educator_logged_in, base_url):
    """공유 교육자 세션을 각 TC 시작 전 QA6_2 클래스 홈으로 초기화한다.

    `educator_logged_in`은 module-scope라 앞선 TC가 남긴 메뉴·모달·스크롤
    상태가 다음 TC에 이어질 수 있다. 이 fixture는 클래스 홈 TC에만 자동
    적용되어 각 시나리오가 동일한 시작 화면에서 실행되도록 한다.
    """
    classroom_url = get_classroom_url()
    home_page = ClassroomHomePage(educator_logged_in)
    home_page.navigate_to_classroom(classroom_url)

    assert home_page.is_classroom_context_preserved(), (
        "클래스 홈 TC 실행 전 QA6_2 클래스룸으로 초기화하지 못했습니다."
    )

    yield


@pytest.mark.smoke
@pytest.mark.educator
def test_tc001_classroom_menu_access(educator_logged_in, base_url):
    """[TC-001] QA6_2팀 최종프로젝트 클래스룸 4개 대상 메뉴 접근 검증.

    1. 교육자 계정으로 로그인 후 [QA6_2팀] 최종프로젝트 클래스룸 진입
    2. 클래스 홈·학습 과목·수업 일정·게시판 4개 메뉴 노출 및 접근 확인
    """
    home_page = ClassroomHomePage(educator_logged_in)

    # 각 메뉴의 노출과 클릭 후 클래스룸 컨텍스트 유지를 함께 확인한다.
    menus = [
        ("클래스 홈", "classrooms"),
        ("학습 과목", "courses"),
        ("수업 일정", "schedules"),
        ("게시판", "articles"),
    ]
    for menu, url_keyword in menus:
        is_visible = home_page.is_menu_visible(menu)
        assert is_visible, f"클래스룸 4개 핵심 메뉴 중 '{menu}' 메뉴가 노출되지 않았습니다."
        home_page.click_menu(menu)
        assert home_page.wait_for_url_contains(url_keyword, timeout=10), (
            f"'{menu}' 메뉴 클릭 후 해당 화면으로 이동하지 못했습니다."
        )
        assert home_page.is_classroom_context_preserved(), (
            f"'{menu}' 메뉴 클릭 후 QA6_2 클래스룸 컨텍스트가 유지되지 않았습니다."
        )

@pytest.mark.educator
def test_tc005_schedule_view_all_navigation(educator_logged_in, base_url):
    """[TC-005] 수업 일정 전체 보기의 메뉴 이동 검증.

    1. 교육자 계정으로 [QA6_2팀] 클래스 홈에 진입
    2. 수업 일정 영역의 [전체 보기] 선택
    3. 수업 일정 메뉴 화면으로 정상 이동하고 컨텍스트가 유지되는지 확인
    """
    home_page = ClassroomHomePage(educator_logged_in)
    home_page.click_menu("클래스 홈")
    home_page.click_schedule_view_all()

    is_schedule_page = home_page.is_schedule_page_displayed(timeout=10)
    assert is_schedule_page, "수업 일정 전체 보기 클릭 후 일정 페이지로 이동하지 못했습니다."

@pytest.mark.educator
def test_tc006_create_schedule_navigation(educator_logged_in, base_url):
    """[TC-006] 새 일정 만들기의 수업 일정 작성 화면 이동 검증.

    1. 교육자 계정으로 [QA6_2팀] 클래스 홈에 진입
    2. 수업 일정 영역의 [새 일정 만들기] 선택
    3. 수업 일정 작성 화면 또는 모달로 정상 이동하는지 확인
    """
    home_page = ClassroomHomePage(educator_logged_in)
    home_page.click_menu("클래스 홈")
    home_page.click_create_schedule()

    assert home_page.is_schedule_create_form_displayed(timeout=10), (
        "새 일정 만들기 클릭 후 일정 작성 화면 또는 모달이 표시되지 않았습니다."
    )

@pytest.mark.educator
def test_tc007_course_view_all_navigation(educator_logged_in, base_url):
    """[TC-007] 학습 과목 전체 보기의 메뉴 이동 및 과목 목록 노출 검증.

    1. 교육자 계정으로 [QA6_2팀] 클래스 홈에 진입
    2. 학습 과목 영역의 [전체 보기] 선택
    3. 학습 과목 메뉴 화면으로 이동하여 과목 목록이 표시되는지 확인
    """
    home_page = ClassroomHomePage(educator_logged_in)
    home_page.click_menu("클래스 홈")
    home_page.click_course_view_all()

    # 과목 목록 화면으로 정상 이동하고 과목 목록 영역이 노출되는지 검증
    is_displayed = home_page.is_course_list_displayed(timeout=10)
    assert is_displayed, "학습 과목 전체 보기 클릭 후 과목 목록 화면이 정상적으로 표시되지 않았습니다."

@pytest.mark.educator
def test_tc008_course_more_navigation(educator_logged_in, base_url):
    """[TC-008] 학습 과목 목록 더보기의 추가 항목 노출 검증.

    1. 교육자 계정으로 [QA6_2팀] 클래스 홈에 진입
    2. 학습 과목 영역의 [더보기] 선택
    3. 클래스 홈을 유지한 채 표시되는 학습 과목 항목 수가 증가하는지 확인
    """
    home_page = ClassroomHomePage(educator_logged_in)
    home_page.click_menu("클래스 홈")
    url_before_click = educator_logged_in.current_url
    initial_course_count = home_page.get_visible_home_course_count()

    assert initial_course_count > 0, "클래스 홈 학습 과목 영역에 표시된 과목이 없습니다."
    home_page.click_course_more()

    increased_course_count = home_page.wait_for_home_course_count_increase(
        initial_course_count,
        timeout=10,
    )

    assert educator_logged_in.current_url == url_before_click, (
        "학습 과목 더보기 클릭 후 클래스 홈 화면이 변경되었습니다."
    )
    assert home_page.is_classroom_context_preserved(), (
        "학습 과목 더보기 클릭 후 QA6_2 클래스룸 컨텍스트가 유지되지 않았습니다."
    )
    assert increased_course_count > initial_course_count, (
        "학습 과목 더보기 클릭 후 표시된 과목 항목 수가 증가하지 않았습니다."
    )
