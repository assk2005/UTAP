from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import custom_logout
from accounts.views import CustomLoginView

urlpatterns = [

    # ================= AUTHENTICATION =================

    path('login/', CustomLoginView.as_view(), name='login'),

    path('logout/', custom_logout, name='logout'),

    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html',
             email_template_name='registration/password_reset_email.html',
             success_url='/password-reset/done/'
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/reset/done/'
         ),
         name='password_reset_confirm'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # ================= ACCOUNTS APP =================

    path('', include('accounts.urls')),

    # ================= ADMIN =================

    path('admin/', admin.site.urls),

    # ================= JWT API =================

    path('api/login/',
         TokenObtainPairView.as_view(),
         name='token_obtain_pair'),

    path('api/token/refresh/',
         TokenRefreshView.as_view(),
         name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)