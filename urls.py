from django.urls import path # type: ignore
from .views import AccountRootView, UserProfileUpdateView

urlpatterns = [
    path('', AccountRootView.as_view(), name='account-root'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),
]