from selenium.webdriver.common.by import By

from src.firefoxPages.base_page import BasePage
import logging

logger = logging.getLogger(__name__)

class FirefoxLoginPage(BasePage):
    """로그인 페이지 Page Object."""

    URL = "https://dev-qaproject-helpy-chat.dev.elicer.io/"

    def __init__(self, driver, timeout=None, action_delay=0):
        super().__init__(driver, timeout, action_delay)

    def login_with_account(self, user_id, password):
        """아이디와 비밀번호를 입력하여 로그인한다.

        Args:
            user_id: 로그인 아이디.
            password: 로그인 비밀번호.
        """
        self.open_url(self.URL)

        id_locator = (By.NAME, "loginId")
        self.fill_text(id_locator, user_id)

        self.pause_for_debugging()

        password_locator = (By.NAME, "password")
        self.fill_text(password_locator, password)

        self.pause_for_debugging()

        login_button_locator = (By.XPATH, "//button[@type='submit']")
        self.click(login_button_locator)
