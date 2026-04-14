from commons.abs.baserequest import RequestStrategy, HttpRequestStrategy
from typing import Dict, Any, Optional


class RequestFactory:
    """
    请求策略类
    """

    _strategies = {
        "HTTP": HttpRequestStrategy
    }

    @classmethod
    def check_strategy(cls, strategy: str):
        """校验策略"""
        if strategy not in cls._strategies.keys():
            return False
        else:
            return True

    @classmethod
    def create_strategy(cls, request_type: str) -> RequestStrategy or Dict[str, str]:
        """创建策略实例"""
        if request_type not in cls._strategies:
            raise ValueError(f'{request_type}类型请求还未注册，请先注册')
        return cls._strategies[request_type]()

    @classmethod
    def get_available_types(cls) -> list:
        """获取可用策略"""
        return list(cls._strategies.keys())


class RequestDispense:

    def __init__(self):
        self.factory = RequestFactory()

    def send_request(self, request_type: str, data):
        try:
            strategy = self.factory.create_strategy(request_type)
            return strategy.send_action(data)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "availableTypes": self.factory.get_available_types()
            }

