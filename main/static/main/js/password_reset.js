document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("passwordResetForm");
    const captchaResponseInput = document.getElementById("h-captcha-response");
    const submitButton = form.querySelector("button[type='submit']");

    // Блокируем кнопку отправки до прохождения капчи
    if (submitButton) {
        submitButton.disabled = true;
    }

    // Функция, вызываемая после успешного прохождения капчи
    window.onCaptchaSuccess = function (token) {
        captchaResponseInput.value = token;
        if (submitButton) {
            submitButton.disabled = false;
        }
    };

    // Обработчик отправки формы
    if (form) {
        form.addEventListener("submit", function (event) {
            if (!captchaResponseInput.value) {
                event.preventDefault();
                alert("Пожалуйста, подтвердите, что вы не робот");
            }
        });
    }
});