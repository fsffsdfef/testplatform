import requests


class RequestUtil(object):

    sess = requests.session()

    def __init__(self, case_info):
        self.case_info = case_info

    def batch_send(self):
        pass

    def send(self):
        res = self.sess.request(**self.case_info)
        return res.json()
