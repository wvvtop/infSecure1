// Функция для переключения видимости пароля
function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = document.querySelector(`#${inputId} ~ .password-toggle-icon`);

    if (input.type === 'password') {
        input.type = 'text';
        icon.textContent = '😐'; // Иконка "скрыть пароль"
    } else {
        input.type = 'password';
        icon.textContent = '😑'; // Иконка "показать пароль"
    }
}

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

    if (phoneInput) {
        // Восстановление отформатированного номера при загрузке страницы
        if (phoneInput.value) {
            phoneInput.value = formatPhoneNumber(phoneInput.value);
        }

        // Обработчик ввода
        phoneInput.addEventListener('input', function (e) {
            e.target.value = formatPhoneNumber(e.target.value);
        });

        // Очистка номера перед отправкой формы
        const registrationForm = document.getElementById('registrationForm');
        if (registrationForm) {
            registrationForm.addEventListener('submit', function (e) {
                // Убираем все нецифровые символы, кроме "+"
                const cleanedPhone = phoneInput.value.replace(/\D/g, '');
                // Убедимся, что номер начинается с +7
                phoneInput.value = '+7' + cleanedPhone.substring(1);
            });
        }
    }
});


document.addEventListener('DOMContentLoaded', function () {
    const registrationForm = document.getElementById('registrationForm');
    const password1Input = document.getElementById('password1');
    const password2Input = document.getElementById('password2');

    // Находим или создаем контейнер для ошибок
    let errorContainer = document.getElementById('password-errors');
    if (!errorContainer) {
        errorContainer = document.createElement('div');
        errorContainer.id = 'password-errors';
        errorContainer.classList.add('password-error-container'); // Класс из CSS
        password1Input.closest('.mb-3').appendChild(errorContainer); // Добавляем ошибки ниже всего блока
    }

    // Функция для валидации пароля
    function validatePassword() {
        const password1 = password1Input.value;
        const password2 = password2Input.value;
        const errors = [];

        // Очистка предыдущих ошибок
        errorContainer.innerHTML = '';

        // Проверка длины пароля
        if (password1.length < 8) {
            errors.push("Пароль должен содержать минимум 8 символов.");
        }
        if (password1.length > 20) {
            errors.push("Пароль не может быть длиннее 20 символов.");
        }

        // Проверка на наличие заглавной буквы
        if (!/[A-ZА-Я]/.test(password1)) {
            errors.push("Пароль должен содержать минимум одну заглавную букву.");
        }

        // Проверка на наличие строчной буквы
        if (!/[a-zа-я]/.test(password1)) {
            errors.push("Пароль должен содержать минимум одну строчную букву.");
        }

        // Проверка на наличие хотя бы одной цифры
        if (!/[0-9]/.test(password1)) {
            errors.push("Пароль должен содержать минимум одну цифру.");
        }

        // Проверка на наличие специального символа
        if (!/[!@#$%^&*(),.?":{}|<>]/.test(password1)) {
            errors.push("Пароль должен содержать минимум один специальный символ.");
        }

        // Проверка совпадения паролей
        if (password1 !== password2 && password2.length > 0) {
            errors.push("Пароли не совпадают.");
        }

        // Отображение ошибок
        if (errors.length > 0) {
            errors.forEach(error => {
                const errorElement = document.createElement('div');
                errorElement.textContent = error;
                errorContainer.appendChild(errorElement);
            });
        }
    }

    // Динамическая проверка при вводе
    password1Input.addEventListener('input', validatePassword);
    password2Input.addEventListener('input', validatePassword);

    // Проверка при отправке формы
    registrationForm.addEventListener('submit', function (event) {
        validatePassword();
        if (errorContainer.children.length > 0) {
            event.preventDefault(); // Остановить отправку формы, если есть ошибки
        }
    });
});
