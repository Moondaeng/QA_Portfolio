from datetime import datetime, timedelta
import logging
import os
from pathlib import Path
import re
import time
from uuid import uuid4

from dotenv import load_dotenv
import pytest
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait


logger = logging.getLogger(__name__)
traceback_log_path: Path | None = None
pytest_result_log_path: Path | None = None
test_started_at: dict[str, float] = {}
test_outcomes: dict[str, str] = {}
session_started_at: float | None = None
parallel_worker = False

# 프로젝트 루트의 .env 파일에서 테스트 환경값을 불러온다.
load_dotenv()


@pytest.hookimpl(trylast=True)
def pytest_configure(config: pytest.Config) -> None:
    """로그 폴더와 실행 파일 경로를 설정한다.

    1. 일반 로그·traceback·결과 폴더 준비
    2. 병렬 실행은 프로세스 이름·PID·고유값으로 파일명 분리
    3. pytest 일반 로그의 저장 경로 지정
    """
    log_directory = Path("logs")
    runtime_log_directory = log_directory / "runtime"
    traceback_log_directory = log_directory / "traceback"
    pytest_log_directory = log_directory / "pytest"
    for directory in (
        runtime_log_directory,
        traceback_log_directory,
        pytest_log_directory,
    ):
        directory.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    global parallel_worker
    parallel_worker = hasattr(config, "workerinput")
    if parallel_worker or getattr(config.option, "numprocesses", 0):
        process_name = config.workerinput["workerid"] if parallel_worker else "controller"
        timestamp += f"_{process_name}_{os.getpid()}_{uuid4().hex[:8]}"

    global traceback_log_path, pytest_result_log_path
    traceback_log_path = (
        traceback_log_directory / f"traceback_{timestamp}.log"
    )
    pytest_result_log_path = pytest_log_directory / f"result_{timestamp}.log"

    logging_plugin = config.pluginmanager.get_plugin("logging-plugin")
    if logging_plugin is None:
        return

    logging_plugin.set_log_path(
        str(runtime_log_directory / f"test_{timestamp}.log")
    )


