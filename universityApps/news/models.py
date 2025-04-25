from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

class NewsArticle(models.Model):
    title = models.CharField(max_length=255, verbose_name=_("Title"))
    slug = models.SlugField(unique=True, blank=True)
    summary = models.TextField(verbose_name=_("Summary"))
    content = models.TextField(verbose_name=_("Content"))
    image = models.ImageField(upload_to='news/images/', blank=True, null=True)
    published = models.BooleanField(default=False)
    publish_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("News Article")
        verbose_name_plural = _("News Articles")
        ordering = ['-publish_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
