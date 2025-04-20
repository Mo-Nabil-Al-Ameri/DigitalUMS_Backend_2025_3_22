from modeltranslation.translator import translator, TranslationOptions
from .models import AcademicLevel 

class AcademicLevelTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(AcademicLevel, AcademicLevelTranslationOptions)