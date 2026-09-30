"""교육자의 수업·자료 제작 P1 UI 자동화."""

import os
from datetime import datetime

import pytest

from pages.educator.course_page import EducatorCoursePage
from pages.educator.lesson_page import EducatorLessonPage
from pages.educator.material_page import EducatorMaterialPage


P1_PARENT_LESSON_TITLE = "[QA 자동화 전용][P1] 자료·퀴즈 검증용"
P1_CONTENT_LESSON_TITLE = "[QA 자동화 전용][P1] 콘텐츠·자료 검증용"


def _required_url(variable_name: str) -> str:
    """필수 QA URL을 반환하고, 설정되지 않았으면 테스트를 건너뛴다."""
    value = os.getenv(variable_name, "").strip()
    if not value:
        pytest.skip(f"{variable_name} 환경 변수가 설정되지 않았습니다.")
    return value


@pytest.mark.educator
def test_tc024_lesson_creation_requires_title(educator_logged_in):
    """[TC-024] 제목 없이 일반 수업을 저장할 수 없는지 검증한다.

    1. 과목 편집 모드에서 수업 생성 폼 열기
    2. 제목을 입력하지 않고 생성 폼 표시 확인
    3. 저장 버튼 비활성화 확인
    """
    lesson_page = _open_course_edit_page(educator_logged_in)
    lesson_page.open_lesson_create_dialog()

    assert lesson_page.is_lesson_create_dialog_displayed(), (
        "일반 수업 생성 다이얼로그 또는 제목 입력 필드가 표시되지 않았습니다."
    )
    assert lesson_page.is_create_submit_disabled(), (
        "수업 제목이 비어 있는데 저장 버튼이 활성화되어 있습니다."
    )


def _open_course_edit_page(driver) -> EducatorLessonPage:
    """QA 과목의 편집 모드를 열고 수업 Page Object를 반환한다."""
    course_page = EducatorCoursePage(driver)
    course_page.navigate_to_course_edit_page(
        _required_url("EDUCATOR_COURSE_EDIT_URL")
    )
    course_page.enter_course_edit_mode()
    return EducatorLessonPage(driver)


def _qa_lesson_title(test_case: str) -> str:
    """사람과 자동화 모두 식별할 수 있는 QA 수업 제목을 만든다."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"[QA 자동화][{test_case}][{timestamp}] 수업"


def _open_p1_content_lesson(driver) -> EducatorMaterialPage:
    """편집 모드를 유지한 채 P1 전용 콘텐츠 하위 수업을 연다."""
    lesson_page = _open_course_edit_page(driver)
    lesson_page.open_nested_lesson_by_titles(
        P1_PARENT_LESSON_TITLE,
        P1_CONTENT_LESSON_TITLE,
    )
    material_page = EducatorMaterialPage(driver)
    material_page.wait_for_visible(material_page.MATERIAL_ADD_BUTTON, timeout=15)
    return material_page


@pytest.mark.educator
def test_tc023_create_normal_lesson(educator_logged_in):
    """[TC-023] 교육자가 일반 수업을 만들고 목록에 반영되는지 검증한다.

    1. 과목 편집 모드에서 고유 제목의 일반 수업 생성
    2. 수업 목록 반영 확인
    3. 생성한 수업 삭제 및 목록에서 제거 확인
    """
    title = _qa_lesson_title("TC023")
    description = f"{title} 일반 수업 생성 UI 자동화"
    lesson_page = _open_course_edit_page(educator_logged_in)
    created = False
    try:
        lesson_page.create_lesson(title, description)
        created = True
        assert lesson_page.is_lesson_listed(title), (
            "저장한 일반 수업이 수업 목록에 표시되지 않았습니다."
        )
    finally:
        if created:
            lesson_page.delete_current_lesson()
            assert lesson_page.wait_until_lesson_removed(title), (
                f"정리 대상 수업이 목록에 남아 있습니다: {title}"
            )


@pytest.mark.educator
def test_tc030_new_lesson_defaults_to_private(educator_logged_in):
    """[TC-030] 새 일반 수업의 기본 공개 상태가 비공개인지 검증한다.

    1. 과목 편집 모드에서 일반 수업 생성
    2. 새 수업의 상태가 비공개인지 확인
    3. 생성한 수업 삭제 및 목록에서 제거 확인
    """
    title = _qa_lesson_title("TC030")
    description = f"{title} 기본 공개 상태 UI 자동화"
    lesson_page = _open_course_edit_page(educator_logged_in)
    created = False
    try:
        lesson_page.create_lesson(title, description)
        created = True
        assert lesson_page.get_lesson_status(title) == "비공개", (
            "새로 만든 일반 수업의 목록 상태가 비공개가 아닙니다."
        )
    finally:
        if created:
            lesson_page.delete_current_lesson()
            assert lesson_page.wait_until_lesson_removed(title), (
                f"정리 대상 수업이 목록에 남아 있습니다: {title}"
            )


@pytest.mark.educator
def test_tc055_text_material_requires_title(educator_logged_in):
    """[TC-055] 제목이 없으면 텍스트 자료를 저장할 수 없는지 검증한다.

    1. P1 전용 수업에서 텍스트 자료 입력 폼 열기
    2. 제목·본문을 입력하지 않고 폼 표시 확인
    3. 저장 버튼 비활성화 확인
    """
    material_page = _open_p1_content_lesson(educator_logged_in)
    material_page.open_text_editor_form()

    assert material_page.is_text_editor_form_displayed(), (
        "텍스트 자료의 제목·본문 입력 폼이 표시되지 않았습니다."
    )
    assert material_page.is_text_editor_save_disabled(), (
        "텍스트 자료 제목이 비어 있는데 저장 버튼이 활성화되어 있습니다."
    )


def _qa_material_title(test_case: str, type_label: str = "텍스트 자료") -> str:
    """사람과 자동화 모두 식별할 수 있는 QA 자료 제목을 만든다."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"[QA 자동화][{test_case}][{timestamp}] {type_label}"


