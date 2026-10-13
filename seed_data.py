"""
seed_data.py
Populates CineVerse with realistic movies, showtimes, occupied seats, and community reviews.
Run via: python seed_data.py
"""
import os
import sys
import django
from datetime import date, time, timedelta
from decimal import Decimal

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cinema_portal.settings')
django.setup()

from movies.models import Movie, Showtime, SeatBooking, MovieReview


def seed_database():
    print("🎬 Seeding CineVerse sample database...")

    # 1. Sample Movies
    movies_data = [
        {
            "title": "Interstellar: Beyond Horizon",
            "genre": "Sci-Fi",
            "duration": 169,
            "release_date": date(2024, 11, 7),
            "poster_url": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=800&auto=format&fit=crop&q=80",
            "description": "When Earth becomes uninhabitable in the near future, a farmer and ex-NASA pilot, Joseph Cooper, is tasked to pilot a spacecraft along with a team of researchers through a newly discovered wormhole to locate a new habitable home for humanity."
        },
        {
            "title": "Cyber Shadow: Neo Tokyo",
            "genre": "Action",
            "duration": 132,
            "release_date": date(2025, 3, 14),
            "poster_url": "https://images.unsplash.com/photo-1578632767115-351597cf2477?w=800&auto=format&fit=crop&q=80",
            "description": "In a rain-drenched cyberpunk metropolis ruled by rogue AI corporations, a cybernetically enhanced mercenary embarks on a high-stakes extraction mission to recover a classified neural prototype before city lockdown."
        },
        {
            "title": "The Grand Symphony",
            "genre": "Drama",
            "duration": 125,
            "release_date": date(2024, 9, 20),
            "poster_url": "https://images.unsplash.com/photo-1465847899084-d164df4dedc6?w=800&auto=format&fit=crop&q=80",
            "description": "An ambitious conductor battles personal grief, orchestra politics, and artistic perfectionism as he strives to premiere a legendary lost musical composition at the historic Vienna Concert Hall."
        },
        {
            "title": "Cosmic Odyssey: Starfall",
            "genre": "Adventure",
            "duration": 144,
            "release_date": date(2025, 1, 10),
            "poster_url": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=800&auto=format&fit=crop&q=80",
            "description": "A rogue explorer and her quirky droid companion traverse unexplored sectors of the Andromeda galaxy, uncovering ancient celestial artifacts that hold the secrets of galactic origins."
        },
        {
            "title": "Whispers in the Mist",
            "genre": "Thriller",
            "duration": 118,
            "release_date": date(2024, 10, 31),
            "poster_url": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=800&auto=format&fit=crop&q=80",
            "description": "A forensic investigator visits an isolated coastal lighthouse village to investigate mysterious ship disappearances, only to uncover a tight-lipped community guarding a centuries-old dark conspiracy."
        },
        {
            "title": "Tales of the Enchanted Forest",
            "genre": "Animation",
            "duration": 102,
            "release_date": date(2025, 2, 22),
            "poster_url": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=800&auto=format&fit=crop&q=80",
            "description": "A brave young spirit guardian and a clumsy woodland hedgehog set out on an enchanting quest across mystical glowing canopies to restore the ancient Tree of Harmony."
        }
    ]

    today = date.today()

    for m_data in movies_data:
        movie, created = Movie.objects.get_or_create(
            title=m_data["title"],
            defaults=m_data
        )
        if created:
            print(f"  + Added Movie: {movie.title}")

        # 2. Showtimes for each movie across 3 days
        screens = [
            ("Screen 1 - IMAX Laser", Decimal("16.50")),
            ("Screen 2 - Dolby Atmos", Decimal("14.00")),
            ("Screen 3 - VIP Luxe", Decimal("19.00")),
        ]

        show_times_list = [time(14, 0), time(17, 30), time(20, 45)]

        for day_offset in range(3):
            show_date = today + timedelta(days=day_offset)
            for idx, (screen_name, price) in enumerate(screens):
                st_time = show_times_list[idx % len(show_times_list)]
                showtime, st_created = Showtime.objects.get_or_create(
                    movie=movie,
                    show_date=show_date,
                    show_time=st_time,
                    screen_number=screen_name,
                    defaults={"ticket_price": price}
                )

                # 3. Add sample bookings on selected showtimes to showcase occupied seats in the 5x8 matrix!
                if day_offset == 0 and idx == 0 and not showtime.bookings.exists():
                    # Pre-book some seats (A3, A4, B5, C1, C2)
                    booking1 = SeatBooking.objects.create(
                        showtime=showtime,
                        customer_name="Alex Turner",
                        customer_email="alex.turner@example.com",
                        customer_phone="+1 555-0192",
                        selected_seats="A3, A4",
                        seat_count=2,
                        total_paid=Decimal("2") * price,
                    )
                    booking2 = SeatBooking.objects.create(
                        showtime=showtime,
                        customer_name="Sophia Martinez",
                        customer_email="sophia.m@example.com",
                        customer_phone="+1 555-0843",
                        selected_seats="C1, C2, C3",
                        seat_count=3,
                        total_paid=Decimal("3") * price,
                    )
                    print(f"    * Created demo bookings ({booking1.booking_reference}, {booking2.booking_reference}) for {showtime}")

        # 4. Community Reviews
        if not movie.reviews.exists():
            sample_reviews = [
                {
                    "reviewer_name": "Marcus Vance",
                    "rating": 5,
                    "comment": "An absolute cinematic masterpiece! The sound design and visuals on the IMAX screen were unbelievable. A must-watch experience."
                },
                {
                    "reviewer_name": "Elena Rostova",
                    "rating": 4,
                    "comment": "Engaging storyline with stellar performances. Pacing slowed a little in the second act, but the climax completely made up for it."
                },
                {
                    "reviewer_name": "David Kim",
                    "rating": 5,
                    "comment": "The world-building and character dynamics kept me on the edge of my seat. Highly recommended to everyone!"
                }
            ]
            for r_data in sample_reviews:
                MovieReview.objects.create(
                    movie=movie,
                    reviewer_name=r_data["reviewer_name"],
                    rating=r_data["rating"],
                    comment=r_data["comment"]
                )
            print(f"    * Added sample reviews for {movie.title}")

    print("🎉 Database seeding completed successfully!")


if __name__ == '__main__':
    seed_database()
