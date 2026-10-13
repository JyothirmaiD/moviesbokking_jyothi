from django.contrib import admin
from .models import Movie, Showtime, SeatBooking, MovieReview


class ShowtimeInline(admin.TabularInline):
    model = Showtime
    extra = 1


class MovieReviewInline(admin.TabularInline):
    model = MovieReview
    extra = 0
    readonly_fields = ("created_date",)


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "duration_formatted", "release_date", "average_rating", "total_reviews")
    list_filter = ("genre", "release_date")
    search_fields = ("title", "description")
    inlines = [ShowtimeInline, MovieReviewInline]


@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ("movie", "show_date", "show_time", "screen_number", "ticket_price", "booked_seats_display", "available_seats_count")
    list_filter = ("show_date", "screen_number", "movie")
    search_fields = ("movie__title", "screen_number")
    ordering = ("show_date", "show_time")

    def booked_seats_display(self, obj):
        seats = obj.booked_seats_list()
        return ", ".join(seats) if seats else "None"
    booked_seats_display.short_description = "Booked Seats"


@admin.register(SeatBooking)
class SeatBookingAdmin(admin.ModelAdmin):
    list_display = ("booking_reference", "customer_name", "customer_email", "showtime", "selected_seats", "seat_count", "total_paid", "created_at")
    list_filter = ("created_at", "showtime__show_date", "showtime__movie")
    search_fields = ("booking_reference", "customer_name", "customer_email", "selected_seats")
    readonly_fields = ("booking_reference", "created_at")


@admin.register(MovieReview)
class MovieReviewAdmin(admin.ModelAdmin):
    list_display = ("movie", "reviewer_name", "rating", "created_date")
    list_filter = ("rating", "created_date", "movie")
    search_fields = ("reviewer_name", "comment", "movie__title")
    readonly_fields = ("created_date",)
