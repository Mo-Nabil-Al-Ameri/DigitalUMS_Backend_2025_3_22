from modeltranslation.translator import translator, TranslationOptions
from .models import StudyPlan,SemesterPlan

class StudyPlanTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(StudyPlan, StudyPlanTranslationOptions)

class SemesterPlanTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(SemesterPlan, SemesterPlanTranslationOptions)