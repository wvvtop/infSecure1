function updateExam(checkbox, studentId, fieldName, csrfToken) {
    const cell = checkbox.closest('td');

    // Устанавливаем "ожидание" (желтый)
    cell.style.backgroundColor = '#fff9c4';

    // Отменяем предыдущий таймер, если он есть
    if (cell.restoreTimeout) {
        clearTimeout(cell.restoreTimeout);
        cell.restoreTimeout = null;
    }

    fetch('', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken,
        },
        body: new URLSearchParams({
            student_id: studentId,
            exam_field: fieldName,
            value: checkbox.checked ? '1' : '0',
        })
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка сети');
        return response.json();
    })
    .then(data => {
        // Устанавливаем цвет по результату
        cell.style.backgroundColor = data.success ? '#c8e6c9' : '#ffcdd2';
    })
    .catch(error => {
        console.error('Ошибка:', error);
        cell.style.backgroundColor = '#ffcdd2';
    })
    .finally(() => {
        // Запоминаем новый таймер, чтобы сбросить цвет через 2 секунды
        cell.restoreTimeout = setTimeout(() => {
            cell.style.backgroundColor = '';
            cell.restoreTimeout = null;
        }, 2000);
    });
}
