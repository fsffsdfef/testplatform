from typing import Dict, List, Any, Tuple, Type
from django.db import transaction
from django.db.models import Model, QuerySet
from commons.cusntom.response import CustomResponse


class UniversalBatchOperator:

    def __init__(self,
                 model_class: Type[Model],
                 primary_data: List[Dict[str, Any]],
                 primary_key_field: str = 'id',
                 action_type=None):
        self.model = model_class
        self.data = primary_data
        self.primary_key_field = primary_key_field
        self.action_type = action_type

    def batch(self):
        action_list = ['create', 'update', 'del']
        if self.action_type is None or self.action_type not in action_list:
            return {"msg": "暂不支持该批量操作", "success": False, "code": "4444"}
        action = {
            "create": self._batch_create,
            "update": self._batch_update,
            "del": self._batch_del
        }
        return action[self.action_type]()

    def _batch_create(self):
        try:
            objects = []
            # objects = [self.model(**item) for item in self.data]
            for item in self.data:
                if not item.get(self.primary_key_field):
                    temp_obj = self.model(**item)
                    if hasattr(temp_obj, "get_random_number"):
                        index_id = temp_obj.get_random_number(
                            self.primary_key_field,
                            None,
                            None,
                            1000,
                            9999)
                        item[self.primary_key_field] = index_id
                    objects.append(self.model(**item))
            with transaction.atomic():
                created = self.model.objects.bulk_create(objects, batch_size=100)
            return {"msg": f"创建成功{created}", "success": True, "code": "555"}
        except Exception as e:
            return {"msg": f"创建失败，{e}", "success": False, "code": "555"}

    @staticmethod
    def _batch_update(data: List[Dict[str, Any]], model: Model, index_id):
        try:
            ids = [item.get(index_id) for item in data if item.get(index_id)]
            query_params = {f"{index_id}__in": ids}
            objects = model.objects.filter(**query_params)

        except Exception as e:
            return e

    def _batch_del(self):
        pass

