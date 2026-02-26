from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Coupon
from datetime import date

class CouponValidationView(APIView):
    def post(self, request):
        code = request.data.get('code', '').strip()

        if not code:
            return Response(
                {"error": "Coupon code is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            coupon = Coupon.objects.get(code__iexact=code)  # case-insensitive
        except Coupon.DoesNotExist:
            return Response(
                {"error": "Invalid coupon code"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not coupon.is_valid_now():
            return Response(
                {"error": "Coupon is not active or has expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "valid": True,
            "code": coupon.code,
            "discount_percentage": str(coupon.discount_percentage)
        }, status=status.HTTP_200_OK)