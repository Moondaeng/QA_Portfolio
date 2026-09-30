from datetime import UTC, datetime
from urllib.parse import urlparse

import pytest

from pages.learner.board_page import LearnerBoardPage
from tests.learner.support import required_url, wait_for_login_destination


pytestmark = pytest.mark.learner


def test_111_open_board_from_class_menu(learner_logged_in_with_learner_driver):
    """[TC-111] 클래스 메뉴를 통한 게시판 화면 이동.

    1. 클래스 사이드바 메뉴 확인
    2. [게시판] 메뉴 선택
    3. 게시판 URL 이동 확인
    """
    board = LearnerBoardPage(learner_logged_in_with_learner_driver)
    board.open_board()
    expected_url = required_url("BOARD_URL")
    current_url = board.wait_for_board_url(expected_url)

    assert urlparse(current_url).path.rstrip("/") == urlparse(
        expected_url
    ).path.rstrip("/"), (
        f"게시판 URL이 일치하지 않습니다: expected={expected_url}, "
        f"actual={current_url}"
    )

def test_116_open_new_post_page(learner_logged_in_with_learner_driver):
    """[TC-116] 게시글 작성 화면 이동.

    1. 클래스 홈의 게시판 영역 확인
    2. [새 게시글 작성] 버튼 클릭
    3. 게시글 제목과 본문 입력란 노출 확인
    """
    board = LearnerBoardPage(learner_logged_in_with_learner_driver)
    board.open_write_from_home()

def test_117_open_write_url_without_login(
    learner_logged_out_with_learner_driver,
):
    """[TC-117] 비로그인 상태에서 게시글 작성 화면 접근.

    1. 로그인하지 않은 브라우저 준비
    2. 게시글 작성 URL로 직접 이동
    """
    board = LearnerBoardPage(learner_logged_out_with_learner_driver)
    board.open_url(required_url("BOARD_WRITE_URL"))
    login_url, email_input = wait_for_login_destination(
        learner_logged_out_with_learner_driver
    )

    assert "accounts" in login_url.lower() or "signin" in login_url.lower(), (
        f"로그인 페이지로 이동하지 않았습니다: current_url={login_url}"
    )
    assert email_input.get_attribute("name") == "loginId", (
        "일반 로그인 화면의 이메일 입력란을 확인하지 못했습니다."
    )

def test_121_open_board_post_list(learner_logged_in_with_learner_driver):
    """[TC-121] 게시글 목록 조회.

    1. 클래스 사이드바에서 [게시판] 선택
    2. 게시글 목록을 화면에서 확인
    3. 제목 헤더가 있는 게시판 테이블 노출 확인
    """
    board = LearnerBoardPage(learner_logged_in_with_learner_driver)
    board.open_board()
    board_table = board.wait_for_board_table()

    assert board_table.is_displayed(), "게시판 목록 테이블이 표시되지 않았습니다."

def test_128_click_write_without_login(
    learner_logged_out_with_learner_driver,
):
    """[TC-128] 비로그인 상태에서 글쓰기 버튼 접근.

    1. 로그인하지 않은 상태로 게시판 URL 이동
    2. 게시판이 열리면 [글쓰기] 버튼 클릭
    3. 게시판 접근 단계에서 로그인 화면으로 이동하면 후속 클릭 생략
    """
    board = LearnerBoardPage(learner_logged_out_with_learner_driver)
    board.open_url(required_url("BOARD_URL"))
    board.open_write_from_board_if_available()
    login_url, email_input = wait_for_login_destination(
        learner_logged_out_with_learner_driver
    )

    assert "accounts" in login_url.lower() or "signin" in login_url.lower(), (
        f"글쓰기 접근 후 로그인 페이지로 이동하지 않았습니다: {login_url}"
    )
    assert email_input.get_attribute("name") == "loginId", (
        "일반 로그인 화면의 이메일 입력란을 확인하지 못했습니다."
    )

def test_129_create_post(learner_logged_in_with_learner_driver):
    """[TC-129] 게시글 필수 정보 입력 후 등록.

    1. 게시글 작성 화면으로 이동
    2. 고유한 제목과 본문 입력
    3. 등록 후 상세 화면에서 생성한 제목과 본문 확인
    """
    board = LearnerBoardPage(learner_logged_in_with_learner_driver)
    unique = datetime.now(UTC).strftime("%Y%m%d%H%M%S%f")
    content = "TC-129 게시글 등록 기능 테스트입니다."
    board.open_write_from_home()
    board.create_post(unique, content)
    created_title, created_content = board.wait_for_post_detail(
        unique,
        content,
    )

    assert created_title == unique, (
        f"등록한 게시글 상세 제목이 일치하지 않습니다: "
        f"expected={unique}, actual={created_title}"
    )
    assert created_content == content, (
        f"등록한 게시글 상세 본문이 일치하지 않습니다: "
        f"expected={content}, actual={created_content}"
    )
