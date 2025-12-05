from commons.abs.baserequest import RequestStrategy, HttpRequestStrategy
from typing import Dict, Any, Optional


class RequestFactory:
    """
    请求策略类
    """

    _strategies = {}

    @classmethod
    def register_strategy(cls, strategy: RequestStrategy):
        """注册策略"""
        cls._strategies[strategy.get_request_type()] = strategy

    @classmethod
    def create_strategy(cls, request_type: str) -> RequestStrategy or Dict[str, str]:
        """创建策略实例"""
        if request_type not in cls._strategies:
            raise ValueError(f'暂不支持{request_type}类型请求')
        return cls._strategies[request_type]

    @classmethod
    def get_available_types(cls) -> list:
        """获取可用策略"""
        return list(cls._strategies.keys())


class RequestDispense:

    def __init__(self):
        self.factory = RequestFactory()
        self._register_default_strategies()

    def _register_default_strategies(self):
        self.factory.register_strategy(HttpRequestStrategy())

    def send_request(self, request_type: str, data):
        try:
            strategy = self.factory.create_strategy(request_type)
            return strategy.send_request(data)
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "requestType": self.get_available_types()
            }

    def http_request(self, data, **kwargs) -> Dict[str, any]:
        """HTTP请求"""
        return self.send_request('HTTP', data)

    def get_available_types(self) -> list:
        """获取可用的请求类型"""
        return self.factory.get_available_types()
