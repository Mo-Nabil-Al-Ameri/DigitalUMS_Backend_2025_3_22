from django.core.exceptions import ValidationError
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from .patterns import (
    NumberingPattern,
    CodeFormatPattern,
)
class BaseNumberingSystem:
    """
    Base class for generating codes and numbers using various numbering patterns.
    """

    def __init__(
        self,
        pattern=NumberingPattern.NUMERIC,
        prefix='',
        suffix='',
        separator='-',
        min_value=1,
        max_value=999,
        padding=3,
        ignored_words=None
    ):
        self.pattern = pattern
        self.prefix = prefix
        self.suffix = suffix
        self.separator = separator
        self.min_value = min_value
        self.max_value = max_value
        self.padding = padding
        self.ignored_words = ignored_words or {'and','in','on', 'of', 'the', 'في', 'من', 'ال', 'و'}

    def generate_number(self, model_class, **kwargs):
        self.target_field = kwargs.get('field', 'number')

        if self.pattern == NumberingPattern.NUMERIC:
            return self._generate_numeric(model_class)

        elif self.pattern == NumberingPattern.AdministrativedepartNumber:
            return self.generate_Admindepartmentnumber(model_class)
        elif self.pattern == NumberingPattern.ALPHA:
            return self._generate_alpha(model_class)

        elif self.pattern == NumberingPattern.ALPHANUMERIC:
            return self._generate_alphanumeric(model_class, **kwargs)

        elif self.pattern == NumberingPattern.NAME_BASED:
            return self._generate_name_based(model_class, **kwargs)

        elif self.pattern == NumberingPattern.PARENT_BASED:
            return self._generate_parent_based(model_class, **kwargs)

        elif self.pattern == NumberingPattern.CUSTOM:
            return kwargs.get('pattern', '')

        raise ValidationError(f"Unsupported numbering pattern: {self.pattern}")

    def _generate_numeric(self, model_class):
        max_value = model_class.objects.aggregate(
            max_value=models.Max(self.target_field)
        )['max_value'] or 0

        new_value = max_value + 1
        if new_value > self.max_value:
            raise ValidationError("Maximum allowed number exceeded.")
        return new_value
    def generate_Admindepartmentnumber(self, model_class, **kwargs):
        filters = kwargs.get('filters', {})
        
        # نجلب الأرقام المستخدمة مرتبة
        used_numbers = model_class.objects.filter(**filters).values_list(self.target_field, flat=True).order_by(self.target_field)

        expected = self.min_value
        for num in used_numbers:
            if num > self.max_value:
                break  # تجاوزنا الحد الأعلى المسموح
            if num > expected:
                return expected
            elif num == expected:
                expected += 1

        if expected > self.max_value:
            raise ValidationError(_(
                f"The maximum allowed number ({self.max_value}) has been reached."
            ))

        return expected

    def _generate_alpha(self, model_class):
        max_value = model_class.objects.aggregate(
            max_value=models.Max(self.target_field)
        )['max_value'] or 0

        new_value = max_value + 1
        if new_value > 26:
            raise ValidationError("Maximum alphabet limit (A-Z) exceeded.")
        return chr(64 + new_value)  # A=65

    def _generate_alphanumeric(self, model_class, **kwargs):
        prefix = kwargs.get('prefix')
        if not prefix:
            raise ValidationError("Prefix is required for alphanumeric numbering.")

        existing_entries = model_class.objects.filter(
            **{f"{self.target_field}__startswith": prefix}
        ).values_list(self.target_field, flat=True)

        i = 1
        while f"{prefix}{str(i).zfill(self.padding)}" in existing_entries:
            i += 1

        return f"{prefix}{str(i).zfill(self.padding)}"
    def _generate_name_based(self, model_class, **kwargs):
        name = kwargs.get('name', '')
        target_field = kwargs.get('field', 'code')
        code_format = kwargs.get('code_format', CodeFormatPattern.FIRST_LETTER_EACH_WORD.value)
        code_length = kwargs.get('code_length', 3)
        current_type = kwargs.get('type')  # اختياري
        academic_suffix = kwargs.get('academic_suffix', '-A')
        admin_suffix = kwargs.get('admin_suffix', '-I')
        manual_code = kwargs.get('manual_code', '').upper()

        if not name and code_format != CodeFormatPattern.MANUAL.value:
            raise ValidationError("Name is required to generate the code.")

        words = name.split()

        if code_format == CodeFormatPattern.FIRST_LETTER_EACH_WORD.value:
            base_code = ''.join(word[0].upper() for word in words if word.lower() not in self.ignored_words)
        elif code_format == CodeFormatPattern.FIRST_N_LETTERS.value:
            base_code = words[0][:code_length].upper() if words else ''
        elif code_format == CodeFormatPattern.FIRST_N_LETTERS_EACH_WORD.value:
            base_code = ''.join(word[:code_length].upper() for word in words if word.lower() not in self.ignored_words)
        elif code_format == CodeFormatPattern.ABBREVIATE_VOWELS_REMOVED.value:
            base_code = ''.join(c for c in words[0].upper() if c not in 'AEIOU')[:code_length] if words else ''
        elif code_format == CodeFormatPattern.MANUAL.value:
            if not manual_code:
                raise ValidationError("Manual code must be provided.")
            base_code = manual_code
        else:
            raise ValidationError(f"Unsupported code format: {code_format}")

        # تحقق من وجود النوع الآخر فقط إذا كان الحقل موجودًا
        has_type_field = 'type' in [f.name for f in model_class._meta.fields]
        if has_type_field and current_type:
            other_type = 'administrative' if current_type == 'academic' else 'academic'
            exists_in_other_type = model_class.objects.filter(name=name, type=other_type).exists()
            exists_in_same_type = model_class.objects.filter(**{target_field: base_code, 'type': current_type}).exists()
        else:
            exists_in_other_type = False
            exists_in_same_type = model_class.objects.filter(**{target_field: base_code}).exists()

        # ممنوع التكرار في نفس النوع
        if exists_in_same_type:
            raise ValidationError(f"A code '{base_code}' already exists for this type.")

        # إذا وُجد الاسم في نوع آخر، أضف لاحقة
        if exists_in_other_type:
            if current_type == 'academic' and academic_suffix:
                base_code += academic_suffix
            elif current_type == 'administrative' and admin_suffix:
                base_code += admin_suffix

        return base_code

    def _generate_parent_based(self, model_class, **kwargs):
        parent_id = kwargs.get('parent_id')
        parent_field = kwargs.get('parent_field')

        if not parent_id or not parent_field:
            raise ValidationError("Both 'parent_id' and 'parent_field' are required for PARENT_BASED numbering.")

        try:
            parent_id = int(parent_id)
        except (TypeError, ValueError):
            raise ValidationError("'parent_id' must be a valid integer.")

        prefix = parent_id * 100

        filter_kwargs = {
            f"{parent_field}_id": parent_id,
            f"{self.target_field}__gte": prefix,
            f"{self.target_field}__lt": prefix + 100
        }

        max_value = model_class.objects.filter(**filter_kwargs).aggregate(
            max_dep=models.Max(self.target_field)
        )['max_dep'] or prefix

        new_value = max_value + 1
        if new_value >= prefix + 100:
            raise ValidationError(f"Maximum number reached for parent ID {parent_id}.")

        return new_value

    def format_number(self, number):
        formatted = str(number)
        if self.pattern == NumberingPattern.NUMERIC:
            formatted = str(number).zfill(4)

        if self.prefix:
            formatted = f"{self.prefix}{self.separator}{formatted}"
        if self.suffix:
            formatted = f"{formatted}{self.separator}{self.suffix}"

        return formatted
