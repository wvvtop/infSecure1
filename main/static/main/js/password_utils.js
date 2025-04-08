
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


document.addEventListener('DOMContentLoaded', function () {
    function setupPasswordValidation(formId, password1Id, password2Id) {
        const form = document.getElementById(formId);
        const password1Input = document.getElementById(password1Id);
        const password2Input = document.getElementById(password2Id);

        if (!form || !password1Input || !password2Input) return;

        let errorContainer = document.getElementById(`${formId}-password-errors`);
        if (!errorContainer) {
            errorContainer = document.createElement('div');
            errorContainer.id = `${formId}-password-errors`;
            errorContainer.classList.add('password-error-container');
            password1Input.closest('.mb-3').appendChild(errorContainer);
        }

        function validatePassword() {
            const password1 = password1Input.value;
            const password2 = password2Input.value;
            const errors = [];
            errorContainer.innerHTML = '';

            if (password1.length < 8) errors.push("Пароль должен содержать минимум 8 символов.");
            if (password1.length > 20) errors.push("Пароль не может быть длиннее 20 символов.");
            if (!/[A-ZА-Я]/.test(password1)) errors.push("Пароль должен содержать минимум одну заглавную букву.");
            if (!/[a-zа-я]/.test(password1)) errors.push("Пароль должен содержать минимум одну строчную букву.");
            if (!/[0-9]/.test(password1)) errors.push("Пароль должен содержать минимум одну цифру.");
            if (!/[!@#$%^&*(),.?":{}|<>]/.test(password1)) errors.push("Пароль должен содержать минимум один спецсимвол.");
            if (password1 !== password2 && password2.length > 0) errors.push("Пароли не совпадают.");

            errors.forEach(error => {
                const errorElement = document.createElement('div');
                errorElement.textContent = error;
                errorContainer.appendChild(errorElement);
            });
        }

        password1Input.addEventListener('input', validatePassword);
        password2Input.addEventListener('input', validatePassword);

        form.addEventListener('submit', function (event) {
            validatePassword();
            if (errorContainer.children.length > 0) event.preventDefault();
        });
    }

    setupPasswordValidation('registrationForm', 'password1', 'password2'); // Для регистрации
    setupPasswordValidation('passwordResetForm', 'new_password', 'confirm_password'); // Для сброса пароля
});