def pytest_sessionstart(session: pytest.Session) -> None:
    """전체 실행 시간 측정을 시작한다.

    1. 세션 시작 시각을 저장하여 종료 시 경과 시간 계산에 사용
    """
    global session_started_at
    session_started_at = time.monotonic()


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(
    session: pytest.Session,
    exitstatus: pytest.ExitCode,
) -> None:
    """전체 테스트 결과 요약을 기록한다.

    1. 병렬 worker는 기록 생략
    2. 결과별 개수와 전체 경과 시간·종료 코드 집계
    3. controller 또는 일반 실행 프로세스에서 결과 파일 저장
    """
    if parallel_worker:
        return
    elapsed = (
        time.monotonic() - session_started_at
        if session_started_at is not None
        else 0.0
    )
    terminal_reporter = session.config.pluginmanager.get_plugin(
        "terminalreporter"
    )
    stats = terminal_reporter.stats if terminal_reporter is not None else {}

    result_categories = (
        "passed",
        "failed",
        "skipped",
        "xfailed",
        "xpassed",
        "error",
    )
    result_counts = {
        category: len(stats.get(category, []))
        for category in result_categories
    }
    deselected = len(stats.get("deselected", []))
    selected = session.testscollected
    collected = selected + deselected

    summary = (
        f"테스트 세션 종료: collected={collected}, selected={selected}, "
        f"passed={result_counts['passed']}, failed={result_counts['failed']}, "
        f"skipped={result_counts['skipped']}, "
        f"xfailed={result_counts['xfailed']}, "
        f"xpassed={result_counts['xpassed']}, errors={result_counts['error']}, "
        f"deselected={deselected}, elapsed={elapsed:.2f}s "
        f"({timedelta(seconds=round(elapsed))}), exitstatus={int(exitstatus)}"
    )
    if pytest_result_log_path is not None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with pytest_result_log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"[{timestamp}] [INFO] [pytest] {summary}\n")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """실패한 테스트의 화면 증거를 저장한다.

    1. 준비·실행·정리 단계의 실패 리포트 확인
    2. fixture와 예외 프레임에서 WebDriver를 찾아 중복 제거
    3. 고유 이름으로 스크린샷 저장 및 경로 첨부, 캡처 실패 시 경고 기록
    4. Allure 기록이 활성화된 경우 같은 PNG를 해당 테스트에 첨부
    """
    outcome = yield
    report = outcome.get_result()
    if not report.failed:
        return

    candidates = list(getattr(item, "funcargs", {}).values())
    # 로그인 fixture가 yield 전에 실패하면 driver는 traceback의 지역 변수에 있다.
    if call.excinfo is not None:
        for entry in call.excinfo.traceback:
            candidates.extend(entry.frame.f_locals.values())

    drivers = {id(value): value for value in candidates if isinstance(value, WebDriver)}
    worker = os.environ.get("PYTEST_XDIST_WORKER", "main")
    test_name = re.sub(r"[^A-Za-z0-9_.-]", "_", item.name)[:60]
    directory = Path(item.config.rootpath) / "logs" / "screenshots"
    if not drivers:
        logger.info("스크린샷 생략: nodeid=%s, phase=%s, WebDriver 없음", item.nodeid, report.when)
    for index, driver in enumerate(drivers.values(), start=1):
        filename = (
            f"{test_name}_{report.when}_{worker}_{index}_"
            f"{datetime.now():%Y%m%d_%H%M%S_%f}_{uuid4().hex[:8]}.png"
        )
        path = directory / filename
        try:
            directory.mkdir(parents=True, exist_ok=True)
            saved = driver.save_screenshot(str(path))
        except (WebDriverException, OSError) as error:
            logger.warning(
                "스크린샷 저장 실패: nodeid=%s, phase=%s, error_type=%s",
                item.nodeid, report.when, type(error).__name__,
            )
            continue
        if not saved:
            logger.warning("스크린샷 저장 실패: path=%s, 반환값=False", path)
            continue
        report.sections.append(("Failure screenshot", str(path)))
        logger.info("실패 스크린샷 저장: nodeid=%s, path=%s", item.nodeid, path)
        if item.config.pluginmanager.hasplugin("allure_listener"):
            import allure

            try:
                allure.attach.file(
                    str(path),
                    name=f"실패 화면 ({report.when}, {worker}, {index})",
                    attachment_type=allure.attachment_type.PNG,
                )
            except OSError as error:
                logger.warning(
                    "Allure 스크린샷 첨부 실패: path=%s, error_type=%s",
                    path, type(error).__name__,
                )


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """개별 결과를 기억하고 실패 traceback을 기록한다.

    1. 실행 결과 또는 실패·건너뜀 상태 저장
    2. 실패한 리포트의 traceback을 별도 파일에 기록
    3. 병렬 실행은 controller만 traceback 기록
    """
    if report.when == "call" or report.failed or report.skipped:
        test_outcomes[report.nodeid] = report.outcome

    if parallel_worker or not report.failed or traceback_log_path is None:
        return

    with traceback_log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(f"[{report.nodeid}] phase={report.when}\n")
        log_file.write(report.longreprtext)
        log_file.write("\n\n")


def pytest_runtest_logstart(
    nodeid: str,
    location: tuple[str, int | None, str],
) -> None:
    """개별 테스트의 시작을 기록한다.

    1. 테스트별 시작 시각 저장
    2. 일반 로그에 테스트 ID 기록
    """
    test_started_at[nodeid] = time.monotonic()
    logger.info("테스트 시작: nodeid=%s", nodeid)


