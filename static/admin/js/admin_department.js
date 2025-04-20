document.addEventListener("DOMContentLoaded", function () {
    const typeField = document.querySelector('#id_type');
    const collegeRow = document.querySelector('.form-row.field-college');

    function toggleCollegeField() {
        if (!typeField || !collegeRow) return;

        switch (typeField.value) {
            case 'academic':
                collegeRow.style.display = 'block';
                break;
            case 'administrative':
                collegeRow.style.display = 'none';
                break;
            default:
                collegeRow.style.display = 'none';
        }
    }

    // عند التحميل الأول
    toggleCollegeField();

    // عند تغيير النوع
    typeField.addEventListener('change', toggleCollegeField);
});
