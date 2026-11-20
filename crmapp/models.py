"""CRM models: companies, contacts, leads, opportunities, activities, pipeline."""

from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Company(models.Model):
    """A company / account."""

    name = models.CharField(max_length=200)
    website = models.URLField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Contact(models.Model):
    """A contact person within a company."""

    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="contacts"
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    role = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Lead(models.Model):
    """A sales lead waiting to be qualified."""

    STATUS_CHOICES = [
        ("new", "New"),
        ("contacted", "Contacted"),
        ("qualified", "Qualified"),
        ("disqualified", "Disqualified"),
        ("converted", "Converted to Opportunity"),
    ]

    name = models.CharField(max_length=200)
    company = models.ForeignKey(
        Company, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads"
    )
    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True, related_name="leads"
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    source = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="new")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_leads",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class PipelineStage(models.Model):
    """A stage in the sales pipeline (kanban column)."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    probability = models.PositiveIntegerField(
        default=0, help_text="Probability percentage (0-100)"
    )
    position = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=20, default="primary")
    is_closed_won = models.BooleanField(default=False)
    is_closed_lost = models.BooleanField(default=False)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.name


class Opportunity(models.Model):
    """A sales opportunity in the pipeline."""

    name = models.CharField(max_length=200)
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opportunities",
    )
    contact = models.ForeignKey(
        Contact,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="opportunities",
    )
    stage = models.ForeignKey(
        PipelineStage, on_delete=models.PROTECT, related_name="opportunities"
    )
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_close_date = models.DateField(null=True, blank=True)
    actual_close_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_opportunities",
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("crmapp:opportunity_detail", args=[self.pk])

    def weighted_value(self):
        """Value weighted by stage probability."""
        if not self.stage:
            return Decimal("0")
        return Decimal(str(self.value)) * Decimal(self.stage.probability) / 100


class Activity(models.Model):
    """A sales activity (call, email, meeting, etc.)."""

    TYPE_CHOICES = [
        ("call", "Call"),
        ("email", "Email"),
        ("meeting", "Meeting"),
        ("lunch", "Lunch"),
        ("demo", "Demo"),
        ("other", "Other"),
    ]

    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name="activities"
    )
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="call")
    subject = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    owner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="owned_activities",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_type_display()}: {self.subject}"  # type: ignore[attr-defined]

    def is_completed(self) -> bool:
        return self.completed_at is not None


class RevenueForecast(models.Model):
    """Monthly revenue forecast snapshot."""

    month = models.DateField(help_text="First day of the forecast month")
    total_weighted = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_pipeline = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        ordering = ["-month"]
        unique_together = ["month"]

    def __str__(self):
        return f"Forecast {self.month:%B %Y}"