def pytest_runtest_logfinish(
    nodeid: str,
    location: tuple[str, int | None, str],
) -> None:
    """개별 테스트의 결과와 경과 시간을 기록한다.

    1. 저장된 시작 시각과 결과 조회 후 임시 기록 제거
    2. 일반 로그에 테스트 ID·결과·경과 시간 기록
    """
    started_at = test_started_at.pop(nodeid, None)
    outcome = test_outcomes.pop(nodeid, "unknown")
    if started_at is None:
        logger.info(
            "테스트 종료: nodeid=%s, outcome=%s, elapsed=unknown",
            nodeid,
            outcome,
        )
        return
    logger.info(
        "테스트 종료: nodeid=%s, outcome=%s, elapsed=%.2fs",
        nodeid,
        outcome,
        time.monotonic() - started_at,
    )


def _create_chrome_driver() -> webdriver.Chrome:
    """실행 환경에 맞는 공용 옵션으로 Chrome WebDriver를 생성한다.

    로컬은 일반 창으로 실행하고 HEADLESS=true인 CI 환경은 같은 해상도의
    headless Chrome으로 실행한다.
    """
    options = webdriver.ChromeOptions()
    headless = os.getenv("HEADLESS", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,880")
        logger.info("Chrome headless 실행: window_size=1920x880")

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"],
    )
    options.add_experimental_option(
        "prefs",
        {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
        },
    )
    chrome_driver = webdriver.Chrome(options=options)
    chrome_driver.set_window_size(1920, 880)
    return chrome_driver


@pytest.fixture
def driver():
    """단일 테스트(function 단위)에서 사용할 독립적인 Chrome WebDriver를 생성한다.

    단독 로그인 테스트 등 매 테스트마다 독립된 세션이 필요한 경우 사용한다.
    """
    chrome_driver = _create_chrome_driver()
    yield chrome_driver

    time.sleep(float(os.getenv("TEST_TEARDOWN_DELAY", "2")))
    chrome_driver.quit()


@pytest.fixture
def learner_driver():
    """학습자 단일 테스트(function 단위)용 Chrome WebDriver를 제공한다."""
    chrome_driver = _create_chrome_driver()
    yield chrome_driver

    time.sleep(float(os.getenv("TEST_TEARDOWN_DELAY", "2")))
    chrome_driver.quit()


@pytest.fixture
def learner_logged_out_with_learner_driver(learner_driver):
    """새로 생성된 로그아웃 상태의 학습자 전용 Driver를 제공한다."""
    return learner_driver


@pytest.fixture(scope="session")
def base_url() -> str:
    """환경변수에서 테스트 대상의 기본 URL을 반환한다.

    Returns:
        str: 마지막 슬래시를 제거한 기본 URL.

    Raises:
        ValueError: .env에 BASE_URL이 작성되지 않은 경우.
    """
    url = os.getenv("BASE_URL", "").strip()

    if not url:
        raise ValueError(".env 파일에 BASE_URL을 설정해야 합니다.")

    return url.rstrip("/")


