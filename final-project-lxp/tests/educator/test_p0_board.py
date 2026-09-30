from datetime import datetime
import logging
import os
import pytest
from selenium.common.exceptions import TimeoutException

from pages.educator.board_page import EducatorBoardPage
from pages.educator.classroom_home_page import get_classroom_url

logger = logging.getLogger(__name__)


def _get_board_url() -> str:
    """QA6_2 클래스룸 게시판 URL을 반환한다."""
    custom_url = os.getenv("BOARD_URL", "").strip()
    if custom_url:
        return custom_url
    return f"{get_classroom_url()}/articles"


def _open_qa6_2_board(driver) -> EducatorBoardPage:
    """공유 교육자 세션을 QA6_2 클래스룸 게시판으로 초기화한다."""
    board_url = _get_board_url()

    def returned_to_classroom_home() -> bool:
        return (
            "/classrooms/" in driver.current_url
            and "/articles" not in driver.current_url
        )

    for attempt in range(2):
        if attempt > 0:
            driver.get(board_url)
        elif (
            "/articles" not in driver.current_url
            or "/articles/" in driver.current_url
            or driver.current_url.endswith("/new")
        ):
            driver.get(board_url)
        else:
            driver.refresh()

        if attempt == 0 and returned_to_classroom_home():
            logger.warning(
                "게시판 이동 직후 클래스 홈으로 돌아와 즉시 재진입합니다: "
                "current_url=%s",
                driver.current_url,
            )
            continue

        board_page = EducatorBoardPage(driver)
        try:
            board_page.wait_for_board_loaded(
                failure_log_level=(
                    logging.WARNING if attempt == 0 else logging.ERROR
                )
            )
            return board_page
        except TimeoutException:
            if attempt == 0 and returned_to_classroom_home():
                logger.warning(
                    "게시판 이동 중 클래스 홈으로 돌아와 한 번 재진입합니다: "
                    "current_url=%s",
                    driver.current_url,
                )
                continue
            if attempt == 0:
                logger.error(
                    "게시판 첫 진입 실패가 재시도 조건에 해당하지 않습니다: "
                    "current_url=%s",
                    driver.current_url,
                )
            raise

    raise RuntimeError("게시판 진입 재시도 흐름이 비정상적으로 종료되었습니다.")


def _delete_generated_post(driver, title: str) -> None:
    """생성 TC가 남긴 QA 전용 게시글을 검증 직후 제거한다."""
    if not ("[QA" in title or "[기관교육자" in title):
        raise ValueError(f"QA 전용 표식이 없는 게시글은 안전을 위해 삭제하지 않습니다: {title}")

    board_page = EducatorBoardPage(driver)
    # 1. 이미 상세 화면에 위치해 있으면 불필요하게 목록으로 나가지 않고 바로 삭제
    if board_page.find_optional_visible(board_page.ARTICLE_MENU_BUTTON, timeout=2):
        logger.info("현재 상세 화면에서 직접 게시글 삭제 진행: %s", title)
        board_page.delete_current_post()
    else:
        logger.info("게시판 목록으로 이동하여 대상 게시글 검색 후 삭제: %s", title)
        board_page = _open_qa6_2_board(driver)
        board_page.select_post_by_title(title)
        board_page.delete_current_post()

    # 2. 삭제 후 목록으로 돌아와 완전 삭제 여부 검증
    board_page = _open_qa6_2_board(driver)
    assert not board_page.is_post_title_visible(title), (
        f"정리 대상 게시글이 삭제 후에도 목록에 남아 있습니다: {title}"
    )


@pytest.mark.educator
def test_tc131_board_list_and_detail_view(educator_logged_in):
    """[TC-131] 게시글 목록 및 상세 조회 검증.

    1. 교육자 계정으로 로그인 후 게시판 메뉴로 이동
    2. 게시글 목록이 정상 로드되는지 확인
    3. 게시글 선택 시 상세 화면(제목, 본문)이 정상 표시되는지 확인
    """
    board_page = _open_qa6_2_board(educator_logged_in)
    post_count = board_page.get_post_count()

    assert post_count > 0, "TC-131의 사전조건인 조회 가능한 게시글이 없습니다."

    list_title = board_page.get_first_post_title()
    board_page.select_first_post()
    detail_title = board_page.get_detail_title()
    detail_content = board_page.get_detail_content()
    assert list_title in detail_title, "목록에서 선택한 게시글의 상세 제목이 표시되지 않았습니다."
    assert detail_content, "게시글 상세 화면에서 본문이 조회되지 않았습니다."


