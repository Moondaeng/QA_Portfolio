import logging
import time

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# Selenium locator는 다음과 같은 튜플 형태로 전달한다.
# 예: (By.ID, "login-button")
Locator = tuple[str, str]

logger = logging.getLogger(__name__)


class BasePage:
    """모든 Page Object가 공통으로 사용하는 기본 기능을 제공한다.

    페이지 이동, 요소 대기, 입력, 클릭, 호버와 스크롤처럼
    여러 화면에서 반복되는 Selenium 동작만 이 클래스에서 관리한다.

    로그인이나 게시글 작성처럼 특정 화면에서만 사용하는 기능은
    BasePage가 아니라 해당 Page Object에 작성한다.
    """

    def __init__(self, driver: WebDriver, timeout: float = 15) -> None:
        """BasePage를 초기화한다.

        Args:
            driver: pytest fixture에서 생성한 Selenium WebDriver.
            timeout: 요소를 기다릴 기본 최대 시간(초).

        Raises:
            ValueError: timeout이 0 이하인 경우.
        """
        if timeout <= 0:
            raise ValueError("timeout은 0보다 커야 합니다.")

        self.driver = driver
        self.default_timeout = timeout

    def _get_timeout(self, timeout: float | None) -> float:
        """메서드에서 실제로 사용할 대기시간을 반환한다.

        각 메서드에 timeout을 전달하면 해당 값을 사용하고,
        전달하지 않으면 BasePage 생성 시 설정한 기본값을 사용한다.

        Args:
            timeout: 개별 동작에 적용할 최대 대기시간. None이면 기본값 사용.

        Returns:
            float: 실제로 사용할 최대 대기시간.

        Raises:
            ValueError: 전달된 timeout이 0 이하인 경우.
        """
        selected_timeout = (
            self.default_timeout if timeout is None else timeout
        )

        if selected_timeout <= 0:
            raise ValueError("timeout은 0보다 커야 합니다.")

        return selected_timeout

    def open_url(self, url: str) -> None:
        """지정한 URL로 이동한다.

        Args:
            url: 이동할 페이지 주소.
        """
        logger.info("페이지 이동: url=%s", url)
        self.driver.get(url)

    def wait_for_present(
        self,
        locator: Locator,
        timeout: float | None = None,
    ) -> WebElement:
        """요소가 DOM에 생성될 때까지 기다린 후 반환한다.

        요소가 화면에 보이지 않아도 DOM에만 존재하면 반환한다.
        숨겨진 요소나 스크롤 컨테이너를 찾을 때 사용할 수 있다.
        사용자가 보는 요소에는 보통 wait_for_visible을 우선 사용한다.

        Args:
            locator: 요소를 찾기 위한 Selenium locator 튜플.
            timeout: 최대 대기시간. None이면 기본 대기시간 사용.

        Returns:
            WebElement: DOM에서 찾은 요소.

        Raises:
            TimeoutException: 제한 시간 안에 요소가 DOM에 나타나지 않은 경우.
        """
        selected_timeout = self._get_timeout(timeout)

        return WebDriverWait(self.driver, selected_timeout).until(
            EC.presence_of_element_located(locator)
        )

    def wait_for_visible(
        self,
        locator: Locator,
        timeout: float | None = None,
    ) -> WebElement:
        """요소가 화면에 표시될 때까지 기다린 후 반환한다.

        Args:
            locator: 요소를 찾기 위한 Selenium locator 튜플.
            timeout: 최대 대기시간. None이면 기본 대기시간 사용.

        Returns:
            WebElement: 화면에 표시된 요소.

        Raises:
            TimeoutException: 제한 시간 안에 요소가 표시되지 않은 경우.
        """
        selected_timeout = self._get_timeout(timeout)

        return WebDriverWait(self.driver, selected_timeout).until(
            EC.visibility_of_element_located(locator)
        )

    def wait_for_clickable(
        self,
        locator: Locator,
        timeout: float | None = None,
    ) -> WebElement:
        """요소가 표시되고 활성화될 때까지 기다린 후 반환한다.

        버튼 클릭이나 입력처럼 사용자가 조작하는 요소에 사용한다.

        Args:
            locator: 요소를 찾기 위한 Selenium locator 튜플.
            timeout: 최대 대기시간. None이면 기본 대기시간 사용.

        Returns:
            WebElement: 표시되고 활성화된 요소.

        Raises:
            TimeoutException: 제한 시간 안에 클릭 가능한 상태가 되지 않은 경우.
        """
        selected_timeout = self._get_timeout(timeout)

        return WebDriverWait(self.driver, selected_timeout).until(
            EC.element_to_be_clickable(locator)
        )

    def wait_for_invisible(
        self,
        locator: Locator,
        timeout: float | None = None,
    ) -> bool:
        """요소가 화면에서 사라질 때까지 기다린다.

        로딩 표시나 팝업이 사라진 뒤 다음 동작을 수행해야 할 때 사용한다.

        Args:
            locator: 사라짐을 확인할 요소의 Selenium locator 튜플.
            timeout: 최대 대기시간. None이면 기본 대기시간 사용.

        Returns:
            bool: 요소가 사라지면 True.

        Raises:
            TimeoutException: 제한 시간 안에 요소가 사라지지 않은 경우.
        """
        selected_timeout = self._get_timeout(timeout)

        return WebDriverWait(self.driver, selected_timeout).until(
            EC.invisibility_of_element_located(locator)
        )

    def wait_for_first_visible(
        self,
        locator: Locator,
        timeout: float | None = None,
    ) -> WebElement:
        """같은 locator로 찾은 요소 중 화면에 보이는 첫 요소를 반환한다.

        React나 MUI 화면에서는 같은 요소가 DOM에 여러 개 존재하고,
        일부 요소만 실제 화면에 표시되는 경우가 있다. 이런 경우에
        숨겨진 요소를 제외하고 현재 보이는 요소를 선택한다.

        Args:
            locator: 중복 요소를 찾기 위한 Selenium locator 튜플.
            timeout: 최대 대기시간. None이면 기본 대기시간 사용.

        Returns:
            WebElement: 화면에 표시된 첫 번째 요소.

        Raises:
            TimeoutException: 제한 시간 안에 표시된 요소를 찾지 못한 경우.
        """
        selected_timeout = self._get_timeout(timeout)

        def find_visible_element(driver: WebDriver) -> WebElement | bool:
            """현재 화면에 보이는 첫 요소를 찾는 대기 조건 함수다."""
            elements = driver.find_elements(*locator)

            for element in elements:
                try:
                    if element.is_displayed():
                        return element
                except StaleElementReferenceException:
                    # 화면이 다시 렌더링되면 기존 요소가 사라질 수 있다.
                    # False를 반환하면 WebDriverWait가 locator를 다시 조회한다.
                    continue

            return False

        return WebDriverWait(self.driver, selected_timeout).until(
            find_visible_element
        )

    def find_optional_visible(
        self,
        locator: Locator,
        timeout: float = 2,
    ) -> WebElement | None:
        """선택적 요소가 보이면 반환하고, 보이지 않으면 None을 반환한다.

        이벤트 팝업이나 안내 배너처럼 없어도 정상인 요소에만 사용한다.
        반드시 존재해야 하는 요소에는 이 메서드를 사용하지 않는다.

        Args:
            locator: 선택적 요소를 찾기 위한 Selenium locator 튜플.
            timeout: 선택적 요소를 기다릴 최대 시간(초).

        Returns:
            WebElement | None: 보이는 요소 또는 요소가 없으면 None.
        """
        try:
            return self.wait_for_first_visible(locator, timeout)
        except TimeoutException:
            logger.debug("선택적 요소가 보이지 않음: locator=%s", locator)
            return None

    def find_elements_visible(
        self,
        locator: Locator,
        timeout: float | None = None,
    ) -> list[WebElement]:
        """화면에 표시된 locator 일치 요소들을 반환한다.

        목록 화면처럼 같은 locator에 여러 요소가 대응되는 경우에 사용한다.
        최소 한 개가 표시될 때까지 기다린 뒤, 재렌더링으로 숨겨진 요소는
        결과에서 제외한다.
        """
        selected_timeout = self._get_timeout(timeout)

        def find_visible_elements(_: WebDriver) -> list[WebElement] | bool:
            visible_elements: list[WebElement] = []

            for element in self.driver.find_elements(*locator):
                try:
                    if element.is_displayed():
                        visible_elements.append(element)
                except StaleElementReferenceException:
                    continue

            return visible_elements or False

        return WebDriverWait(self.driver, selected_timeout).until(
            find_visible_elements
        )

    def get_text(
        self,
        locator: Locator,
        timeout: float | None = None,
    ) -> str:
        """화면에 보이는 요소의 공백을 정리한 텍스트를 반환한다."""
        return self.wait_for_first_visible(locator, timeout).text.strip()

    def fill_text(
        self,
        locator: Locator,
        text: str,
        clear_first: bool = True,
        timeout: float | None = None,
    ) -> WebElement:
        """입력 요소에 텍스트를 입력한다.

        입력 요소가 표시되고 활성화될 때까지 기다린다. clear_first가
        True이면 기존 값을 지운 후 새로운 텍스트를 입력한다.

        Args:
            locator: 입력 요소를 찾기 위한 Selenium locator 튜플.
            text: 입력할 문자열.
            clear_first: 기존 입력값을 먼저 지울지 여부.
            timeout: 최대 대기시간. None이면 기본 대기시간 사용.

        Returns:
            WebElement: 텍스트를 입력한 요소.

        Raises:
            TimeoutException: 제한 시간 안에 입력 가능한 상태가 되지 않은 경우.
        """
        selected_timeout = self._get_timeout(timeout)

        def fill_current_element(_: WebDriver) -> WebElement | bool:
            """재렌더링된 입력 요소를 매번 다시 찾아 입력한다."""
            try:
                element = EC.element_to_be_clickable(locator)(self.driver)
                if not element:
                    return False

                # DOM 상의 존재/활성화만으로는 사람이 볼 수 있는 입력 대상인지
                # 보장되지 않는다. 중심점이 현재 뷰포트 안에 들어온 뒤 입력한다.
                self.scroll_element_into_view(element, block="center", timeout=1)
                if clear_first:
                    element.clear()
                element.send_keys(text)
                return element
            except StaleElementReferenceException:
                return False

        return WebDriverWait(self.driver, selected_timeout).until(fill_current_element)

    def _try_click_element(self, locator: Locator) -> WebElement | bool:
        """요소 클릭을 한 번 시도한다.

        화면 재렌더링이나 다른 요소의 일시적인 가로막힘 때문에 클릭하지
        못하면 False를 반환한다. click 메서드의 WebDriverWait가 이 함수를
        다시 호출하면서 locator도 새로 조회한다.

        Args:
            locator: 클릭할 요소의 Selenium locator 튜플.

        Returns:
            WebElement | bool: 클릭한 요소 또는 재시도가 필요하면 False.
        """
        try:
            element = EC.element_to_be_clickable(locator)(self.driver)

            if not element:
                return False

            # DOM에만 존재하는 요소가 아니라 사용자가 실제로 보는 위치에서
            # 클릭되도록, 요소 중심점이 브라우저 뷰포트 안에 들어온 것을
            # 확인한 뒤 클릭한다.
            self.scroll_element_into_view(element, block="center", timeout=1)
            element.click()
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

    def click(
        self,
        locator: Locator,
        timeout: float | None = None,
    ) -> WebElement:
        """요소가 클릭 가능할 때까지 기다린 후 클릭한다.

        화면 재렌더링으로 요소가 바뀌거나 다른 요소가 일시적으로 클릭을
        가로막으면 제한 시간 동안 locator를 다시 조회하여 클릭한다.

        Args:
            locator: 클릭할 요소의 Selenium locator 튜플.
            timeout: 최대 대기시간. None이면 기본 대기시간 사용.

        Returns:
            WebElement: 클릭한 요소.

        Raises:
            TimeoutException: 제한 시간 안에 요소를 클릭하지 못한 경우.
        """
        selected_timeout = self._get_timeout(timeout)

        try:
            return WebDriverWait(self.driver, selected_timeout).until(
                lambda _: self._try_click_element(locator)
            )
        except TimeoutException as error:
            raise TimeoutException(
                f"요소 클릭에 실패했습니다: locator={locator}"
            ) from error

    def click_when_position_stable(
        self, locator: Locator, timeout: float | None = None,
    ) -> WebElement:
        """스크롤 후 가리지 않은 요소의 위치가 0.5초간 안정되면 클릭한다.

        DOM 교체와 클릭 가로막힘은 제한 시간 내 다시 조회한다.
        성공한 클릭은 반복하지 않으며 화면 전환 확인은 호출자가 담당한다.
        """
        previous = None
        stable_since = time.monotonic()
        last_state: dict[str, object] = {"reason": "not_found"}

        def click_ready_element(driver):
            nonlocal previous, stable_since, last_state
            try:
                elements = driver.find_elements(*locator)
                if not elements:
                    last_state = {"reason": "not_found"}

                for element in elements:
                    displayed = element.is_displayed()
                    enabled = element.is_enabled()
                    if not displayed or not enabled:
                        last_state = {
                            "reason": "not_interactable",
                            "displayed": displayed,
                            "enabled": enabled,
                        }
                        continue
                    if not self._is_element_center_in_viewport(element):
                        last_state = {
                            "reason": "outside_viewport",
                            "rect": driver.execute_script(
                                "const r=arguments[0].getBoundingClientRect();"
                                "return [r.left,r.top,r.width,r.height];",
                                element,
                            ),
                            "viewport": driver.execute_script(
                                "return [window.innerWidth,window.innerHeight];"
                            ),
                        }
                        driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center', "
                            "inline: 'nearest', behavior: 'instant'});", element,
                        )
                        previous = None
                        return False
                    state = driver.execute_script(
                        """
                        const e = arguments[0], r = e.getBoundingClientRect();
                        const top = document.elementFromPoint(
                            r.left + r.width / 2, r.top + r.height / 2);
                        return {clear: top === e || e.contains(top),
                            rect: [r.left, r.top, r.width, r.height],
                            viewport: [window.innerWidth, window.innerHeight],
                            topTag: top ? top.tagName : null,
                            topClass: top ? (top.getAttribute('class') || '') : null};
                        """, element,
                    )
                    current = (element.id, state["rect"])
                    if not state["clear"]:
                        last_state = {
                            "reason": "covered",
                            "rect": state["rect"],
                            "viewport": state["viewport"],
                            "top_tag": state["topTag"],
                            "top_class": state["topClass"],
                        }
                        previous = None
                        return False
                    if current != previous:
                        last_state = {
                            "reason": "position_changed",
                            "rect": state["rect"],
                            "viewport": state["viewport"],
                        }
                        previous = current
                        stable_since = time.monotonic()
                        return False
                    # 0.2초 polling에서 여러 차례 같은 위치와 가림 상태가 유지되는지 확인한다.
                    if time.monotonic() - stable_since < 0.5:
                        last_state = {
                            "reason": "stabilizing",
                            "rect": state["rect"],
                            "viewport": state["viewport"],
                        }
                        return False
                    element.click()
                    logger.info("위치 안정 및 가림 확인 후 클릭 완료: locator=%s", locator)
                    return element
            except (StaleElementReferenceException, ElementClickInterceptedException) as error:
                last_state = {"reason": type(error).__name__}
                previous = None
                logger.debug("클릭 전 DOM 또는 가림 상태 변경: locator=%s", locator)
            previous = None
            return False

        try:
            return WebDriverWait(
                self.driver, self._get_timeout(timeout), poll_frequency=0.2,
            ).until(click_ready_element)
        except TimeoutException as error:
            logger.error(
                "스크롤 후 클릭 준비 대기 실패: locator=%s, last_state=%s",
                locator,
                last_state,
            )
            raise TimeoutException(
                f"스크롤 후 클릭 준비 대기 실패: locator={locator}, "
                f"last_state={last_state}"
            ) from error

    def click_with_javascript(self, element: WebElement) -> WebElement:
        """JavaScript를 사용해 WebElement의 click 이벤트를 실행한다.

        일반적인 Selenium 클릭과 실제 동작이 다를 수 있으므로 기본 클릭의
        대체 수단으로 사용하지 않는다. 일반 click이 실패하는 원인을 확인한
        뒤 JavaScript 클릭이 필요한 것으로 판단된 경우에만 사용한다.

        Args:
            element: JavaScript로 클릭할 WebElement.

        Returns:
            WebElement: 클릭 이벤트를 실행한 요소.
        """
        logger.warning("JavaScript 클릭 사용: element=%s", element)
        self.driver.execute_script("arguments[0].click();", element)
        return element

    def _is_element_center_in_viewport(self, element: WebElement) -> bool:
        """요소의 중심점이 현재 브라우저 화면 안에 있는지 확인한다.

        Args:
            element: 화면 내부에 있는지 확인할 WebElement.

        Returns:
            bool: 요소의 중심점이 화면 안에 있으면 True.
        """
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
        element: WebElement,
        block: str = "center",
        timeout: float | None = None,
    ) -> WebElement:
        """이미 찾은 WebElement가 보이도록 화면을 스크롤한다.

        scrollIntoView 실행 후 요소의 중심점이 실제 브라우저 화면 안으로
        들어올 때까지 기다린다. 동적 목록에서 찾은 WebElement를 다시
        locator로 찾기 어려운 경우에도 사용할 수 있다.

        Args:
            element: 화면으로 이동시킬 WebElement.
            block: 스크롤 후 요소의 세로 위치.
                start, center, end, nearest 중 하나를 사용한다.
            timeout: 화면 안으로 들어올 때까지의 최대 대기시간.

        Returns:
            WebElement: 화면으로 스크롤한 요소.

        Raises:
            ValueError: 지원하지 않는 block 값을 전달한 경우.
            TimeoutException: 제한 시간 안에 요소 중심점이 화면에 없는 경우.
        """
        allowed_blocks = {"start", "center", "end", "nearest"}

        if block not in allowed_blocks:
            raise ValueError(f"지원하지 않는 block 값입니다: {block}")

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

        selected_timeout = self._get_timeout(timeout)
        WebDriverWait(self.driver, selected_timeout).until(
            lambda _: self._is_element_center_in_viewport(element)
        )
        return element
