from rest_framework import generics, permissions # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from .serializers import UserProfileSerializer


class AccountRootView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        return Response({
            'message': 'Account API root',
            'endpoints': {
                'profile_update': '/api/accounts/profile/update/'
            }
        })


class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # This ensures the user can only update THEIR own profile
        return self.request.user