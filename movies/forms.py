from django import forms
from .models import SeatBooking, MovieReview, Showtime


VALID_ROWS = {"A", "B", "C", "D", "E"}
VALID_COLS = {str(i) for i in range(1, 9)}


class SeatBookingForm(forms.ModelForm):
    """
    Form to capture customer details and selected seats for a showtime.
    Implements robust server-side validation against double-booking and invalid seats.
    """
    selected_seats = forms.CharField(
        widget=forms.HiddenInput(attrs={"id": "id_selected_seats"}),
        error_messages={"required": "Please select at least one seat from the matrix."}
    )

    class Meta:
        model = SeatBooking
        fields = ["customer_name", "customer_email", "customer_phone", "selected_seats"]
        widgets = {
            "customer_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter your full name",
                "required": True,
            }),
            "customer_email": forms.EmailInput(attrs={
                "class": "form-control",
                "placeholder": "name@example.com",
                "required": True,
            }),
            "customer_phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "+1 (555) 000-0000 (Optional)",
            }),
        }

    def __init__(self, *args, **kwargs):
        self.showtime = kwargs.pop("showtime", None)
        super().__init__(*args, **kwargs)

    def clean_selected_seats(self):
        seats_str = self.cleaned_data.get("selected_seats", "").strip()
        if not seats_str:
            raise forms.ValidationError("You must select at least one seat.")

        # Split and clean seat codes
        seat_codes = [s.strip().upper() for s in seats_str.split(",") if s.strip()]
        if not seat_codes:
            raise forms.ValidationError("No valid seat selections found.")

        # Remove duplicates within the submission
        unique_seats = list(dict.fromkeys(seat_codes))

        # Validate that seat codes exist in the 5x8 matrix (A1 to E8)
        for seat in unique_seats:
            if len(seat) < 2 or seat[0] not in VALID_ROWS or seat[1:] not in VALID_COLS:
                raise forms.ValidationError(
                    f"'{seat}' is not a valid seat in the 5x8 matrix. Valid seats are A1-E8."
                )

        # Server-side concurrency & double-booking check against showtime's existing bookings
        if self.showtime:
            already_booked = set(self.showtime.booked_seats_list())
            conflicts = set(unique_seats).intersection(already_booked)
            if conflicts:
                conflict_list = ", ".join(sorted(conflicts))
                raise forms.ValidationError(
                    f"Seat(s) {conflict_list} were just booked by someone else! Please choose different seats."
                )

        return ", ".join(unique_seats)


class MovieReviewForm(forms.ModelForm):
    """
    Form for community movie review submission with 1-5 star rating.
    """
    rating = forms.IntegerField(
        min_value=1,
        max_value=5,
        widget=forms.HiddenInput(attrs={"id": "id_rating", "value": "5"}),
        error_messages={
            "min_value": "Rating must be at least 1 star.",
            "max_value": "Rating cannot exceed 5 stars.",
            "required": "Please provide a star rating from 1 to 5.",
        }
    )

    class Meta:
        model = MovieReview
        fields = ["reviewer_name", "rating", "comment"]
        widgets = {
            "reviewer_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Your name or screen nickname",
                "required": True,
            }),
            "comment": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "What did you think of the storyline, directing, performances, and visuals?",
                "rows": 4,
                "required": True,
            }),
        }
