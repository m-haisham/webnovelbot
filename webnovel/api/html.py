from requests import Session


class HtmlApi:
    """
    provide html pages

    to be used primarily with BaseApi.html
    """

    def __init__(self, session: Session = None):
        """
        :param session: session to use for requests
        """
        if session is None:
            self.session = Session()
        else:
            self.session = session

    def profile(self):
        """
        :return: user profile html
        """
        return self.session.get(
            f'https://www.webnovel.com/profile/{self.session.cookies.get("uid")}?appId=10'
        ).content

    def vote(self):
        """
        :return: voting page html
        """
        return self.session.get(
            'https://www.webnovel.com/vote'
        ).content
