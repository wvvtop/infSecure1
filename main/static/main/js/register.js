document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("registrationForm");
    const captchaResponseInput = document.getElementById("h-captcha-response");
    const submitButton = form.querySelector("button[type='submit']");

    // Блокируем кнопку отправки до того, как капча будет пройдена
    submitButton.disabled = true;

    // Функция, которая будет вызвана после успешного прохождения капчи
    window.onCaptchaSuccess = function (token) {
        // Записываем токен в скрытое поле формы
        captchaResponseInput.value = token;

        // Разблокируем кнопку отправки
        submitButton.disabled = false;
    };

    // Обработчик отправки формы
    form.addEventListener("submit", function (event) {
        // Если капча не пройдена, отменяем отправку формы
        if (!captchaResponseInput.value) {
            event.preventDefault(); // Останавливаем отправку формы
            alert("Пожалуйста, пройдите капчу.");
        }
    });
});


