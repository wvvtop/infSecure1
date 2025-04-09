function updateExam(checkbox, studentId, fieldName, csrfToken) {
    const form = document.createElement('form');
    form.method = 'post';
    form.action = '';

    const csrf = document.createElement('input');
    csrf.type = 'hidden';
    csrf.name = 'csrfmiddlewaretoken';
    csrf.value = csrfToken;
    form.appendChild(csrf);

    const studentInput = document.createElement('input');
    studentInput.type = 'hidden';
    studentInput.name = 'student_id';
    studentInput.value = studentId;
    form.appendChild(studentInput);

    const fieldInput = document.createElement('input');
    fieldInput.type = 'hidden';
    fieldInput.name = 'exam_field';
    fieldInput.value = fieldName;
    form.appendChild(fieldInput);

    const valueInput = document.createElement('input');
    valueInput.type = 'hidden';
    valueInput.name = 'value';
    valueInput.value = checkbox.checked ? '1' : '0';
    form.appendChild(valueInput);

    document.body.appendChild(form);
    form.submit();
}
