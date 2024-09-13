from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from django_test_app.bookings.models import Booking
from django_test_app.bookings.serializers import BookingSerializer


# Create your views here.
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = (IsAuthenticated,)
