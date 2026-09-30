"""교육자 수업 공개/비공개 전환 기능 자동화 테스트 (TC-085, TC-088).

영구 QA 전용 수업을 재사용하여 공개/비공개 상태 전환 및 학습자 화면의 노출/차단 여부를
교차 검증하며, 종료 시 원래의 상태로 안전하게 복구한다.
"""

import os
import pytest

from pages.educator.course_page import EducatorCoursePage
from pages.educator.lesson_page import EducatorLessonPage
from pages.learner.content_page import LearnerContentPage
from tests.conftest import _learner_login_flow


DEFAULT_VISIBILITY_LESSON_TITLE = "[QA 자동화 전용][P1] 자료·퀴즈 검증용"


def _required_url(variable_name: str) -> str:
    """QA 전용 URL 환경변수를 가져오고, 없으면 테스트를 건너뛴다."""
    url = os.getenv(variable_name, "").strip()
    if not url:
        pytest.skip(f"{variable_name} 환경 변수가 설정되지 않았습니다.")
    return url


def _visibility_lesson_title() -> str:
    """영구적으로 재사용하는 QA 전용 공개·비공개 전환 수업 제목을 반환한다."""
    return os.getenv(
        "P1_VISIBILITY_LESSON_TITLE", DEFAULT_VISIBILITY_LESSON_TITLE
    ).strip()


def _open_course_edit_page(driver) -> EducatorLessonPage:
    """QA 과목의 편집 모드를 열고 수업 Page Object를 반환한다."""
    course_page = EducatorCoursePage(driver)
    course_page.navigate_to_course_edit_page(
        _required_url("EDUCATOR_COURSE_EDIT_URL")
    )
    course_page.enter_course_edit_mode()
    return EducatorLessonPage(driver)


def _open_learner_course_page(driver) -> LearnerContentPage:
    """학습자 세션으로 동일 QA 과목 화면을 열어 실제 수업 노출을 확인한다."""
    learner_page = LearnerContentPage(driver)
    learner_page.navigate(_required_url("LEARNER_COURSE_URL"))
    return learner_page


def _verify_educator_status_after_refresh(
    driver, title: str, expected_status: str
) -> EducatorLessonPage:
    """새로고침 후에도 수업 상태 배지가 expected_status를 유지하는지(서버 영구 저장) 검증한다."""
    driver.refresh()
    course_page = EducatorCoursePage(driver)
    course_page.enter_course_edit_mode()
    lesson_page = EducatorLessonPage(driver)
    if not lesson_page.find_optional_visible(lesson_page.LESSON_HEADER_STATUS_BADGE, timeout=3):
        lesson_page.open_lesson_by_title(title)
    current_status = lesson_page.get_current_lesson_visibility_badge_text()
    assert current_status == expected_status, (
        f"서버 저장 실패(새로고침 후 배지 롤백): 기대 상태={expected_status}, 실제 상태={current_status}"
    )
    return lesson_page


@pytest.mark.educator
def test_tc085_tc088_lesson_visibility_lifecycle(
    educator_logged_in,
    learner_driver,
    base_url,
    learner_account,
):
    """[TC-085, TC-088] 전용 수업의 공개·비공개 전환과 학습자 노출/차단을 검증한다.

    1. 전용 수업의 초기 공개 상태 확인 및 학습자 로그인
    2. 공개·비공개 전환마다 새로고침 후 저장 상태와 학습자 노출 확인
    3. 종료 시 초기 공개 상태로 복원
    """
    title = _visibility_lesson_title()
    lesson_page = _open_course_edit_page(educator_logged_in)
    initial_status = None
    try:
        # 1. 미리 준비된 영구 QA 전용 수업을 연다.
        assert lesson_page.is_lesson_listed(title), (
            f"전용 테스트 수업을 찾지 못했습니다: {title}."
        )
        lesson_page.open_lesson_by_title(title)

        # 2. 기준 데이터의 초기 상태 확인
        initial_status = lesson_page.get_current_lesson_visibility_badge_text()
        assert initial_status in ("공개", "비공개"), (
            f"수업 상태 배지가 올바르지 않습니다: {initial_status}"
        )

        # 3. 학습자 로그인 및 초기 화면 진입
        _learner_login_flow(learner_driver, base_url, learner_account)
        learner_page = _open_learner_course_page(learner_driver)

        if initial_status == "공개":
            # 4. [TC-088] 공개 ➡️ 비공개 전환 검증
            status_after_toggle = lesson_page.toggle_current_lesson_visibility()
            assert status_after_toggle == "비공개", (
                f"비공개 전환 실패: {status_after_toggle}"
            )
            # 1단계: 교육자 새로고침 후 서버 영구 저장 여부 확인
            lesson_page = _verify_educator_status_after_refresh(
                educator_logged_in, title, "비공개"
            )
            # 2단계: 학습자 노출 차단 검증
            learner_page = _open_learner_course_page(learner_driver)
            assert learner_page.wait_until_lesson_visibility(title, False, timeout=10), (
                "비공개 전환한 수업이 학습자 화면에 여전히 노출됩니다."
            )

            # 5. [TC-085] 비공개 ➡️ 공개 전환 검증
            restored_status = lesson_page.toggle_current_lesson_visibility()
            assert restored_status == "공개", (
                f"공개 전환 실패: {restored_status}"
            )
            # 1단계: 교육자 새로고침 후 서버 영구 저장 여부 확인
            lesson_page = _verify_educator_status_after_refresh(
                educator_logged_in, title, "공개"
            )
            # 2단계: 학습자 노출 검증
            learner_page = _open_learner_course_page(learner_driver)
            assert learner_page.wait_until_lesson_visibility(title, True, timeout=10), (
                "공개 전환한 수업이 학습자 화면에 노출되지 않았습니다."
            )
        else:
            # 4. [TC-085] 비공개 ➡️ 공개 전환 검증
            status_after_toggle = lesson_page.toggle_current_lesson_visibility()
            assert status_after_toggle == "공개", (
                f"공개 전환 실패: {status_after_toggle}"
            )
            # 1단계: 교육자 새로고침 후 서버 영구 저장 여부 확인
            lesson_page = _verify_educator_status_after_refresh(
                educator_logged_in, title, "공개"
            )
            # 2단계: 학습자 노출 검증
            learner_page = _open_learner_course_page(learner_driver)
            assert learner_page.wait_until_lesson_visibility(title, True, timeout=10), (
                "공개 전환한 수업이 학습자 화면에 노출되지 않았습니다."
            )

            # 5. [TC-088] 공개 ➡️ 비공개 전환 검증
            restored_status = lesson_page.toggle_current_lesson_visibility()
            assert restored_status == "비공개", (
                f"비공개 전환 실패: {restored_status}"
            )
            # 1단계: 교육자 새로고침 후 서버 영구 저장 여부 확인
            lesson_page = _verify_educator_status_after_refresh(
                educator_logged_in, title, "비공개"
            )
            # 2단계: 학습자 노출 차단 검증
            learner_page = _open_learner_course_page(learner_driver)
            assert learner_page.wait_until_lesson_visibility(title, False, timeout=10), (
                "비공개 전환한 수업이 학습자 화면에 여전히 노출됩니다."
            )

    finally:
        # 원래 상태로 반드시 원복
        if initial_status:
            current_status = lesson_page.get_current_lesson_visibility_badge_text()
            if current_status != initial_status:
                lesson_page.toggle_current_lesson_visibility()
