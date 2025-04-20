# subjects/utils.py

import re
from django.utils.text import slugify
from django.utils.translation import get_language
from django.db.models import Q
def generate_subject_code(model_class, instance, field_name='code', from_field='name', max_check=20, subject_type=None):
    from universityApps.courses.models import Subject_Types

    """Generate a repeatable code for a subject based on its type."""
    raw_text = getattr(instance, from_field,)
    raw_text=raw_text.strip()[:4]
    base_code = slugify(raw_text).upper()
    code = base_code
    if subject_type is not None:
        if subject_type == Subject_Types.UNIVERSITY:
            code ="UMS"
            return code
        elif subject_type == Subject_Types.COLLEGE:
            if not instance.college:
                raise ValueError("Subject must be associated with a college.")
            code =instance.college.code
            return code
        elif subject_type == Subject_Types.DEPARTMENT:
            if not instance.department:
                raise ValueError("Subject must be associated with a department.")
            code =instance.department.code
            return code
        else :
            return code
    return base_code

def generate_unique_code(model_class, instance, field_name='code', from_field='name', max_check=20):
    """
    توليد رمز (code) فريد بناءً على حقل آخر (الاسم عادة)، مع أداء متوازن.
    """
    raw_text = getattr(instance, from_field,)
    
    raw_text=raw_text.strip()[:4]
   
    base_code = slugify(raw_text).upper()

    code = base_code

    queryset = model_class.objects.filter(
        Q(**{f"{field_name}__startswith": base_code})
    ).exclude(id=instance.id).order_by(field_name)[:max_check]

    existing_codes = set(queryset.values_list(field_name, flat=True))

    if code not in existing_codes:
        return code

    pattern = re.compile(rf'^{re.escape(base_code)}-(\d+)$')
    numbers = [
        int(match.group(1)) for c in existing_codes
        if (match := pattern.match(c))
    ]

    next_number = (max(numbers) + 1) if numbers else 1

    return f"{base_code}-{next_number}"


def generate_unique_slug(model_class, instance, slug_field_name='slug', slug_from_fields=None, max_check=100):
    """
    توليد سلاج فريد (slug) مع دعم الترجمة الديناميكية حسب اللغة المختارة.
    """
    if slug_from_fields is None:
        raise ValueError("slug_from_fields is required.")

    lang = get_language() or 'en'
    base_slug_parts = [str(getattr(instance, field, '')) for field in slug_from_fields]
    combined_text = '-'.join(base_slug_parts)

    # حسب اللغة، نقرر كيف نصنع الـ slug
    if lang == 'ar':
        base_slug = slugify(combined_text, allow_unicode=True)  # يدعم الحروف العربية
    else:
        base_slug = slugify(combined_text)  # بدون unicode للإنجليزي

    slug = base_slug

    queryset = model_class.objects.filter(
        Q(**{f"{slug_field_name}__startswith": base_slug})
    ).exclude(id=instance.id).order_by(slug_field_name)[:max_check]

    existing_slugs = set(queryset.values_list(slug_field_name, flat=True))

    if slug not in existing_slugs:
        return slug

    pattern = re.compile(rf'^{re.escape(base_slug)}-(\d+)$')
    numbers = [
        int(match.group(1)) for s in existing_slugs
        if (match := pattern.match(s))
    ]

    next_number = (max(numbers) + 1) if numbers else 1

    return f"{base_slug}-{next_number}"
