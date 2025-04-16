// Функция для форматирования номера телефона
const formatPhoneNumber = (value) => {
    // Убираем все нецифровые символы, кроме "+"
    let cleaned = ('' + value).replace(/\D/g, '');

    // Проверяем, начинается ли номер с 7 или +7
    if (!cleaned.startsWith('7') && !cleaned.startsWith('+7')) {
        cleaned = '7' + cleaned; // Добавляем 7, если её нет
    }

    // Ограничиваем длину номера (максимум 11 цифр, включая +7)
    if (cleaned.length > 11) {
        cleaned = cleaned.substring(0, 11);
    }

    // Форматируем номер
    let formatted = '+7';
    if (cleaned.length > 1) {
        formatted += ' (' + cleaned.substring(1, 4);
    }
    if (cleaned.length > 4) {
        formatted += ') ' + cleaned.substring(4, 7);
    }
    if (cleaned.length > 7) {
        formatted += '-' + cleaned.substring(7, 9);
    }
    if (cleaned.length > 9) {
        formatted += '-' + cleaned.substring(9, 11);
    }

    return formatted;
};

// Обработка номера телефона
document.addEventListener('DOMContentLoaded', function () {
    const phoneInput = document.getElementById('phone_number');
    const registrationForm = document.getElementById('registrationForm');
    const editProfileForm = document.getElementById('editProfileForm');

    // Создаем контейнер для ошибок, если его нет
    let phoneErrorContainer = document.getElementById('phone-errors');
    if (!phoneErrorContainer) {
        phoneErrorContainer = document.createElement('div');
        phoneErrorContainer.id = 'phone-errors';
        phoneErrorContainer.classList.add('phone-error-container');
        phoneInput.closest('.mb-3').appendChild(phoneErrorContainer);
    }

    // Функция форматирования номера
    const formatPhoneNumber = (value) => {
        let cleaned = value.replace(/\D/g, ''); // Убираем все нецифровые символы

        if (!cleaned.startsWith('7')) {
            cleaned = '7' + cleaned; // Добавляем 7, если её нет
        }

        if (cleaned.length > 11) {
            cleaned = cleaned.substring(0, 11);
        }

        let formatted = '+7';
        if (cleaned.length > 1) formatted += ' (' + cleaned.substring(1, 4);
        if (cleaned.length > 4) formatted += ') ' + cleaned.substring(4, 7);
        if (cleaned.length > 7) formatted += '-' + cleaned.substring(7, 9);
        if (cleaned.length > 9) formatted += '-' + cleaned.substring(9, 11);

        return formatted;
    };

    // Функция валидации номера
    function validatePhoneNumber() {
        const rawValue = phoneInput.value.replace(/\D/g, ''); // Убираем всё, кроме цифр
        phoneErrorContainer.innerHTML = ''; // Очистка ошибок

        if (rawValue.length < 11) {
            phoneErrorContainer.textContent = "Номер телефона должен содержать 11 цифр.";
            return false;
        }
        return true;
    }

    if (phoneInput) {
        if (phoneInput.value) {
            phoneInput.value = formatPhoneNumber(phoneInput.value);
        }

        phoneInput.addEventListener('input', function (e) {
            e.target.value = formatPhoneNumber(e.target.value);
            validatePhoneNumber();
        });

        if (registrationForm) {
            registrationForm.addEventListener('submit', function (e) {
                if (!validatePhoneNumber()) {
                    e.preventDefault(); // Блокируем отправку, если номер некорректный
                } else {
                    const cleanedPhone = phoneInput.value.replace(/\D/g, '');
                    phoneInput.value = '+7' + cleanedPhone.substring(1);
                }
            });
        }
        else if(editProfileForm) {
            editProfileForm.addEventListener('submit', function (e) {
                if (!validatePhoneNumber()) {
                    e.preventDefault(); // Блокируем отправку, если номер некорректный
                } else {
                    const cleanedPhone = phoneInput.value.replace(/\D/g, '');
                    phoneInput.value = '+7' + cleanedPhone.substring(1);
                }
            });
        }
    }
});