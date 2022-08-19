from django.conf.urls import url
from django.contrib.auth import views
from rest_framework_simplejwt import views as jwt_views
from .views import signup, LoginView, ProfileDetailView, userSettings, api_login, api_getUserDetails

# TODO:
# url(r'^account_activation_sent/$', core_views.account_activation_sent, name='account_activation_sent'),
# url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
#     core_views.activate, name='activate'),

urlpatterns = [
    url(r'^login$', LoginView.as_view(), name='login'),
    url(r'^signup/$', signup, name='signup'),
    url(r'^profile$', ProfileDetailView.as_view(), name='profile'),
    url(r'^logout$', views.LogoutView.as_view(), name='logout'),
    url(r'^password_change$', views.PasswordChangeView.as_view(), name='password_change'),
    url(r'^password_change/done$', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    url(r'^password_reset$', views.PasswordResetView.as_view(), name='password_reset'),
    url(r'^password_reset/done$', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    url(r'^reset/done$', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),


    url(r'^settings$', userSettings, name='userSettings'),

    # url(r'^api/login$', api_login, name='api_login'),
    # simpleJWT
    url(r'^api/token$', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^api/token/refresh$', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    url(r'^api/user$', api_getUserDetails, name='api_getUserDetails'),
]
