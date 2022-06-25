from sre_constants import SUCCESS
from django.urls import path

from web.forms import LoginForm
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view
from .forms import ChangePasswordForm, LoginForm, ResetPasswordForm , PasswordForm



urlpatterns = [
    path('', views.ProductView.as_view(), name='home'),
    path('product-detail/<int:id>',views.ProductDetail.as_view(), name='product_detail'),
    path('mobiles', views.mobile, name='mobiles'),
    path('top-wear', views.topwear, name='top-wear'),
    path('bottom-wear', views.bottomwear, name='bottom-wear'),
    path('signup',views.Registration.as_view(), name = 'signup'),
    path('account/login/', auth_view.LoginView.as_view(template_name='login.html', authentication_form=LoginForm), name='login'),
    path('logout/',auth_view.LogoutView.as_view(next_page='login'), name='logout'),
    path('profile/', views.Profile.as_view(), name='profile'),
    path('address/', views.address, name='address'),
    path('add-to-cart/', views.addtocart, name='addtocart'),
    path('cart/', views.showcart, name='cart'),
    path('pluscart/', views.plus_Cart),
    path('minuscart/', views.minus_Cart),
    path('removecart/', views.remove_cart),
    path('checkout/', views.checkout, name='checkout'),
    path('paymentdone/',views.paymentdone, name='paymentdone'),
    path('order/', views.order,name='order'),

    path('passwordchange/', auth_view.PasswordChangeView.as_view(template_name='passchange.html', form_class=ChangePasswordForm, success_url='/'), name='passwordchange'),

    path('password-reset/', auth_view.PasswordResetView.as_view(template_name='passwordreset.html', form_class=ResetPasswordForm), name='password-reset'),
    path('password-reset/done/', auth_view.PasswordResetDoneView.as_view(template_name='passwordreset_done.html'), name='password-reset-done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_view.PasswordResetConfirmView.as_view(template_name='passwordreset_confirm.html', form_class=PasswordForm), name='password-reset-confirm'),
    path('password-reset-complete/', auth_view.PasswordResetCompleteView.as_view(template_name='passwordreset_complete.html'), name='password-reset-complete'),
] + static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
