import pytest

from pages.debug_helper import pause_for_debugging
from pages.learner.class_home import LearnClassHome


pytestmark = pytest.mark.learner

def test_008_010_015_016_course_preview_more_flow(
    learner_logged_in_with_learner_driver,
):
    """[TC-008, TC-010, TC-015, TC-016] 과목 더보기 흐름을 확인한다.

    1. 클래스 홈의 과목 미리보기와 더보기 표시 확인
    2. 더보기가 사라질 때까지 추가 과목 불러오기
    3. 과목 수 증가와 펼쳐진 항목의 표시·텍스트 확인
    """
    home = LearnClassHome(learner_logged_in_with_learner_driver)
    initial_items = home.get_visible_course_previews()

    # TC-015: 표시 범위를 초과한 과목이 있으면 [더보기]가 노출된다.
    assert home.is_course_more_visible(scroll_to_section=False), (
        "학습 과목 [더보기]가 표시되지 않습니다."
    )

    # TC-016: [더보기]가 사라질 때까지 추가 과목을 모두 불러온다.
    expanded_items = home.expand_all_course_previews(
        initial_items=initial_items,
    )
    assert len(expanded_items) > len(initial_items), (
        "[더보기] 후 추가 과목이 표시되지 않았습니다."
    )
    assert not home.is_course_more_visible(scroll_to_section=False), (
        "모든 과목을 불러온 뒤에도 [더보기]가 남아 있습니다."
    )

    # TC-008: 펼쳐진 모든 학습 과목 미리보기가 화면에 표시된다.
    assert expanded_items, "표시된 학습 과목 미리보기가 없습니다."
    assert all(item.is_displayed() for item in expanded_items), (
        "화면에 표시되지 않은 학습 과목 미리보기가 있습니다."
    )

    # TC-010: 펼쳐진 모든 과목의 콘텐츠 유형과 명칭이 비어 있지 않다.
    preview_texts = [item.text.strip() for item in expanded_items]
    assert preview_texts, "학습 콘텐츠가 포함된 과목 미리보기가 없습니다."
    assert all(preview_texts), (
        "콘텐츠 유형 또는 명칭이 비어 있는 과목 미리보기가 있습니다."
    )

@pytest.mark.smoke
def test_018_open_all_courses_from_class_home(learner_logged_in_with_learner_driver):
    """[TC-018] 클래스 홈 학습 과목의 [전체 보기]로 이동한다.

    1. 클래스 홈에서 학습 과목 전체 보기 선택
    2. 현재 URL에 courses 경로가 포함되는지 확인
    """
    home = LearnClassHome(learner_logged_in_with_learner_driver)

    home.open_all_courses()

    assert "courses" in learner_logged_in_with_learner_driver.current_url.lower()

@pytest.mark.smoke
def test_079_open_all_schedules_from_class_home(learner_logged_in_with_learner_driver):
    """[TC-079] 클래스 홈 수업 일정의 [전체 보기]로 이동한다.

    1. 클래스 홈에서 수업 일정 전체 보기 선택
    2. 현재 URL에 schedules 경로가 포함되는지 확인
    """
    home = LearnClassHome(learner_logged_in_with_learner_driver)

    home.open_all_schedules()

    assert "schedules" in learner_logged_in_with_learner_driver.current_url.lower()

    # pause_for_debugging(2)

@pytest.mark.smoke
def test_119_open_all_board_posts_from_class_home(learner_logged_in_with_learner_driver):
    """[TC-119] 클래스 홈 게시판의 [전체 보기]로 이동한다.

    1. 클래스 홈에서 게시판 전체 보기 선택
    2. 현재 URL에 articles 경로가 포함되는지 확인
    """
    home = LearnClassHome(learner_logged_in_with_learner_driver)

    home.open_all_board_posts()

    assert "articles" in learner_logged_in_with_learner_driver.current_url.lower()
