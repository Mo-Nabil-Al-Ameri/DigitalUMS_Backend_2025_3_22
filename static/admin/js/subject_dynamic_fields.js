document.addEventListener('DOMContentLoaded', function () {
    const typeField = document.getElementById('id_type');
    const collegeField = document.getElementById('id_college');
    const departmentField = document.getElementById('id_department');

    if (!typeField || !collegeField || !departmentField) {
        console.error('Type, College, or Department fields not found.');
        return;
    }

    const collegeRow = collegeField.closest('.form-row');
    const departmentRow = departmentField.closest('.form-row');

    function toggleFields() {
        const value = typeField.value;

        if (!collegeRow || !departmentRow) {
            console.error('Could not find collegeRow or departmentRow.');
            return;
        }

        if (value === 'university') {
            collegeRow.style.display = 'none';
            departmentRow.style.display = 'none';
        } else if (value === 'college') {
            collegeRow.style.display = 'block';
            departmentRow.style.display = 'none';
        } else if (value === 'department') {
            collegeRow.style.display = 'none';
            departmentRow.style.display = 'block';
        } else if (value === 'specialization') {
            collegeRow.style.display = 'none';
            departmentRow.style.display = 'none';
        }
    }

    typeField.addEventListener('change', toggleFields);

    // تشغيله مرة واحدة عند تحميل الصفحة
    toggleFields();
});
