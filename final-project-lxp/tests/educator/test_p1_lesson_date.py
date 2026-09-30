"""교육자 기존 수업 날짜 수정 및 보존 자동화 테스트 (TC-112).

교육자가 기존 수업의 수정 다이얼로그에서 수업 날짜를 수정한 뒤 저장하고,
재진입 후에도 수정된 날짜가 정상 유지되는지 검증하며 종료 시 생성 데이터를 삭제 원복한다.
"""

from datetime import datetime, timedelta
import logging
import os
import sys

import pytest
from selenium.common.exceptions import WebDriverException

from pages.educator.course_page import EducatorCoursePage
from pages.educator.lesson_page import EducatorLessonPage

logger = logging.getLogger(__name__)


def _required_url(variable_name: str) -> str:
    """QA 전용 URL 환경변수를 가져오고, 없으면 테스트를 건너뛴다."""
    url = os.getenv(variable_name, "").strip()
    if not url:
        pytest.skip(f"{variable_name} 환경 변수가 설정되지 않았습니다.")
    return url


def _qa_lesson_title(test_case: str) -> str:
    """고유 식별 가능한 QA 수업 제목을 생성한다."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"[QA 자동화][{test_case}][{timestamp}] 수업"


def _open_course_edit_page(driver) -> EducatorLessonPage:
    """QA 과목의 편집 모드를 열고 수업 Page Object를 반환한다."""
    course_page = EducatorCoursePage(driver)
    course_page.navigate_to_course_edit_page(
        _required_url("EDUCATOR_COURSE_EDIT_URL")
    )
    course_page.enter_course_edit_mode()
    return EducatorLessonPage(driver)


@pytest.mark.educator
def test_tc112_edit_lesson_schedule_date(educator_logged_in):
    """[TC-112] 기존 수업의 수업 날짜를 수정하고 저장 후 재진입 시에도 보존되는지 검증한다.

    1. QA 수업을 생성하고 수정 폼에서 14일 후 날짜 입력·저장
    2. 새로고침 후 재진입하여 날짜 유지 확인
    3. 생성한 수업 삭제 및 목록에서 제거 확인
    """
    title = _qa_lesson_title("TC112")
    description = f"{title} 날짜 수정 UI 자동화"
    target = datetime.now() + timedelta(days=14)
    target_date = target.strftime("%Y%m%d")
    expected_display = target.strftime("%Y.%m.%d")

    lesson_page = _open_course_edit_page(educator_logged_in)
    created = False
    try:
        # 1. QA 전용 수업 생성
        lesson_page.create_lesson(title, description)
        created = True

        # 2. 수업 수정 다이얼로그 열기
        lesson_page.open_lesson_edit_dialog()
        assert lesson_page.is_lesson_edit_dialog_displayed(), "수업 수정 다이얼로그 미표시"

        # 3. 수업 날짜 수정 입력
        lesson_page.enter_lesson_date(target_date)
        current_val = lesson_page.get_lesson_date_value()
        assert "".join(filter(str.isdigit, current_val)) == target_date, (
            f"날짜 입력값이 반영되지 않았습니다: {current_val}"
        )

        # 4. 수정사항 저장
        lesson_page.save_lesson_edit()

        # 5. 과목 화면 새로고침 및 수업 재진입 후 수정된 날짜 유지 확인
        educator_logged_in.refresh()
        lesson_page = _open_course_edit_page(educator_logged_in)
        lesson_page.open_lesson_by_title(title)
        lesson_page.open_lesson_edit_dialog()
        persisted_val = lesson_page.get_lesson_date_value()
        assert "".join(filter(str.isdigit, persisted_val)) == target_date, (
            f"재진입 후 수정된 수업 날짜가 유지되지 않았습니다: {persisted_val}"
        )

    finally:
        if created:
            test_failed = sys.exc_info()[0] is not None
            try:
                lesson_page.close_lesson_edit_dialog()
                lesson_page.delete_current_lesson()
                assert lesson_page.wait_until_lesson_removed(title), f"수업 삭제 실패: {title}"
            except (WebDriverException, AssertionError, LookupError):
                if not test_failed:
                    raise
                logger.exception("TC-112 본 테스트 실패 후 생성 수업 정리에도 실패: title=%s", title)
