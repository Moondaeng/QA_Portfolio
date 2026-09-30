import pytest

from pages.learner.board_page import LearnerBoardPage


pytestmark = pytest.mark.learner


def _open_board(learner_logged_in_with_learner_driver) -> LearnerBoardPage:
    """게시판 목록을 열고 조작에 사용할 Page Object를 반환한다."""
    board = LearnerBoardPage(learner_logged_in_with_learner_driver)
    board.open_board()
    return board

@pytest.mark.smoke
def test_124_open_first_post_detail(learner_logged_in_with_learner_driver):
    """[TC-124] 게시판 첫 번째 게시글의 상세 영역을 확인한다.

    1. 게시판 목록으로 이동하여 첫 번째 게시글 선택
    2. 제목과 작성 시각을 포함한 게시글 상세 영역 조회
    3. 게시글 상세 영역 노출 확인
    """
    board = _open_board(learner_logged_in_with_learner_driver)

    board.open_first_post()
    detail_section = board.wait_for_post_detail_section()

    assert detail_section.is_displayed(), "게시글 상세 영역이 표시되지 않았습니다."

def test_127_130_open_write_and_validate_required_title(
    learner_logged_in_with_learner_driver,
):
    """[TC-127, TC-130] 작성 화면 이동과 필수 제목 검증을 확인한다.

    1. 게시판에서 글쓰기 화면으로 이동
    2. 제목과 본문 입력란 확인
    3. 제목 없이 본문만 입력하고 저장 버튼 비활성화 확인
    """
    board = _open_board(learner_logged_in_with_learner_driver)

    # TC-127: 게시판 목록의 [글쓰기]를 통해 작성 화면을 연다.
    board.open_write_from_board()
    title_input = board.wait_for_first_visible(board.TITLE_INPUT)
    content_input = board.wait_for_first_visible(board.CONTENT_INPUT)

    assert title_input.get_attribute("name") == "title", (
        "게시글 제목 입력란으로 이동하지 않았습니다."
    )
    assert content_input.get_attribute("contenteditable") == "true", (
        "게시글 내용 입력란으로 이동하지 않았습니다."
    )

    # TC-130: 제목을 비우고 내용만 입력하면 저장 버튼이 비활성화된다.
    save_button = board.prepare_missing_required_title(
        "TC-130 필수 항목 검증을 위한 내용입니다.",
    )

    assert not save_button.is_enabled(), "제목이 비어 있는데 저장 버튼이 활성화되었습니다."
