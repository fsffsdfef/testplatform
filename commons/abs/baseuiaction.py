from playwright.sync_api import sync_playwright


class uiAction(object):

    def __init__(self, page):
        self.browser = sync_playwright().chromium.launch(headless=False)
        self.page = page

    def open_url(self, url):
        """打开页面"""
        return self.page.goto(url)