@pytest.mark.educator
def test_tc054_create_text_material(educator_logged_in):
    """[TC-054] 교육자가 텍스트 자료를 생성하고 목록에 정상 표시되는지 검증한다.

    1. P1 전용 수업에서 제목과 본문을 입력해 텍스트 자료 생성
    2. 자료 목록 반영 확인
    3. 생성한 자료 삭제 및 목록에서 제거 확인
    """
    title = _qa_material_title("TC054", "텍스트 자료")
    content = f"{title} 본문 내용 UI 자동화"
    material_page = _open_p1_content_lesson(educator_logged_in)
    created = False
    try:
        material_page.create_text_material(title, content)
        created = True
        assert material_page.is_material_listed(title), (
            "생성한 텍스트 자료가 학습 자료 목록에 표시되지 않았습니다."
        )
    finally:
        if created:
            material_page.delete_material_by_title(title)
            assert material_page.wait_until_material_removed(title), (
                f"정리 대상 텍스트 자료가 목록에 남아 있습니다: {title}"
            )


@pytest.mark.educator
def test_tc078_material_data_persists_after_reload(educator_logged_in):
    """[TC-078] 생성된 자료가 새로고침 및 재진입 후에도 보존되는지 검증한다.

    1. P1 전용 수업에 텍스트 자료 생성 및 목록 반영 확인
    2. 새로고침 후 수업에 재진입하여 자료 유지 확인
    3. 생성한 자료 삭제 및 목록에서 제거 확인
    """
    title = _qa_material_title("TC078", "텍스트 자료")
    content = f"{title} 데이터 보존 UI 자동화"
    material_page = _open_p1_content_lesson(educator_logged_in)
    created = False
    try:
        material_page.create_text_material(title, content)
        created = True
        assert material_page.is_material_listed(title), (
            "생성한 텍스트 자료가 학습 자료 목록에 표시되지 않았습니다."
        )

        # 현재 자료 상세 URL은 새로고침하면 과목 수업 목록으로 돌아간다.
        # 따라서 실제 교육자 진입 경로를 다시 열어 저장 자료의 보존을 확인한다.
        educator_logged_in.refresh()
        material_page = _open_p1_content_lesson(educator_logged_in)
        material_page.wait_until_material_listed(title, timeout=15)
        assert material_page.is_material_listed(title), (
            "브라우저 새로고침 및 수업 재진입 후 생성한 텍스트 자료가 목록에서 사라졌습니다."
        )
    finally:
        if created:
            # 새로고침 직후 과목 목록으로 돌아간 실패 경로에서도 QA 자료를 원복한다.
            material_page = _open_p1_content_lesson(educator_logged_in)
            material_page.delete_material_by_title(title)
            assert material_page.wait_until_material_removed(title), (
                f"정리 대상 텍스트 자료가 목록에 남아 있습니다: {title}"
            )