def _educator_login_flow(driver: webdriver.Chrome, base_url: str) -> None:
    """교육자 로그인 및 QA6_2 클래스룸 진입 공통 플로우를 수행한다."""
    from pages.login_page import LoginPage
    from pages.educator.classroom_home_page import ClassroomHomePage

    educator_email = os.getenv("EDUCATOR_EMAIL", "").strip()
    educator_password = os.getenv("EDUCATOR_PASSWORD", "").strip()

    if not educator_email or not educator_password:
        pytest.skip(".env 파일에 EDUCATOR_EMAIL과 EDUCATOR_PASSWORD가 설정되지 않았습니다.")

    login_page = LoginPage(driver)
    login_page.navigate(base_url)
    login_page.login(educator_email, educator_password)

    is_logged_in = login_page.wait_until_logged_in(timeout=15)
    assert is_logged_in, "교육자 로그인에 실패했습니다."

    # 1. 로그인 직후 계정 확인 화면이 나타난 경우 먼저 통과한다.
    login_page.handle_reauth_if_present(
        educator_password,
        source="fixture.educator_login",
        reason="after_login",
    )

    # 2. QA6_2팀 최종프로젝트 클래스룸 진입
    classroom_home = ClassroomHomePage(driver)
    classroom_home.select_qa6_2_classroom()

    # 3. 클래스 진입 과정에서 비밀번호 재인증이 발생하는 경우 처리
    reauthenticated = login_page.handle_reauth_if_present(
        educator_password,
        source="fixture.educator_login",
        reason="class_selection",
    )

    # 4. 재인증 완료 후 원래 클래스 홈으로 자동 복귀하지 않은 경우만 1회 보완 이동
    if reauthenticated and not classroom_home.is_classroom_context_preserved():
        classroom_home.open_classroom_url()
        login_page.handle_reauth_if_present(
            educator_password,
            source="fixture.educator_login",
            reason="classroom_fallback_navigation",
        )

    # 5. 클래스 홈이 먼저 렌더링된 뒤 재인증으로 늦게 전환되는 경우를 확인한다.
    #    일반 페이지에 머무르면 Timeout은 정상적인 "재인증 없음" 결과다.
    try:
        WebDriverWait(driver, 5, poll_frequency=0.25).until(
            lambda current_driver: "accounts" in current_driver.current_url.lower()
            or "signin" in current_driver.current_url.lower()
        )
    except TimeoutException:
        delayed_reauth = False
    else:
        delayed_reauth = True
        logger.info("클래스 진입 후 지연된 비밀번호 재인증 화면 감지")

    if delayed_reauth:
        login_page.handle_reauth_if_present(
            educator_password,
            source="fixture.educator_login",
            reason="delayed_class_selection",
        )
        if not classroom_home.is_classroom_context_preserved():
            classroom_home.open_classroom_url()
            login_page.handle_reauth_if_present(
                educator_password,
                source="fixture.educator_login",
                reason="delayed_classroom_fallback_navigation",
            )

    # 6. 최종 클래스룸 홈 URL 및 핵심 네비게이션 요소 도달 보장
    assert classroom_home.wait_for_classroom_loaded(), (
        "교육자 로그인 및 재인증 후 QA6_2 클래스룸 진입에 실패했습니다."
    )


def _learner_login_flow(driver: webdriver.Chrome, base_url: str, learner_account: dict[str, str]) -> None:
    """학습자 로그인 및 QA6_2 클래스룸 진입 공통 플로우를 수행한다."""
    from pages.login_page import LoginPage
    from pages.learner.class_home import LearnClassHome

    login_page = LoginPage(driver)
    login_page.navigate(base_url)
    login_page.login(
        learner_account["user_id"],
        learner_account["password"],
    )

    is_logged_in = login_page.wait_until_logged_in(timeout=15)
    assert is_logged_in, "학습자 로그인에 실패했습니다."

    # 로그인 직후 계정 확인 화면이 나타난 경우 먼저 통과한다.
    login_page.handle_reauth_if_present(
        learner_account["password"],
        source="fixture.learner_login",
        reason="after_login",
    )

    # QA6_2팀 최종프로젝트 클래스룸 진입
    class_home = LearnClassHome(driver)
    class_home.enter_team_project()

    # 클래스 접근 권한 확인 과정에서 재인증이 새로 발생할 수 있다.
    # enter_team_project는 클래스룸/재인증 중 먼저 도착한 화면까지 기다리므로,
    # 이 시점에는 URL을 즉시 검사해도 재인증 화면을 놓치지 않는다.
    reauthenticated = login_page.handle_reauth_if_present(
        learner_account["password"],
        source="fixture.learner_login",
        reason="class_selection",
    )

    if reauthenticated and not class_home.wait_until_team_project_open():
        # 재인증 완료 후 원래 클래스 URL로 자동 복귀하지 않은 경우만 재이동한다.
        class_home.open_team_project_url()
        login_page.handle_reauth_if_present(
            learner_account["password"],
            source="fixture.learner_login",
            reason="classroom_fallback_navigation",
        )

    assert class_home.wait_until_team_project_open(), (
        "학습자 재인증 후 QA6_2 클래스룸 진입에 실패했습니다."
    )


