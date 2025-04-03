document.addEventListener("DOMContentLoaded", function () {
    const typeField = document.querySelector('#id_type');
    const collegeRow = document.querySelector('.form-row.field-college');

    function toggleCollegeField() {
        if (!typeField || !collegeRow) return;

        if (typeField.value === 'academic') {
            collegeRow.style.display = 'block';
        } else {
            collegeRow.style.display = 'none';
        }
    }

    // عند التحميل الأول
    toggleCollegeField();

    // عند تغيير النوع
    typeField.addEventListener('change', toggleCollegeField);
});
