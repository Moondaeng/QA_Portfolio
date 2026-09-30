from dataclasses import dataclass


@dataclass(frozen=True)
class CourseSelectionData:
    """과목 및 수업 목록에서 선택할 인덱스 데이터.

    Attributes:
        course_index: 과목 목록에서 선택할 0부터 시작하는 인덱스.
        lesson_index: 수업 목록에서 선택할 0부터 시작하는 인덱스.
    """

    course_index: int
    lesson_index: int = 0


COURSE_DETAIL_SELECTION = CourseSelectionData(course_index=0)
LEARNING_START_SELECTION = CourseSelectionData(
    course_index=0,
    lesson_index=0,
)
