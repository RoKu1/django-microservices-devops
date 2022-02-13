from django.urls import path
from .views import MyObtainTokenPairView, UserViewSet, MyTokenRefreshView, signup, SignupVerify, forgotpassword, changepassword, status

urlpatterns = [
    path('user/status/', status, name='check_status'),
    path('user/token/', MyObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('user/tokenrefresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('user/signup/', signup, name='signup'),
    path('user/signupverify/', SignupVerify.as_view(), name='signupverify'),
    path('user/forgot/', forgotpassword, name='forgot_pswd'),
    path('user/changepassword/', changepassword, name='chnge_pswd'),
    path('user/upsert/', UserViewSet.as_view({'get': 'retrieve', 'put': 'partial_update',
                                             'delete': 'destroy'}), name='user_actions'),
]
