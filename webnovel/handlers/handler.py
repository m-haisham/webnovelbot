from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from ..bot import WebnovelBot


class IHandler:
    bot: WebnovelBot
    driver: WebDriver

    def __init__(self, bot):
        self.bot = bot
        self.driver = bot.driver

        self.wait = WebDriverWait(self.driver, self.bot.timeout)

    def get(self, selector):
        return self.driver.find_element_by_css_selector(selector)

    def wait_for(self, selector):
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def wait_and_get(self, selector):
        self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

        return self.driver.find_element_by_css_selector(selector)
