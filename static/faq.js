document.addEventListener('DOMContentLoaded', function () {
    const arrows = document.querySelectorAll('.arrow img');
    const arrowDivs = document.querySelectorAll('.arrow');
    const cardAnswers = document.querySelectorAll('.card_answer');

    arrows.forEach((arrow, index) => {
        arrow.addEventListener('click', function () {
            const answer = cardAnswers[index];
            const arrowDiv = arrowDivs[index];
            if (answer) {
                answer.classList.toggle('active');
                answer.classList.toggle('hidden');
                arrowDiv.classList.toggle('rotated');
            }
        });
    });
});