"""교육자 수업자료 수정 및 원복 자동화 테스트 (TC-117)."""

from datetime import datetime
import os
import pytest

from pages.educator.course_page import EducatorCoursePage
from pages.educator.lesson_page import EducatorLessonPage
from pages.educator.material_page import EducatorMaterialPage

P1_PARENT_LESSON_TITLE = "[QA 자동화 전용][P1] 자료·퀴즈 검증용"
P1_CONTENT_LESSON_TITLE = "[QA 자동화 전용][P1] 콘텐츠·자료 검증용"


def _required_url(variable_name: str) -> str:
    """QA 전용 URL 환경변수를 가져오고, 없으면 테스트를 건너뛴다."""
    url = os.getenv(variable_name, "").strip()
    if not url:
        pytest.skip(f"{variable_name} 환경 변수가 설정되지 않았습니다.")
    return url


def _open_course_edit_page(driver) -> EducatorLessonPage:
    """QA 과목의 편집 모드를 열고 수업 Page Object를 반환한다."""
    course_page = EducatorCoursePage(driver)
    course_page.navigate_to_course_edit_page(
        _required_url("EDUCATOR_COURSE_EDIT_URL")
    )
    course_page.enter_course_edit_mode()
    return EducatorLessonPage(driver)


def _open_p1_content_lesson(driver) -> EducatorMaterialPage:
    """편집 모드를 유지한 채 P1 전용 콘텐츠 하위 수업을 연다."""
    lesson_page = _open_course_edit_page(driver)
    lesson_page.open_nested_lesson_by_titles(
        P1_PARENT_LESSON_TITLE, P1_CONTENT_LESSON_TITLE
    )
    material_page = EducatorMaterialPage(driver)
    material_page.wait_for_visible(material_page.MATERIAL_ADD_BUTTON, timeout=15)
    return material_page


@pytest.mark.educator
def test_tc117_edit_text_material(educator_logged_in):
    """[TC-117] 기존 텍스트 자료의 제목·본문 수정값이 재진입 뒤에도 유지되는지 검증한다.

    1. QA 텍스트 자료를 생성한 뒤 제목과 본문 수정
    2. 목록·편집 폼 및 새로고침 후 재진입 화면에서 수정값 확인
    3. 생성한 자료 삭제 및 목록에서 제거 확인
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_title = f"[QA 자동화][TC117][{timestamp}] 원본 텍스트 자료"
    original_content = f"{original_title} 원본 본문 UI 자동화"
    edited_title = f"[QA 자동화][TC117][{timestamp}] 수정된 텍스트 자료"
    edited_content = f"{edited_title} 수정 내용 UI 자동화"

    material_page = _open_p1_content_lesson(educator_logged_in)
    created = False
    try:
        # 1. QA 전용 원본 자료를 만든 뒤 기존 자료처럼 수정한다.
        material_page.create_text_material(original_title, original_content)
        created = True
        material_page.edit_text_material(original_title, edited_title, edited_content)

        # 2. 목록 반영 및 편집 폼의 실제 본문값 확인
        assert material_page.is_material_listed(edited_title), (
            f"수정된 제목이 수업 자료 목록에 표시되지 않았습니다: {edited_title}"
        )
        assert edited_content in material_page.get_text_material_content(edited_title), (
            "수정한 수업자료 본문이 편집 폼에 반영되지 않았습니다."
        )

        # 3. 화면 새로고침 및 실제 교육자 경로 재진입 후 제목·본문 보존 확인
        educator_logged_in.refresh()
        material_page = _open_p1_content_lesson(educator_logged_in)
        material_page.wait_until_material_listed(edited_title, timeout=15)
        assert material_page.is_material_listed(edited_title), (
            f"재진입 후 수정된 수업자료 제목이 유지되지 않았습니다: {edited_title}"
        )
        assert edited_content in material_page.get_text_material_content(edited_title), (
            "재진입 후 수정된 수업자료 본문이 유지되지 않았습니다."
        )

    finally:
        # 실행 중간 실패를 포함해 이 TC가 만든 고유 QA 자료만 삭제한다.
        material_page = _open_p1_content_lesson(educator_logged_in)
        cleanup_title = (
            edited_title
            if material_page.is_material_listed(edited_title)
            else original_title
        )
        if created or material_page.is_material_listed(cleanup_title):
            if material_page.is_material_listed(cleanup_title):
                material_page.delete_material_by_title(cleanup_title)
                assert material_page.wait_until_material_removed(cleanup_title), (
                    f"정리 대상 수업자료가 목록에 남아 있습니다: {cleanup_title}"
                )
