from selenium.webdriver.common.by import By
from src.firefoxPages.base_page import BasePage
import logging

logger = logging.getLogger(__name__)

class FirefoxMakeAgent(BasePage):
    """AI 에이전트 생성 페이지(Page Object)."""
    
    def __init__(self, driver, timeout=None, action_delay=0):
        super().__init__(driver, timeout, action_delay)

    def click_agent_plus_menu(self, close_menu = True):
        """에이전트 생성(+) 메뉴를 클릭한다.

        Args:
            close_menu (bool): True이면 메뉴를 연 뒤 바깥 영역을 클릭하여
                메뉴를 닫는다.
        """
        plus_locator = (
            By.XPATH,
            "//button[.//*[contains(@class, 'MuiAvatar-circular')]"
            "and .//*[contains(@data-testid, 'plusIcon')]]"
        )
        self.click(plus_locator)

        self.pause_for_debugging()

        if close_menu:
            hidden_locator = (
                By.XPATH,
                "//div[contains(@class, 'MuiModal-backdrop')]"
            )
            self.click(hidden_locator)

    
    def input_agent_name(self, agent_name):
        """에이전트 이름을 입력한다.

        Args:
            agent_name (str): 입력할 에이전트 이름.
        """
        name_locator = (
            By.NAME,
            "name"
        )
        self.click(name_locator)

        # 설명란 클릭은 TC 확인을 위해 구현
        description_locator = (
            By.XPATH,
            "//input[@name = 'description']"
        )
        self.pause_for_debugging()

        self.click(description_locator)

        self.pause_for_debugging()

        self.fill_text(name_locator, agent_name)
        

    def input_agent_description(self, description):
        """에이전트 설명을 입력한다.

        Args:
            description (str): 입력할 에이전트 설명.
        """
        description_locator = (
            By.XPATH,
            "//input[@name = 'description']"
        )
        self.click(description_locator)

        self.fill_text(description_locator, description)
    
    def select_agent_category(self, agent_category_index = 0):
        """에이전트 카테고리를 선택한다.

        Args:
            category_index (int): 선택할 카테고리의 인덱스.
        """
        category_box_locator = (
            By.ID,
            "agent-builder-purpose",
        )

        category_list_locator = (
            By.XPATH,
            "//ul[@aria-labelledby='agent-builder-purpose-label']"
            "//li[@role='option']"
        )

        self.click(category_box_locator)

        self.pause_for_debugging()

        self.click_from_list(category_list_locator, agent_category_index)

        self.pause_for_debugging()

    def input_agent_rule(self, rules):
        """에이전트의 규칙을 입력한다.

        Args:
            rules (str): 입력할 규칙
        """
        rule_area_locator = (
            By.NAME,
            "systemPrompt"
        )      

        self.click(rule_area_locator)

        self.pause_for_debugging()
        
        # TC 동작 확인용 설명란 클릭
        description_locator = (
            By.XPATH,
            "//input[@name = 'description']"
        )

        self.click(description_locator)
 
        self.pause_for_debugging()
        
        self.fill_text(rule_area_locator, rules)

    def input_agent_conversation_starters(self, greetings):
        """에이전트의 시작 대화를 입력한다.

        Args:
            greetings (str): 설정할 시작 대화
        """   
        greeting_index = 0

        greeting_locator = (
            By.XPATH,
            f"//input[@name = 'conversationStarters.{greeting_index}.value']"
        )


        self.click(greeting_locator)

        self.pause_for_debugging()

        self.fill_text(greeting_locator, greetings)

        self.pause_for_debugging()

    def scroll_make_agent_page(self):
        """에이전트 만들기 페이지의 스크롤을 이동시킨다."""
        scroll_locator = (
            By.XPATH,
            "//*[normalize-space()='기능']"
        )

        self.scroll_into_view(scroll_locator)
    
    def send_preview_message(self, message):
        """에이전트 미리보기에 메시지를 전송한다.
        
        Args:
            message: 전송할 메시지
        """
        input_locator = (
            By.XPATH,
            "//div[.//p[normalize-space()='미리보기']]"
            "//textarea[@name='input']"
            )
        visible_input = self.wait_for_first_visible(input_locator)

        visible_input.send_keys(message)
        

        self.pause_for_debugging()

        send_button_locator = (
            By.XPATH,
            "//div[.//p[normalize-space()='미리보기']]"
            "//button[@aria-label='보내기']"
        )

        visible_button = self.wait_for_first_visible(send_button_locator)

        visible_button.click()

        # input_locator = ( 
        #     By.XPATH, 
        #     "//p[normalize-space()='미리보기']"
        #     "/following::textarea[@name='input'][1]" )
        # self.fill_text(input_locator, message)


    def click_make_agent(self):
        """에이전트 만들기 버튼을 클릭한다"""
        make_button_locator = (
            By.XPATH,
            "//button[normalize-space()='만들기' and "
            "contains(@class, 'MuiLoadingButton-root')]"   
        )
        self.pause_for_debugging()

        self.click(make_button_locator)
    
        
    