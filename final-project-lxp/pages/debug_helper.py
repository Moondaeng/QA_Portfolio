import time


def pause_for_debugging(seconds: float = 0) -> None:
    """디버깅 중 브라우저 동작을 눈으로 확인하기 위해 대기한다.

    Args:
        seconds: 대기 시간(초). 0이면 대기하지 않는다.

    Raises:
        ValueError: seconds가 음수인 경우.
    """
    if seconds < 0:
        raise ValueError("seconds는 0 이상이어야 합니다.")

    if seconds == 0:
        return

    time.sleep(seconds)