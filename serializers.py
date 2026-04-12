from rest_framework import serializers # pyright: ignore[reportMissingImports]
from django.contrib.auth.models import User # type: ignore

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Only include fields that are safe for the user to edit
        fields = ['first_name', 'last_name', 'email']


