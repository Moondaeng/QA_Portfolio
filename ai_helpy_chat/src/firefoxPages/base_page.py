import logging
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logger = logging.getLogger(__name__)


class BasePage:
    """페이지 탐색에 필요한 공통 기능을 제공하는 기본 Page Object.

    URL 이동, 요소 탐색, 입력, 클릭, 호버,
    스크롤 및 포인터 이동 기능을 제공한다.
    """
    # 프로젝트의 메인 콘텐츠 구조에 맞게 필요하면 재정의한다.
    MAIN_LOCATOR = (
        By.CSS_SELECTOR,
        "main, [role='main']",
    )

    def __init__(self, driver, timeout=None, action_delay=0):
        self.driver = driver
        self.default_timeout = 30 if timeout is None else timeout
        self.action_delay = action_delay

    def _get_timeout(self, timeout):
        """전달된 타임아웃 또는 기본 타임아웃을 반환한다.

        Args:
            timeout: 적용할 대기시간.

        Returns:
            int | float: 적용할 대기시간.
        """
        return self.default_timeout if timeout is None else timeout

    def pause_for_debugging(self, seconds=None):
        """디버깅 중 동작을 눈으로 확인하기 위해 선택적으로 대기한다.

        Args:
            seconds: 대기시간. 지정하지 않으면 action_delay를 사용한다.
        """
        if self.action_delay <= 0:
            return

        delay = self.action_delay if seconds is None else seconds

        if delay < 0:
            raise ValueError("seconds는 0 이상이어야 합니다.")

        time.sleep(delay)

    def open_url(self, url):
        """지정한 URL로 이동한다.

        Args:
            url: 이동할 페이지 주소.
        """
        logger.info("페이지 이동: url=%s", url)
        self.driver.get(url)

    def wait_for_visible(self, locator, timeout=None):
        """보이는 요소를 찾을 때까지 기다린다.

        Args:
            locator: 요소를 찾기 위한 locator.
            timeout: 최대 대기시간.

        Returns:
            WebElement: 화면에 표시된 요소.
        """
        timeout = self._get_timeout(timeout)

        return WebDriverWait(
            self.driver,
            timeout
        ).until(
            EC.visibility_of_element_located(locator)
        )



    def wait_for_invisible(self, locator, timeout=None):
        """안보이는 요소를 찾을 때까지 기다린다.

        Args:
            locator: 요소를 찾기 위한 locator.
            timeout: 최대 대기시간.

        Returns:
            bool: 요소가 화면에서 사라지면 True.
        """
        timeout = self._get_timeout(timeout)

        return WebDriverWait(
            self.driver,
            timeout
        ).until(
            EC.invisibility_of_element_located(locator)
        )

    def wait_for_clickable(self, locator, timeout=None):
        """클릭 가능한 요소를 찾을 때까지 기다린다.

        Args:
            locator: 요소를 찾기 위한 locator.
            timeout: 최대 대기시간.

        Returns:
            WebElement: 표시되고 활성화된 요소.
        """
        timeout = self._get_timeout(timeout)

        return WebDriverWait(
            self.driver,
            timeout
        ).until(
            EC.element_to_be_clickable(locator)
        )

    def wait_for_present(self, locator, timeout=None):
        """단일 요소가 DOM에 나타날 때까지 대기한 뒤 반환한다.

        Args:
            locator: Selenium locator 튜플(By, value).
            timeout: 최대 대기시간.

        Returns:
            WebElement: DOM에 존재하는 요소.
        """
        timeout = self._get_timeout(timeout)

        return WebDriverWait(
            self.driver,
            timeout,
        ).until(
            EC.presence_of_element_located(locator)
        )

    def wait_for_all_present(self, locator, timeout=None):
        """여러 요소가 DOM에 나타날 때까지 대기한 뒤 반환한다.

        Args:
            locator: Selenium locator 튜플(By, value).
            timeout: 최대 대기시간.

        Returns:
            list[WebElement]: DOM에 존재하는 요소 목록.
        """
        timeout = self._get_timeout(timeout)

        wait = WebDriverWait(self.driver, timeout)
        return wait.until(
            EC.presence_of_all_elements_located(locator)
        )

    def wait_for_first_visible(self, locator, timeout=None):
        """중복 요소 중 화면에 표시된 첫 번째 요소를 반환한다.

        React, MUI, Virtuoso처럼 재렌더링이 잦은 환경에서
        flaky 테스트를 줄이기 위해 제한 시간 동안 요소를 반복 탐색한다.

        Args:
            locator: 숨겨진 요소를 포함한 중복 요소의 locator.
            timeout: 최대 대기시간.

        Returns:
            WebElement: 화면에 표시된 첫 번째 요소.
        """
        timeout = self._get_timeout(timeout)

        def _find_visible(driver):
            elements = driver.find_elements(*locator)

            for element in elements:
                try:
                    if element.is_displayed():
                        return element
                except StaleElementReferenceException:
                    continue

            # WebDriverWait가 조건 함수를 다시 호출하도록 False를 반환한다.
            return False

        return WebDriverWait(
            self.driver,
            timeout,
        ).until(_find_visible)

    def find_optional_visible(self, locator, timeout=None):
        """표시된 첫 번째 요소를 반환하고, 없으면 None을 반환한다.

        요소가 없어도 정상인 선택적 UI를 확인할 때 사용한다.

        Args:
            locator: 요소를 찾기 위한 locator.
            timeout: 최대 대기시간.

        Returns:
            WebElement | None:
                표시된 첫 번째 요소 또는 찾지 못하면 None.
        """
        try:
            return self.wait_for_first_visible(locator, timeout)
        except TimeoutException:
            logger.debug(
                "선택적 요소가 보이지 않음: locator=%s",
                locator,
            )
            return None


    def fill_text(self, locator, text, clear_first=True, timeout=None):
        """표시된 입력 요소에 텍스트를 입력한다.

        Args:
            locator: 입력 요소의 locator.
            text: 입력할 텍스트.
            clear_first: 기존 값을 먼저 지울지 여부.
            timeout: 최대 대기시간.

        Returns:
            WebElement: 텍스트를 입력한 요소.
        """

        element = self.wait_for_visible(locator, timeout)

        if clear_first:
            element.clear()

        element.send_keys(text)
        return element

    def _try_click_element(self, locator):
        """요소 클릭을 한 번 시도하고, 재시도가 필요하면 False를 반환한다."""
        try:
            element = EC.element_to_be_clickable(locator)(self.driver)

            if not element:
                return False

            element.click()
            logger.debug("요소 클릭 완료: locator=%s", locator)
            return element

        except (
            StaleElementReferenceException,
            ElementClickInterceptedException,
        ) as error:
            logger.debug(
                "요소 클릭 재시도: locator=%s, error=%s",
                locator,
                type(error).__name__,
            )
            return False

    def click(self, locator, timeout=None):
        """요소가 클릭 가능해질 때까지 대기한 뒤 클릭한다.

        Stale 또는 일시적인 클릭 차단이 발생하면 제한 시간 동안
        요소를 다시 탐색하여 클릭을 재시도한다.

        Args:
            locator: 클릭할 요소의 locator.
            timeout: 최대 대기시간.

        Returns:
            WebElement: 클릭한 요소.

        Raises:
            TimeoutException: 제한 시간 안에 클릭하지 못한 경우.
        """
        timeout = self._get_timeout(timeout)

        try:
            # locator를 조건 함수에 전달하기 위해 lambda를 사용한다.
            return WebDriverWait(
                self.driver,
                timeout
            ).until(
                lambda _: self._try_click_element(locator)
            )

        except TimeoutException as error:
            raise TimeoutException(
                f"요소 클릭에 실패했습니다: locator={locator}"
            ) from error

    def click_if_present(self, locator, timeout=2):
        """요소가 존재하고 클릭 가능할 때 클릭한다.

        요소가 제한 시간 안에 나타나지 않으면 테스트를 실패시키지 않고
        False를 반환한다.

        Args:
            locator: 클릭할 요소의 locator.
            timeout: 선택적 요소를 기다릴 최대 시간.

        Returns:
            WebElement | bool:
                클릭한 요소 또는 요소가 없으면 False.
        """
        try:
            return self.click(locator, timeout=timeout)
        except TimeoutException:
            logger.debug(
                "선택적 요소를 제한 시간 내 클릭하지 못함: locator=%s",
                locator,
            )
            return False

    def click_with_javascript(self, element):
        """JavaScript로 WebElement의 click 이벤트를 실행한다.

        일반적인 Selenium 클릭으로 처리할 수 없는 경우에만 사용한다.
        실제 사용자 클릭과 동작이 다를 수 있으므로 기본 클릭의
        대체 수단으로 사용하지 않는다.
        """
        logger.warning("JavaScript 클릭 사용: element=%s", element)
        self.driver.execute_script(
            "arguments[0].click();",
            element,
        )
        return element

    def _try_click_element_by_index(self, locator, index):
        """목록에서 지정한 인덱스의 요소 클릭을 한 번 시도한다.

        조건을 만족하지 않으면 WebDriverWait가 다시 호출할 수 있도록
        False를 반환한다.

        Args:
            locator: 요소 목록의 locator.
            index: 클릭할 요소의 인덱스.

        Returns:
            WebElement | bool:
                클릭 가능한 요소 또는 조건을 충족하지 않으면 False.
        """
        elements = self.driver.find_elements(*locator)
        element_count = len(elements)

        if not -element_count <= index < element_count:
            return False

        element = elements[index]

        try:
            if element.is_displayed() and element.is_enabled():
                element.click()
                logger.debug(
                    "목록 요소 클릭 완료: locator=%s, index=%s",
                    locator,
                    index,
                )
                return element

            return False

        except (
            StaleElementReferenceException,
            ElementClickInterceptedException,
        ) as error:
            logger.debug(
                "목록 요소 클릭 재시도: locator=%s, index=%s, error=%s",
                locator,
                index,
                type(error).__name__,
            )
            return False

    def click_from_list(self, locator, index, timeout=None):
        """요소 목록에서 지정한 인덱스의 요소를 클릭한다.

        동적 목록의 개수가 부족하거나 요소가 클릭 가능한 상태가 아니면
        제한 시간 동안 목록을 다시 조회한다.

        Args:
            locator: 요소 목록을 찾기 위한 locator.
            index: 클릭할 요소의 인덱스.
            timeout: 최대 대기시간.

        Returns:
            WebElement: 클릭한 요소.

        Raises:
            IndexError: 제한 시간 후에도 인덱스가 범위를 벗어난 경우.
            TimeoutException: 요소가 없거나 클릭 가능한 상태가 되지 않은 경우.
        """
        timeout = self._get_timeout(timeout)

        try:
            # locator와 index를 조건 함수에 전달하기 위해 lambda를 사용한다.
            return WebDriverWait(
                self.driver,
                timeout,
            ).until(
                lambda _: self._try_click_element_by_index(
                    locator,
                    index,
                )
            )

        except TimeoutException as error:
            elements = self.driver.find_elements(*locator)
            element_count = len(elements)

            if (
                element_count > 0
                and not -element_count <= index < element_count
            ):
                raise IndexError(
                    f"인덱스 범위 초과: index={index}, "
                    f"element_count={element_count}"
                ) from error

            raise

    def hover_to_main(self):
        """메인 영역으로 마우스 포인터를 이동한다."""
        target = self.wait_for_visible(self.MAIN_LOCATOR)

        ActionChains(self.driver).move_to_element(target).perform()
        return target

    def hover(self, locator):
        """특정 요소로 마우스를 이동시킨다.

        Args:
            locator: 호버할 요소의 locator

        Returns:
            WebElement: 마우스 포인터를 이동한 요소.
        """
        element = self.wait_for_visible(locator)
        ActionChains(self.driver).move_to_element(element).perform()

        return element

    def hover_element(self, element):
        """전달받은 WebElement로 마우스 포인터를 이동한다.

        Args:
            element: 호버할 WebElement.

        Returns:
            WebElement: 마우스 포인터를 이동한 요소.
        """
        ActionChains(self.driver).move_to_element(element).perform()
        return element

    def scroll_window(self, pos_x=0, pos_y=0):
        """페이지를 스크롤한다.

        별도의 스크롤 컨테이너를 사용하는 페이지에는 적용되지 않는다.

        Args:
            pos_x: 가로 이동 거리.
            pos_y: 세로 이동 거리.
        """
        self.driver.execute_script(
            "window.scrollBy("
            "arguments[0], arguments[1]"
            ");",
            pos_x,
            pos_y,
        )

    def scroll_window_to_bottom(self):
        """브라우저 문서의 최하단으로 이동한다.

        별도의 스크롤 컨테이너를 사용하는 페이지에는 적용되지 않는다.
        """
        self.driver.execute_script(
            "window.scrollTo("
            "0, document.documentElement.scrollHeight"
            ");"
        )


    def scroll_element_by(self, locator, pos_x=0, pos_y=0):
        """요소 내부를 지정한 거리만큼 스크롤한다.

        Args:
            locator: 스크롤 대상 locator.
            pos_x: 가로 이동 거리.
            pos_y: 세로 이동 거리.

        Returns:
            WebElement: 스크롤 대상 요소.
        """
        element = self.wait_for_present(locator)

        self.driver.execute_script(
            "arguments[0].scrollLeft += arguments[1];"
            "arguments[0].scrollTop += arguments[2];",
            element,
            pos_x,
            pos_y,
        )

        return element

    def scroll_into_view(self, locator):
        """지정한 요소가 보이도록 스크롤한다.

        Args:
            locator: 스크롤할 요소의 locator.

        Returns:
            WebElement: 스크롤한 요소.
        """
        element = self.wait_for_present(locator)
        self.scroll_element_into_view(element)
        return element

    def _is_element_center_in_viewport(self, element):
        """요소의 중심점이 viewport 내부에 있는지 확인한다."""
        return self.driver.execute_script(
            """
            const rect = arguments[0].getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;

            return (
                centerX >= 0 &&
                centerX <= window.innerWidth &&
                centerY >= 0 &&
                centerY <= window.innerHeight
            );
            """,
            element,
        )

    def scroll_element_into_view(
        self,
        element,
        block="center",
        timeout=None,
    ):
        """지정한 WebElement가 보이도록 스크롤한다.

        Args:
            element: 스크롤할 WebElement.
            block: 세로 정렬 위치.
            timeout: 요소 중심점이 viewport에 들어올 때까지의 최대 대기시간.

        Returns:
            WebElement: 스크롤한 요소.

        Raises:
            ValueError: 지원하지 않는 block 값을 전달한 경우.
            TimeoutException: 요소 중심점이 viewport에 들어오지 않은 경우.
        """
        allowed_blocks = {"start", "center", "end", "nearest"}

        if block not in allowed_blocks:
            raise ValueError(
                f"지원하지 않는 block 값입니다: {block}"
            )

        timeout = self._get_timeout(timeout)

        self.driver.execute_script(
            """
            arguments[0].scrollIntoView({
                block: arguments[1],
                inline: "nearest",
                behavior: "instant"
            });
            """,
            element,
            block,
        )

        WebDriverWait(
            self.driver,
            timeout,
        ).until(
            lambda _: self._is_element_center_in_viewport(element)
        )

        logger.debug(
            "요소를 viewport 안으로 스크롤: block=%s",
            block,
        )
        return element