@pytest.mark.educator
def test_tc061_quiz_material_requires_title(educator_logged_in):
    """[TC-061] 필수 입력값인 퀴즈 제목이 없을 때 저장이 차단되는지 검증한다.

    1. P1 전용 수업에서 퀴즈 생성 폼 열기
    2. 입력값 없이 폼 표시와 저장 버튼 비활성화 확인
    """
    material_page = _open_p1_content_lesson(educator_logged_in)
    material_page.open_quiz_editor_form()
    assert material_page.is_quiz_editor_form_displayed(), (
        "퀴즈 생성 폼이 화면에 표시되지 않았습니다."
    )
    assert material_page.is_quiz_editor_save_disabled(), (
        "퀴즈 자료 제목이 비어 있는데 저장 버튼이 활성화되어 있습니다."
    )


@pytest.mark.educator
def test_tc060_create_quiz_material(educator_logged_in):
    """[TC-060] 교육자가 퀴즈 자료를 생성하고 목록에 정상 표시되는지 검증한다.

    1. P1 전용 수업에서 고유 제목의 퀴즈 자료 생성
    2. 자료 목록 반영 확인
    3. 생성한 자료 삭제 및 목록에서 제거 확인
    """
    title = _qa_material_title("TC060", "퀴즈 자료")
    material_page = _open_p1_content_lesson(educator_logged_in)
    created = False
    try:
        material_page.create_quiz_material(title)
        created = True
        assert material_page.is_material_listed(title), (
            "생성한 퀴즈 자료가 학습 자료 목록에 표시되지 않았습니다."
        )
    finally:
        if created:
            material_page.delete_material_by_title(title)
            assert material_page.wait_until_material_removed(title), (
                f"정리 대상 퀴즈 자료가 목록에 남아 있습니다: {title}"
            )


@pytest.mark.educator
def test_tc058_video_material_invalid_url_rejected(educator_logged_in):
    """[TC-058] 유효하지 않은 형식의 영상 링크 입력 시 저장이 차단되는지 검증한다.

    1. P1 전용 수업에서 동영상 생성 폼 열기
    2. 공란 상태의 저장 버튼 비활성화 확인
    3. 제목과 잘못된 URL 입력 후 저장 버튼 비활성화 확인
    """
    material_page = _open_p1_content_lesson(educator_logged_in)
    material_page.open_video_editor_form()
    assert material_page.is_video_editor_form_displayed(), (
        "동영상 생성 폼이 화면에 표시되지 않았습니다."
    )
    # 1. 공란 상태 저장 비활성 검증
    assert material_page.is_video_editor_save_disabled(), (
        "입력값이 비어 있는데 저장 버튼이 활성화되어 있습니다."
    )
    # 2. 비정상 URL 형식 입력 시 저장 차단 검증
    material_page.enter_video_material_title("동영상 유효성 검증용 제목")
    material_page.enter_video_material_url("영상입니다")
    assert material_page.is_video_editor_save_disabled(), (
        "잘못된 URL 형식 입력 시 저장 버튼이 비활성화되어 있어야 합니다."
    )


@pytest.mark.educator
def test_tc057_create_video_material(educator_logged_in):
    """[TC-057] 교육자가 유효한 링크의 동영상 자료를 생성하고 목록에 표시되는지 검증한다.

    1. P1 전용 수업에서 제목과 유효한 영상 링크로 자료 생성
    2. 자료 목록 반영 확인
    3. 생성한 자료 삭제 및 목록에서 제거 확인
    """
    title = _qa_material_title("TC057", "동영상 자료")
    valid_video_url = "https://www.youtube.com/watch?v=umDExCfl05w"
    material_page = _open_p1_content_lesson(educator_logged_in)
    created = False
    try:
        material_page.create_video_material(title, valid_video_url)
        created = True
        assert material_page.is_material_listed(title), (
            "생성한 동영상 자료가 학습 자료 목록에 표시되지 않았습니다."
        )
    finally:
        if created:
            material_page.delete_material_by_title(title)
            assert material_page.wait_until_material_removed(title), (
                f"정리 대상 동영상 자료가 목록에 남아 있습니다: {title}"
            )
