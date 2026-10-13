from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q, Avg
from .models import Movie, Showtime, SeatBooking, MovieReview
from .forms import SeatBookingForm, MovieReviewForm


def movie_list(request):
    """
    Displays the catalog of movies with genre filter, search, and average rating badges.
    """
    genre = request.GET.get("genre", "").strip()
    query = request.GET.get("q", "").strip()

    movies = Movie.objects.all().prefetch_related("reviews", "showtimes")

    if genre:
        movies = movies.filter(genre__iexact=genre)

    if query:
        movies = movies.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(genre__icontains=query)
        )

    # All genres for the filter tabs/pills
    genres = [c[0] for c in Movie.GENRE_CHOICES]

    # Quick stats
    total_movies = movies.count()

    context = {
        "movies": movies,
        "genres": genres,
        "selected_genre": genre,
        "search_query": query,
        "total_movies": total_movies,
    }
    return render(request, "movies/movie_list.html", context)


def movie_detail(request, movie_id):
    """
    Displays single movie details, showtimes, community reviews, and the review submission form.
    """
    movie = get_object_or_404(Movie.objects.prefetch_related("reviews", "showtimes"), id=movie_id)
    reviews = movie.reviews.all().order_by("-created_date")
    showtimes = movie.showtimes.all().order_by("show_date", "show_time")

    # Group showtimes by date for clean Bootstrap pill navigation
    showtimes_by_date = {}
    for st in showtimes:
        date_str = st.show_date.strftime("%A, %b %d")
        if date_str not in showtimes_by_date:
            showtimes_by_date[date_str] = []
        showtimes_by_date[date_str].append(st)

    review_form = MovieReviewForm()

    context = {
        "movie": movie,
        "reviews": reviews,
        "showtimes_by_date": showtimes_by_date,
        "review_form": review_form,
    }
    return render(request, "movies/movie_detail.html", context)


def add_review(request, movie_id):
    """
    Handles review submission workflow with 1-5 star rating and comment validation.
    """
    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == "POST":
        form = MovieReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.movie = movie
            review.save()
            messages.success(
                request,
                f"Thank you, {review.reviewer_name}! Your {review.rating}★ review for '{movie.title}' was posted."
            )
        else:
            for field, errors in form.errors.items():
                for err in errors:
                    messages.error(request, f"{err}")

    return redirect("movies:movie_detail", movie_id=movie.id)


def book_seats(request, showtime_id):
    """
    Seat booking workflow: displays 5x8 seat matrix, tracks real-time selection,
    and server-side validates seat availability and total price.
    """
    showtime = get_object_or_404(
        Showtime.objects.select_related("movie"),
        id=showtime_id
    )

    booked_seats = showtime.booked_seats_list()

    # Generate the 5x8 matrix grid definition (Rows A-E, Cols 1-8)
    rows = ["A", "B", "C", "D", "E"]
    cols = [str(i) for i in range(1, 9)]
    seat_grid = []
    for r in rows:
        row_seats = []
        for c in cols:
            seat_code = f"{r}{c}"
            row_seats.append({
                "code": seat_code,
                "row": r,
                "col": c,
                "is_booked": seat_code in booked_seats
            })
        seat_grid.append({"row_label": r, "seats": row_seats})

    if request.method == "POST":
        form = SeatBookingForm(request.POST, showtime=showtime)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.showtime = showtime
            seats_list = booking.seats_list()
            booking.seat_count = len(seats_list)
            # Server-side authoritative price calculation: Never rely only on client JS calculation!
            booking.total_paid = Decimal(booking.seat_count) * showtime.ticket_price
            booking.save()

            messages.success(
                request,
                f"Booking confirmed! Your reference code is {booking.booking_reference}."
            )
            return redirect("movies:booking_confirmation", booking_reference=booking.booking_reference)
        else:
            for field, errors in form.errors.items():
                for err in errors:
                    messages.error(request, f"{err}")
    else:
        form = SeatBookingForm(showtime=showtime)

    context = {
        "showtime": showtime,
        "movie": showtime.movie,
        "booked_seats": booked_seats,
        "seat_grid": seat_grid,
        "form": form,
        "ticket_price": float(showtime.ticket_price),
        "available_seats_count": showtime.available_seats_count(),
    }
    return render(request, "movies/book_seats.html", context)


def booking_confirmation(request, booking_reference):
    """
    Displays the booked cinema ticket receipt voucher with reference code.
    """
    booking = get_object_or_404(
        SeatBooking.objects.select_related("showtime", "showtime__movie"),
        booking_reference=booking_reference
    )
    context = {
        "booking": booking,
        "showtime": booking.showtime,
        "movie": booking.showtime.movie,
    }
    return render(request, "movies/booking_confirmation.html", context)


def my_bookings(request):
    """
    Allows a customer to look up their previous ticket bookings using their email or reference code.
    """
    search_term = request.GET.get("q", "").strip()
    bookings = []
    has_searched = False

    if search_term:
        has_searched = True
        bookings = SeatBooking.objects.filter(
            Q(customer_email__iexact=search_term) |
            Q(booking_reference__iexact=search_term)
        ).select_related("showtime", "showtime__movie").order_by("-created_at")

    context = {
        "search_term": search_term,
        "bookings": bookings,
        "has_searched": has_searched,
    }
    return render(request, "movies/my_bookings.html", context)
