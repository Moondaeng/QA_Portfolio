"""교육자 수업 일정 생성, 수정 및 캘린더 반영 자동화 테스트 (TC-130).

교육자가 수업 일정을 생성하고 수정한 뒤 캘린더/목록에 정상 반영되는지 검증하며,
테스트 종료 시 생성된 일정을 삭제하여 환경을 깨끗하게 원복한다.
"""

from datetime import datetime
import os
import pytest

from pages.educator.classroom_home_page import get_classroom_url
from pages.educator.schedule_page import EducatorSchedulePage


def _default_schedules_url() -> str:
    """기본 클래스룸의 수업 일정 URL을 반환한다."""
    return f"{get_classroom_url()}/schedules"


def _required_url(variable_name: str) -> str:
    """QA 전용 URL 환경변수를 가져오거나 기본 URL을 반환한다."""
    return os.getenv(variable_name, "").strip() or _default_schedules_url()


def _qa_schedule_title(test_case: str) -> str:
    """고유 식별 가능한 QA 일정 제목을 생성한다."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"[QA 자동화][{test_case}][{timestamp}] 수업 일정"


@pytest.mark.educator
def test_tc130_create_and_edit_schedule(educator_logged_in):
    """[TC-130] 교육자가 수업 일정을 생성하고 수정한 뒤 캘린더 반영을 검증한다.

    1. 일정 화면에서 고유 제목의 일정 생성 및 반영 확인
    2. 일정 제목 수정 및 반영 확인
    3. 생성한 일정 삭제 및 제거 확인
    """
    schedule_page = EducatorSchedulePage(educator_logged_in)
    schedule_url = _required_url("EDUCATOR_SCHEDULE_URL")
    schedule_page.navigate_to_schedule_page(schedule_url)

    title = _qa_schedule_title("TC130")
    edited_title = f"{title}_수정완료"
    created = False

    try:
        # 1. 새 수업 일정 생성
        # 저장 클릭 뒤 캘린더 반영 대기에서 실패하더라도, 이미 생성됐을 가능성이
        # 있으므로 finally에서 QA 표식 제목을 확인·원복한다.
        created = True
        schedule_page.create_schedule(title)
        assert schedule_page.is_schedule_listed(title), (
            f"생성한 수업 일정이 캘린더에 표시되지 않았습니다: {title}"
        )

        # 2. 일정 제목 수정
        schedule_page.edit_schedule_title(title, edited_title)
        assert schedule_page.is_schedule_listed(edited_title), (
            f"수정된 수업 일정이 캘린더에 표시되지 않았습니다: {edited_title}"
        )

    finally:
        if created:
            schedule_page.close_schedule_editor_if_present()
            target = (
                edited_title
                if schedule_page.is_schedule_listed(edited_title)
                else title
            )
            if schedule_page.is_schedule_listed(target):
                schedule_page.delete_schedule(target)
                assert schedule_page.wait_until_schedule_removed(target), (
                    f"일정 삭제 후에도 항목이 남아 있습니다: {target}"
                )
