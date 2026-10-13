/**
 * CINEVERSE - Interactive Seat Booking Matrix & Review Engine
 * Handles 5x8 seat selection, dynamic price calculation, and star rating widget.
 */

document.addEventListener("DOMContentLoaded", () => {
    initSeatSelectionMatrix();
    initStarRatingWidget();
});

/**
 * 5x8 Cinema Seat Matrix Logic
 */
function initSeatSelectionMatrix() {
    const seatButtons = document.querySelectorAll(".seat-btn:not(.booked)");
    const selectedSeatsInput = document.getElementById("id_selected_seats");
    const seatDisplayContainer = document.getElementById("selected-seats-display");
    const seatCountDisplay = document.getElementById("selected-count-display");
    const totalPriceDisplay = document.getElementById("total-price-display");
    const checkoutSubmitBtn = document.getElementById("checkout-submit-btn");
    const ticketPriceEl = document.getElementById("unit-ticket-price");

    if (!seatButtons.length || !selectedSeatsInput || !ticketPriceEl) {
        return; // Not on the seat selection page
    }

    const unitPrice = parseFloat(ticketPriceEl.dataset.price || "0");
    let selectedSeats = [];

    // Pre-populate if hidden input already has values (e.g. on validation reload)
    if (selectedSeatsInput.value.trim()) {
        selectedSeats = selectedSeatsInput.value
            .split(",")
            .map(s => s.trim().toUpperCase())
            .filter(Boolean);

        // Mark corresponding buttons
        selectedSeats.forEach(code => {
            const btn = document.querySelector(`.seat-btn[data-seat="${code}"]`);
            if (btn && !btn.classList.contains("booked")) {
                btn.classList.add("selected");
            }
        });
        updateSummary();
    }

    // Attach click listeners to available seats
    seatButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            const seatCode = btn.dataset.seat;
            if (!seatCode) return;

            if (selectedSeats.includes(seatCode)) {
                // Deselect
                selectedSeats = selectedSeats.filter(s => s !== seatCode);
                btn.classList.remove("selected");
            } else {
                // Select (maximum 8 seats per booking for safety)
                if (selectedSeats.length >= 8) {
                    alert("Maximum 8 seats can be selected per transaction.");
                    return;
                }
                selectedSeats.push(seatCode);
                btn.classList.add("selected");
            }

            // Sort seats alphabetically (e.g. A1, A2, B4)
            selectedSeats.sort((a, b) => {
                if (a[0] === b[0]) {
                    return parseInt(a.slice(1)) - parseInt(b.slice(1));
                }
                return a.localeCompare(b);
            });

            updateSummary();
        });
    });

    function updateSummary() {
        const count = selectedSeats.length;
        const total = (count * unitPrice).toFixed(2);

        // Update hidden form field
        selectedSeatsInput.value = selectedSeats.join(", ");

        // Update counts and prices in DOM
        if (seatCountDisplay) {
            seatCountDisplay.textContent = count;
        }

        if (totalPriceDisplay) {
            totalPriceDisplay.textContent = `$${total}`;
        }

        // Render seat badges/tags in sidebar
        if (seatDisplayContainer) {
            if (count === 0) {
                seatDisplayContainer.innerHTML = '<span class="text-muted fst-italic">No seats selected yet</span>';
            } else {
                seatDisplayContainer.innerHTML = selectedSeats
                    .map(seat => `<span class="seat-tag"><i class="bi bi-ticket-perforated me-1"></i>${seat}</span>`)
                    .join(" ");
            }
        }

        // Enable or disable checkout button
        if (checkoutSubmitBtn) {
            if (count > 0) {
                checkoutSubmitBtn.removeAttribute("disabled");
                checkoutSubmitBtn.classList.remove("opacity-50");
            } else {
                checkoutSubmitBtn.setAttribute("disabled", "true");
                checkoutSubmitBtn.classList.add("opacity-50");
            }
        }
    }
}

/**
 * Interactive 1-5 Star Review Rating Widget
 */
function initStarRatingWidget() {
    const starWidget = document.getElementById("star-rating-container");
    const ratingInput = document.getElementById("id_rating");
    const ratingLabel = document.getElementById("rating-caption");

    if (!starWidget || !ratingInput) return;

    const stars = starWidget.querySelectorAll(".star-item");
    const ratingTexts = {
        1: "1 Star - Poor",
        2: "2 Stars - Fair",
        3: "3 Stars - Good",
        4: "4 Stars - Great",
        5: "5 Stars - Masterpiece!"
    };

    let currentRating = parseInt(ratingInput.value || "5", 10);

    function renderStars(rating) {
        stars.forEach(star => {
            const val = parseInt(star.dataset.value, 10);
            if (val <= rating) {
                star.classList.add("bi-star-fill", "text-warning");
                star.classList.remove("bi-star", "text-secondary");
            } else {
                star.classList.add("bi-star", "text-secondary");
                star.classList.remove("bi-star-fill", "text-warning");
            }
        });
        if (ratingLabel) {
            ratingLabel.textContent = ratingTexts[rating] || `${rating} Stars`;
        }
    }

    renderStars(currentRating);

    stars.forEach(star => {
        const val = parseInt(star.dataset.value, 10);

        star.addEventListener("mouseenter", () => {
            renderStars(val);
        });

        star.addEventListener("click", () => {
            currentRating = val;
            ratingInput.value = currentRating;
            renderStars(currentRating);
        });
    });

    starWidget.addEventListener("mouseleave", () => {
        renderStars(currentRating);
    });
}
