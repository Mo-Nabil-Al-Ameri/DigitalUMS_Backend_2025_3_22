document.addEventListener('DOMContentLoaded', function () {
    const studyPlanField = document.getElementById('id_study_plan');
    const academicLevelField = document.getElementById('id_academic_level');

    if (studyPlanField && academicLevelField) {
        function clearAcademicLevels() {
            academicLevelField.innerHTML = '';
            const option = document.createElement('option');
            option.textContent = '--- Please select a Study Plan first ---';
            option.disabled = true;
            option.selected = true;
            academicLevelField.appendChild(option);
        }

        function loadAcademicLevels(studyPlanId) {
            const url = `/academic/ajax/get-academic-levels/?study_plan=${studyPlanId}`;
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    academicLevelField.innerHTML = '';
                    if (data.levels.length > 0) {
                        data.levels.forEach(function (level) {
                            const option = document.createElement('option');
                            option.value = level.id;
                            option.textContent = level.name;
                            academicLevelField.appendChild(option);
                        });
                    } else {
                        clearAcademicLevels();
                    }
                })
                .catch(error => {
                    console.error('Error fetching academic levels:', error);
                    clearAcademicLevels();
                });
        }

        if (!studyPlanField.value) {
            clearAcademicLevels();
        } else {
            loadAcademicLevels(studyPlanField.value);
        }

        studyPlanField.addEventListener('change', function () {
            const studyPlanId = this.value;
            if (studyPlanId) {
                loadAcademicLevels(studyPlanId);
            } else {
                clearAcademicLevels();
            }
        });
    }
});
