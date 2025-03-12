function togglePassword(inputId) {
    const input = document.getElementById(inputId);
    const icon = document.querySelector(`#${inputId} ~ .password-toggle-icon`); // Adjusted selector for sibling relationship

    if (input.type === 'password') {
        input.type = 'text';
        icon.textContent = '😐'; // Change to "hide" icon
    } else {
        input.type = 'password';
        icon.textContent = '😑'; // Change back to "show" icon
    }
}
