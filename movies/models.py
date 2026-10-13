import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Movie(models.Model):
    """
    Represents a movie available for viewing and review in the portal.
    """
    GENRE_CHOICES = [
        ("Action", "Action"),
        ("Sci-Fi", "Sci-Fi"),
        ("Drama", "Drama"),
        ("Comedy", "Comedy"),
        ("Romance", "Romance"),
        ("Horror", "Horror"),
        ("Animation", "Animation"),
        ("Thriller", "Thriller"),
        ("Adventure", "Adventure"),
    ]

    title = models.CharField(max_length=200)
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES, default="Action")
    duration = models.PositiveIntegerField(help_text="Duration in minutes (e.g. 148)")
    release_date = models.DateField()
    poster_url = models.URLField(max_length=500, help_text="Direct URL to movie poster image")
    description = models.TextField()

    class Meta:
        ordering = ["-release_date", "title"]

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        """Calculates the average rating from community reviews."""
        avg = self.reviews.aggregate(Avg("rating"))["rating__avg"]
        return round(avg, 1) if avg is not None else 0.0

    @property
    def total_reviews(self):
        """Returns total review count."""
        return self.reviews.count()

    @property
    def duration_formatted(self):
        """Formats minutes into human-readable e.g. 2h 28m."""
        hours = self.duration // 60
        mins = self.duration % 60
        if hours > 0:
            return f"{hours}h {mins}m"
        return f"{mins}m"

    @property
    def integer_rating(self):
        """Returns the floor integer of the average rating for star display."""
        return int(self.average_rating)

    @property
    def has_half_star(self):
        """Whether there's a fractional rating >= 0.5."""
        return (self.average_rating - int(self.average_rating)) >= 0.5


class Showtime(models.Model):
    """
    Represents a specific screening of a movie in a specific screen at a given date/time.
    """
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="showtimes")
    show_date = models.DateField()
    show_time = models.TimeField()
    ticket_price = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("12.50"))
    screen_number = models.CharField(max_length=50, default="Screen 1 - IMAX")

    class Meta:
        ordering = ["show_date", "show_time"]
        unique_together = ("movie", "show_date", "show_time", "screen_number")

    def __str__(self):
        return f"{self.movie.title} | {self.show_date} {self.show_time.strftime('%I:%M %p')} ({self.screen_number})"

    def booked_seats_list(self):
        """
        Gathers all individual seat codes (e.g. ['A1', 'A2']) booked for this showtime.
        """
        booked_set = set()
        for booking in self.bookings.all():
            for seat in booking.seats_list():
                if seat:
                    booked_set.add(seat.strip().upper())
        return sorted(list(booked_set))

    def available_seats_count(self):
        """Total capacity is 40 seats (5 rows x 8 cols = 40)."""
        total_capacity = 40
        return max(0, total_capacity - len(self.booked_seats_list()))


class SeatBooking(models.Model):
    """
    Stores ticket reservations for a showtime with customer info, selected seats, and total paid.
    """
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE, related_name="bookings")
    customer_name = models.CharField(max_length=150)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=20, blank=True)
    selected_seats = models.CharField(
        max_length=255,
        help_text="Comma-separated list of booked seats (e.g. A1, A2, B4)"
    )
    seat_count = models.PositiveIntegerField(default=1)
    total_paid = models.DecimalField(max_digits=8, decimal_places=2)
    booking_reference = models.CharField(max_length=20, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Ref: {self.booking_reference} - {self.customer_name} ({self.selected_seats})"

    def seats_list(self):
        """Parses the comma-separated selected_seats string into a Python list."""
        if not self.selected_seats:
            return []
        return [s.strip().upper() for s in self.selected_seats.split(",") if s.strip()]

    def save(self, *args, **kwargs):
        # Auto-generate unique booking reference if not provided
        if not self.booking_reference:
            ref = f"TKT-{uuid.uuid4().hex[:8].upper()}"
            while SeatBooking.objects.filter(booking_reference=ref).exists():
                ref = f"TKT-{uuid.uuid4().hex[:8].upper()}"
            self.booking_reference = ref
        super().save(*args, **kwargs)


class MovieReview(models.Model):
    """
    Community reviews and 1-5 star ratings for movies.
    """
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="reviews")
    reviewer_name = models.CharField(max_length=120)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Star rating from 1 to 5",
        choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)]
    )
    comment = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_date"]

    def __str__(self):
        return f"{self.reviewer_name} ({self.rating}★) on {self.movie.title}"