# ==============================================================================
# [Module Scope 픽스처 - 기본 권장] 파일당 1회 로그인 세션 재사용 (속도 향상 & 재인증 방지)
# ==============================================================================
@pytest.fixture(scope="module")
def educator_logged_in(base_url):
    """[기본 권장] 모듈(파일) 단위로 1회 로그인하고 클래스룸에 진입한 WebDriver를 제공한다."""
    chrome_driver = _create_chrome_driver()
    _educator_login_flow(chrome_driver, base_url)
    yield chrome_driver
    time.sleep(float(os.getenv("TEST_TEARDOWN_DELAY", "2")))
    chrome_driver.quit()


@pytest.fixture(scope="module")
def learner_logged_in(base_url, learner_account):
    """[기본 권장] 모듈(파일) 단위로 1회 로그인하고 QA6_2 클래스룸에 진입한 WebDriver를 제공한다."""
    chrome_driver = _create_chrome_driver()
    _learner_login_flow(chrome_driver, base_url, learner_account)
    yield chrome_driver
    time.sleep(float(os.getenv("TEST_TEARDOWN_DELAY", "2")))
    chrome_driver.quit()


# ==============================================================================
# [Function Scope 픽스처] 매 테스트(TC)마다 독립적으로 새 브라우저 열고 로그인
# ==============================================================================
@pytest.fixture(scope="function")
def educator_logged_in_function(base_url):
    """단일 테스트(TC)마다 독립적으로 새 브라우저를 열고 교육자 로그인을 수행한다."""
    chrome_driver = _create_chrome_driver()
    _educator_login_flow(chrome_driver, base_url)
    yield chrome_driver
    time.sleep(float(os.getenv("TEST_TEARDOWN_DELAY", "2")))
    chrome_driver.quit()


@pytest.fixture(scope="function")
def learner_logged_in_function(base_url, learner_account):
    """단일 테스트(TC)마다 독립적으로 새 브라우저를 열고 학습자 로그인을 수행한다."""
    chrome_driver = _create_chrome_driver()
    _learner_login_flow(chrome_driver, base_url, learner_account)
    yield chrome_driver
    time.sleep(float(os.getenv("TEST_TEARDOWN_DELAY", "2")))
    chrome_driver.quit()


@pytest.fixture
def learner_logged_in_with_learner_driver(
    learner_driver,
    base_url,
    learner_account,
):
    """학습자 전용 Driver로 로그인하여 QA6_2 클래스룸에 진입한다."""
    _learner_login_flow(learner_driver, base_url, learner_account)
    return learner_driver


# ==============================================================================
# [Session Scope 픽스처] 전체 pytest 실행 동안 브라우저 1개로 단 1회 로그인 유지
# ==============================================================================
@pytest.fixture(scope="session")
def educator_logged_in_session(base_url):
    """전체 pytest 세션 동안 브라우저를 1회만 열고 교육자 로그인을 유지한다."""
    chrome_driver = _create_chrome_driver()
    _educator_login_flow(chrome_driver, base_url)
    yield chrome_driver
    time.sleep(float(os.getenv("TEST_TEARDOWN_DELAY", "2")))
    chrome_driver.quit()


@pytest.fixture(scope="session")
def learner_logged_in_session(base_url, learner_account):
    """전체 pytest 세션 동안 브라우저를 1회만 열고 학습자 로그인을 유지한다."""
    chrome_driver = _create_chrome_driver()
    _learner_login_flow(chrome_driver, base_url, learner_account)
    yield chrome_driver
    time.sleep(float(os.getenv("TEST_TEARDOWN_DELAY", "2")))
    chrome_driver.quit()


@pytest.fixture(scope="session")
def learner_account():
    """환경변수에서 학습자 로그인 계정을 반환한다."""
    user_id = os.getenv("LEARNER_EMAIL", "").strip()
    password = os.getenv("LEARNER_PASSWORD", "").strip()

    if not user_id or not password:
        pytest.fail(
            "LEARNER_EMAIL 또는 LEARNER_PASSWORD가 설정되지 않았습니다. "
            "프로젝트 루트의 .env 파일을 확인하세요."
        )

    return {
        "user_id": user_id,
        "password": password,
    }
