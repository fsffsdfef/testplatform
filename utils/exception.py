from rest_framework.views import exception_handler
from utils.baseresponse import BaseResponse
import traceback
ERROR_CODE = {
    404: '异常测试',
    # 400: {
    #     'required': '不能为空'
    # }
}


def custom_exception_handler(exc, context):
    msg = ''
    print(f'exc: {exc}')
    view = context['view']
    re = context['request']

    print(f'ip地址为：{re.META.get("REMOTE_ADDR")}，视图为{str(view)}，请求地址：{re.path}')
    result = exception_handler(exc, context)
    # if result:
    #     for i in result.data.keys():
    #         msg = result.data[i]
    #         print(f'{i}{msg}')
    #         break
    #     result.data.clear()
    #     result.data['code'] = result.status_code
    #     if result.status_code in ERROR_CODE:
    #         result.data['msg'] = ERROR_CODE[result.status_code]
    #     else:
    #         result.data['msg'] = msg
    #     response = result
    #     print(f'sds{response}')
    # # 输出异常信息和异常出处
    # # if response is not None:
    # #     print('Exception:', response.data)
    # #     tb = traceback.format_tb(exc.__traceback__)
    # #     print('Traceback:', ''.join(tb))
    # else:
    #     response = {'error': exc}
    return result
