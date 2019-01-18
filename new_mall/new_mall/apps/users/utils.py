from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from users.models import User


def jwt_response_payload_handler(token,user=None,request=None):
    '''
    自定义jwt认证成功反回数据
    '''

    return {
        'token':token,
        'user_id':user.id,
        'username':user.username
    }

class UsernameMobileAuthBachend(ModelBackend):
    '''判断手机号(用户名)是否正确'''
    # 2.获取参数,
    # 3.判断传入的是用户名或则手机号任意一个
    # 4.校验通过,判断密码是否正确
    # 5.返回用户信息
    def authenticate(self,request,username=None,password=None,**kwargs):
        '''判断用户名或则密码是否正确'''
        query_set = User.objects.filter(Q(username=username)|Q(mobile=username))

        try:
            if query_set.exists(): #返回True表示有

                #取出唯一一条数据,没有则报错
                user = query_set.get()

                if user.check_password(password): #判断密码是否正确

                    return user
        except:

            return None

