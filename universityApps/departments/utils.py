from django.utils.text import slugify
import os
import datetime
# function for department image path
def department_image_path(instance, filename):
    # تحويل اسم القسم والكلية إلى صيغة مناسبة للمسار
    department_slug = slugify(instance.name)
    college_slug = slugify(instance.college.name)
    # الحصول على تاريخ اليوم بصيغة معينة
    date_str = datetime.datetime.now().strftime("%Y_%m_%d")
    # دمج مسار الملف مع مسار المجلد
    full_path = os.path.join('colleges', college_slug, department_slug,'images', date_str, filename)
    return full_path
