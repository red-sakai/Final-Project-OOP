document.addEventListener('DOMContentLoaded', function() {
    // Select all arrow elements
    const arrows = document.querySelectorAll('.arrow');
    const cardAnswers = document.querySelectorAll('.card_answer');
    
    // Add click event listener to each arrow
    arrows.forEach(function(arrow, index) {
        arrow.addEventListener('click', function() {
            // Toggle the active class on the arrow (for rotation if you want to add that in CSS)
            arrow.classList.toggle('active');
            
            // Toggle the visibility of the corresponding answer
            if (cardAnswers[index]) {
                cardAnswers[index].classList.toggle('active');
                
                // Toggle between down and up arrow image
                const arrowImg = arrow.querySelector('img');
                if (arrow.classList.contains('active')) {
                    // Change to up arrow when expanded
                    arrowImg.src = "{{ url_for('static', filename='images/angle-up-solid.svg') }}";
                } else {
                    // Change back to down arrow when collapsed
                    arrowImg.src = "{{ url_for('static', filename='images/angle-down-solid.svg') }}";
                }
            }
        });
    });
});

// modify test