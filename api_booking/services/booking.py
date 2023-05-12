from typing import List

from api_booking.models import Booking, BookingItem


class BookingService:
    @classmethod
    def create(cls, booking_data: dict) -> Booking:
        data_booking_items = booking_data.pop("booking_items", [])
        booking_items: List[BookingItem] = []
        booking = Booking(**booking_data)
        booking.save()

        for _booking_item_data in data_booking_items:
            booking_items.append(
                BookingItem(
                    booking_id=booking.id,
                    **_booking_item_data
                )
            )

        BookingItem.objects.bulk_create(booking_items)

        return booking

    @classmethod
    def create_payment_order(cls, booking: Booking):
        pass
