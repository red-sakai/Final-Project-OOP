document.addEventListener("DOMContentLoaded", function () {
    const dateInput = document.getElementById('schedule');
    if (dateInput) {
        const today = new Date();
        const minDateObj = new Date(today);
        minDateObj.setDate(today.getDate() + 2);
        const yyyy = minDateObj.getFullYear();
        const mm = String(minDateObj.getMonth() + 1).padStart(2, '0');
        const dd = String(minDateObj.getDate()).padStart(2, '0');
        const minDate = `${yyyy}-${mm}-${dd}`;
        dateInput.min = minDate;
        dateInput.removeAttribute('max');
    }
});
