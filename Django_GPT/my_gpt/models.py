from django.conf import settings
from django.db import models


class InferenceHistory(models.Model):
    class Task(models.TextChoices):
        SENTIMENT = "sentiment", "Sentiment"
        SUMMARIZE = "summarize", "Summarize"
        MODERATE = "moderate", "Moderate"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="inference_histories",
    )
    task = models.CharField(max_length=20, choices=Task.choices)
    input_text = models.TextField()
    output_text = models.TextField()
    result_data = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.task} - {self.created_at}"

