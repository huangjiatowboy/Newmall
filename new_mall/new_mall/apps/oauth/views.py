from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework_jwt.settings import api_settings

from oauth.models import OAuthQQUser


# oauth/qq/authorization/
from oauth.serializers import QQUserSerializer


class QQAuthURLView(APIView):
    '''提供QQ登录页面网址'''

    def get(self,request):
        #next表示从那个页面进入到的登录页面,将来登录成功后,就自动跳转到那一个页面
        next = request.query_params.get('next')

        if not next:
            next = '/' #首页

        oauth = OAuthQQ(
            client_id=settings.QQ_CLIENT_ID,
            client_secret=settings.QQ_CLIENT_SECRET,
            redirect_uri=settings.QQ_REDIRECT_URI,
            state=next
        )

        login_url = oauth.get_qq_url()

        return Response({'login_url':login_url})

# oauth/qq/user/
class QQUserView(APIView):
    '''用户QQ登录回调处理'''

    def get(self,request):

        #提取code请求参数
        code = request.query_params.get('code')

        if not code:

            return Response({'message':'缺少code'},status=status.HTTP_400_BAD_REQUEST)

        #创建工具对象
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)

        try:
            #使用code向服务器请求access_token
            access_token = oauth.get_access_token(code)

            #使用access_token获取openid
            openid = oauth.get_open_id(access_token)


        except Exception:

            return Response({'message': 'QQ服务异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 使用openid查询该QQ用户是否在美多商商城中板顶过用户
        try:

            oauth_user = OAuthQQUser.objects.get(openid=openid)

        except OAuthQQUser.DoesNotExist:

            #如果用户不存在,则先创建在绑定
            # openid = generate_encrypted_openid(openid)
            return Response({'openid':openid})

        else:
            #到此处表示登录成功
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

            #获取oauth_user关联user

            user = oauth_user.user

            payload = jwt_payload_handler(user)

            token = jwt_encode_handler(payload)

            response = Response({
                'token': token,
                'user_id': user.id,
                'username': user.username
            })

            return response

    def post(self,request):
        #绑定QQ

        user_serializer = QQUserSerializer(data=request.data)
        #校验请求参数
        user_serializer.is_valid(raise_exception=True)
        #保定openid和美多用户
        user = user_serializer.save()

        #绑定功能实现,接下来生成jwt返回
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        response = Response({
            'token': token,
            'user_id': user.id,
            'username': user.username
        })

        return response

