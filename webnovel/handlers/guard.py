from selenium.common.exceptions import NoSuchElementException

from .handler import IHandler
from ..bot import GUARD_URL
from ..decorators import chainable


class GuardHandler(IHandler):
    def __init__(self, bot):
        """
        :param bot: webnovel bot
        :raises ValueError: if current url is not a guard url
        """
        super(GuardHandler, self).__init__(bot)

        if not self.driver.current_url.startswith(GUARD_URL):
            raise ValueError('current page is not a guard')

        # make sure its fully loaded
        self.wait_for('.codeInfo > input')

        self.input_element = self.get('.codeInfo > input')
        self.confirm_buttom = self.get('#checkTrust')
        self.resend_button = self.get('#resTrustEmail')
        self.back_button = self.get('.m-main-hd a')

    @chainable
    def input(self, code: str):
        """
        inputs code into authentication input field

        :param code: authentication code
        """
        self.input_element.send_keys(code)

    @chainable
    def confirm(self):
        """ press confirm button """
        self.confirm_buttom.click()

    @chainable
    def resend(self):
        """ press resend email button """
        self.resend_button.click()

    def back(self):
        """ press back button """
        self.back_button.click()

    def wait_until_confirmed(self):
        self.wait.until(lambda driver: (
                not self.driver.current_url.startswith(GUARD_URL)
                or self.driver.find_elements_by_css_selector('.error_tip._on')
        ))

        try:
            self.get('.error_tip._on')
        except NoSuchElementException:
            return True
        else:
            return False
