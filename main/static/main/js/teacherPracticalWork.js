// timeSlots.js

document.addEventListener('DOMContentLoaded', function () {
    // Выбрать все слоты в день
    document.querySelectorAll('.select-all-day').forEach(button => {
        button.addEventListener('click', function () {
            const day = this.dataset.day;
            document.querySelectorAll(`input[name="time_slots"][value^="${day}_"]`).forEach(checkbox => {
                checkbox.checked = true;
            });
        });
    });

    // Выбрать слоты до 15:55
    document.querySelectorAll('.select-before-1555').forEach(button => {
        button.addEventListener('click', function () {
            const day = this.dataset.day;
            const earlyTimes = ['08:30', '10:15', '12:00', '14:10', '15:55'];

            document.querySelectorAll(`input[name="time_slots"][value^="${day}_"]`).forEach(checkbox => {
                const time = checkbox.value.split('_')[1];
                checkbox.checked = earlyTimes.includes(time);
            });
        });
    });

    document.querySelectorAll('.reset-day').forEach(button => {
        button.addEventListener('click', function () {
            const day = this.dataset.day;
            document.querySelectorAll(`input[name="time_slots"][value^="${day}_"]`).forEach(checkbox => {
                checkbox.checked = false;  // Снимаем все галочки
            });
        });
    });
});