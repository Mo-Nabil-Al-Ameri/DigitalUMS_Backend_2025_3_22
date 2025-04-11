from django.db import models

class University(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("University Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("University Description"))
    code=models.CharField(
        editable=False, 
        help_text='Unique numeric identifier for the university', 
        unique=True, verbose_name='University Code',
        default='DUMS'
        )
    class Meta:
        verbose_name = _("University")
        verbose_name_plural = _("Universities")

    def __str__(self):
        return self.name

class UniversityDetail(models.Model):
    title = models.CharField(max_length=150,verbose_name=_("Detail Title"))
    subtitle = models.TextField(verbose_name=_("Detail subtitle"))
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='details',verbose_name=_("University"))

    def __str__(self):
        return f"{self.title}"
