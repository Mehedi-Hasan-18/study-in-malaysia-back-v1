from django.db import models


class News(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    cover_public_id = models.CharField(max_length=255, blank=True)
    cover_url = models.URLField(blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "news"
        ordering = ["-published_at"]
        verbose_name_plural = "news"

    def __str__(self):
        return self.title


class Blog(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    cover_public_id = models.CharField(max_length=255, blank=True)
    cover_url = models.URLField(blank=True)
    author = models.CharField(max_length=100, blank=True)
    tags = models.CharField(max_length=300, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "blog"
        ordering = ["-published_at"]

    def __str__(self):
        return self.title


class FAQ(models.Model):
    question = models.CharField(max_length=300)
    answer = models.TextField()
    category = models.CharField(max_length=100, blank=True)
    display_order = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    class Meta:
        db_table = "faq"
        ordering = ["display_order", "id"]

    def __str__(self):
        return self.question


class Inquiry(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "inquiry"
        ordering = ["-created_at"]
        verbose_name_plural = "inquiries"

    def __str__(self):
        return f"{self.name} <{self.email}>"
