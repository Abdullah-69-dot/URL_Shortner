from django.db import models

class URL(models.Model):
    """
    Core Model for storing long URLs and their corresponding short codes.
    Includes timestamps and access count for basic analytics.
    """
    url = models.URLField(max_length=2048)
    short_code = models.CharField(max_length=20, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    access_count = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"{self.short_code} -> {self.url[:50]}"