@pytest.mark.educator
def test_tc132_create_general_post(educator_logged_in):
    """[TC-132] 일반 게시글 작성 후 목록·상세 반영 확인.

    1. 게시판에서 고유 제목과 본문으로 게시글 생성
    2. 상세 화면에 제목과 본문 반영 확인
    3. 생성한 게시글 삭제 및 정리 결과 확인
    """
    board_page = _open_qa6_2_board(educator_logged_in)
    timestamp = datetime.now().strftime("%m%d_%H%M%S")
    test_title = f"[QA 자동화] 일반 게시글 테스트_{timestamp}"
    test_content = f"자동화 검증 본문 내용입니다. 타임스탬프: {timestamp}"

    created = False
    try:
        board_page.write_post(test_title, test_content)
        created = True
        detail_title = board_page.wait_for_detail_title(test_title)
        detail_content = board_page.wait_for_detail_content(test_content)
        assert test_title in detail_title, "작성한 일반 게시글 제목이 상세 화면에 반영되지 않았습니다."
        assert test_content in detail_content, "작성한 일반 게시글 본문이 상세 화면에 반영되지 않았습니다."
    finally:
        if created:
            _delete_generated_post(educator_logged_in, test_title)


@pytest.mark.educator
def test_tc134_edit_own_post(educator_logged_in):
    """[TC-134] 본인 게시글 수정 및 저장값 반영 확인.

    1. 수정할 QA 게시글을 새로 생성
    2. 제목·본문 수정 후 변경값 반영과 이전 값 부재 확인
    3. 생성한 게시글 삭제 및 정리 결과 확인
    """
    board_page = _open_qa6_2_board(educator_logged_in)
    timestamp = datetime.now().strftime("%m%d_%H%M%S")
    original_title = f"[QA 자동화] 수정 대상 게시글_{timestamp}"
    original_content = f"수정 전 자동화 검증 본문입니다. 타임스탬프: {timestamp}"
    updated_title = f"[QA 수정] 제목 수정_{timestamp}"
    updated_content = f"수정 후 자동화 검증 본문입니다. 타임스탬프: {timestamp}"
    cleanup_title = original_title

    created = False
    try:
        board_page.write_post(original_title, original_content)
        created = True
        board_page.wait_for_detail_title(original_title)
        board_page.wait_for_detail_content(original_content)
        board_page.click_edit_button()
        board_page.enter_title(updated_title)
        board_page.enter_content(updated_content)
        board_page.click_submit_button()
        cleanup_title = updated_title

        detail_title = board_page.wait_for_detail_title(updated_title)
        detail_content = board_page.wait_for_detail_content(updated_content)
        assert updated_title in detail_title, "수정한 게시글 제목이 상세 화면에 반영되지 않았습니다."
        assert updated_content in detail_content, "수정한 게시글 본문이 상세 화면에 반영되지 않았습니다."
        assert original_title not in detail_title, "수정 전 게시글 제목이 남아 있습니다."
        assert original_content not in detail_content, "수정 전 게시글 본문이 남아 있습니다."
    finally:
        if created:
            _delete_generated_post(educator_logged_in, cleanup_title)


@pytest.mark.educator
def test_tc146_create_institution_educator_only_post(educator_logged_in):
    """[TC-146] 기관교육자 전용 게시글 작성 후 상세 반영을 확인한다.

    1. 글쓰기 화면 진입 및 제목·본문 입력
    2. [기관교육자 전용] 옵션 활성화 및 체크 상태 확인
    3. 게시글 등록 후 상세 화면 반영 확인
    4. 생성한 게시글 삭제 및 정리 결과 확인
    """
    board_page = _open_qa6_2_board(educator_logged_in)
    timestamp = datetime.now().strftime("%m%d_%H%M%S")
    test_title = f"[기관교육자 전용 QA] 게시글_{timestamp}"
    test_content = f"기관교육자 전용 게시글 자동화 검증 본문입니다. 타임스탬프: {timestamp}"

    created = False
    try:
        board_page.click_write_button()
        board_page.enter_title(test_title)
        board_page.enter_content(test_content)
        board_page.enable_institution_educator_only()
        assert board_page.is_institution_educator_only_selected(), (
            "기관교육자 전용 공개 설정이 선택되지 않았습니다."
        )
        board_page.click_submit_button()
        created = True

        detail_title = board_page.wait_for_detail_title(test_title)
        detail_content = board_page.wait_for_detail_content(test_content)
        assert test_title in detail_title, "등록한 게시글 제목이 상세 화면에 반영되지 않았습니다."
        assert test_content in detail_content, "등록한 게시글 본문이 상세 화면에 반영되지 않았습니다."
    finally:
        if created:
            _delete_generated_post(educator_logged_in, test_title)
