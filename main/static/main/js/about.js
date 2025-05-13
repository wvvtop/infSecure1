function loadInstructors() {
    $.getJSON('/api/instructors/?_=' + new Date().getTime(), function(data) {
        const container = $('#instructors-container');
        container.empty();

        data.instructors.forEach(i => {
            const initials = (i.first_name?.[0] || '') + (i.last_name?.[0] || '');
            const cardHTML = `
                <div class="instructor-card">
                    <div class="instructor-img">
                        <div class="default-avatar">${initials}</div>
                    </div>
                    <div class="instructor-info">
                        <h3>${i.first_name} ${i.last_name}</h3>
                        <p>Телефон: ${i.phone}</p>
                    </div>
                </div>
            `;
            container.append(cardHTML);
        });
    }).fail(function() {
        console.error("Ошибка при загрузке инструкторов");
    });
}

$(document).ready(function() {
    loadInstructors();
    setInterval(loadInstructors, 5000); // обновление каждые 5 сек
});
