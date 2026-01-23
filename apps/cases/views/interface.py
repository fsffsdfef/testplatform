from rest_framework.generics import GenericAPIView
from django.db.models import Q
from ..sers.interface_case_ser import *
from commons.cusntom.view import CustomView
from commons.cusntom.pagination import CustomPage
from commons.cusntom.response import CustomResponse


class InterfaceView(CustomView):

    model = HttpCaseModel
    serializer_class = HttpCaseSer
    permission_classes = []
    pagination_class = CustomPage
    fields = {
        "caseId": {
            "type": 'exact',
            "converter": int,
            "allow_empty": False
        },
        "caseName": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": True
        },
        "portId": {
            "type": 'icontains',
            "converter": int,
            "allow_empty": True,
            'related_field': 'port__portId',
            'related_lookup_type': 'icontains'
        },
        "portName": {
            "type": 'icontains',
            "converter": str,
            "allow_empty": True,
            'related_field': 'port__portName',
            'related_lookup_type': 'icontains'
        }
    }
    index_key = "caseId"

    def delete(self, request, *args, **kwargs):
        case_id = request.get('caseId')
        ids = request.get('ids', [])
        if case_id:
            obj = self.model.objects.get(caseId=case_id)
            suit_rel = obj.suit.all().values('suitName', 'suitId')
            suit_list = list()
            if suit_rel is not None:
                for suit in suit_rel:
                    suit_list.append(suit['suitName'])
            if len(suit_list) > 0:
                return CustomResponse(data=[], msg=f"{suit_list}套件正在使用，不可删除", code=101, success=False)
            else:
                return super().delete(request, *args, **kwargs)
        if len(ids) > 0:
            case_objs = self.model.objects.filter(caseId__in=ids)
            case_objs_with_suits = case_objs.prefetch_related('suit')
            # 收集所有关联的套件
            all_suit_info = []
            blocking_cases = []

            for case in case_objs_with_suits:
                # 获取该用例关联的所有套件
                related_suits = case.suit.all()
                if related_suits.exists():
                    # 收集套件信息
                    suit_info = [{'suitName': suit.suitName, 'suitId': suit.suitId} for suit in related_suits]
                    all_suit_info.extend(suit_info)
                    # 记录哪些用例被关联了
                    blocking_cases.append(case.caseId)

            if all_suit_info:
                # 去重并生成友好的错误信息
                unique_suits = {}
                for suit in all_suit_info:
                    key = (suit['suitId'], suit['suitName'])
                    if key not in unique_suits:
                        unique_suits[key] = suit

                suit_names = [suit['suitName'] for suit in unique_suits.values()]
                blocking_case_str = ', '.join(map(str, blocking_cases))

                return CustomResponse(
                    data=[],
                    msg=f"用例 [{blocking_case_str}] 被套件 [{', '.join(suit_names)}] 使用中，不可删除",
                    code=101,
                    success=False
                )
            else:
                # 没有关联套件，执行批量删除
                deleted_count, _ = case_objs.delete()
                return CustomResponse(
                    data={'deleted_count': deleted_count},
                    msg=f"成功删除 {deleted_count} 个用例",
                    code=100,
                    success=True
                )
        else:
            return super().delete(request, *args, **kwargs)


httpcase_view = InterfaceView.as_view()
