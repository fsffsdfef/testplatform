import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class RequestUtil(object):

    sess = requests.session()

    def __init__(self, url, method, method_type):
        self.method_type = method_type
        self.url = url
        self.method = method

    def get_adapter(self, total):
        retries = Retry(total=total, backoff_factor=1, status_forcelist=[500, 502, 503, 504],
                        allowed_methods=frozenset(["GET", "POST"]))
        adapter = HTTPAdapter(max_retries=retries)
        return adapter

    def batch_send(self, cases):
        pass

    def send(self, case_info):
        express_item_date = case_info.pop('expressItem', None)
        time_out = case_info.pop('timeOut', 3)
        retries = case_info.pop('retries', 0)
        if retries == 0:
            self.sess.mount(self.method_type, self.get_adapter(total=retries))
        res = self.sess.request(url=self.url, method=self.method, **case_info, timeout=time_out)
        return res.json()
