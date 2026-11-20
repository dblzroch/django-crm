"""CRM views: companies, contacts, leads, opportunities, pipeline, forecast."""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import (
    Activity,
    Company,
    Contact,
    Lead,
    Opportunity,
    PipelineStage,
)


# ------------------------------------------------------------------
# Dashboard
# ------------------------------------------------------------------
@login_required
def dashboard(request):
    """CRM dashboard with key metrics and recent activity."""
    total_opportunities = Opportunity.objects.count()
    total_value = Opportunity.objects.aggregate(total=Sum("value"))["total"] or 0
    weighted_value = sum(o.weighted_value() for o in Opportunity.objects.all())
    open_opps = (
        Opportunity.objects.exclude(stage__is_closed_won=True)
        .exclude(stage__is_closed_lost=True)
        .count()
    )
    won_opps = Opportunity.objects.filter(stage__is_closed_won=True).count()
    lost_opps = Opportunity.objects.filter(stage__is_closed_lost=True).count()
    recent_activities = Activity.objects.select_related(
        "opportunity", "owner"
    ).order_by("-created_at")[:10]
    upcoming = Activity.objects.filter(
        completed_at__isnull=True, due_date__lte=timezone.now() + timedelta(days=7)
    ).order_by("due_date")[:10]

    return render(
        request,
        "crmapp/dashboard.html",
        {
            "total_opportunities": total_opportunities,
            "total_value": total_value,
            "weighted_value": weighted_value,
            "open_opps": open_opps,
            "won_opps": won_opps,
            "lost_opps": lost_opps,
            "recent_activities": recent_activities,
            "upcoming": upcoming,
        },
    )


# ------------------------------------------------------------------
# Companies
# ------------------------------------------------------------------
@login_required
def company_list(request):
    companies = Company.objects.all().order_by("name")
    return render(request, "crmapp/company_list.html", {"companies": companies})


@login_required
def company_detail(request, pk):
    company = get_object_or_404(Company, pk=pk)
    contacts = company.contacts.all()  # type: ignore[attr-defined]
    opportunities = company.opportunities.all()  # type: ignore[attr-defined]
    return render(
        request,
        "crmapp/company_detail.html",
        {"company": company, "contacts": contacts, "opportunities": opportunities},
    )


@login_required
def company_create(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        website = request.POST.get("website", "").strip()
        phone = request.POST.get("phone", "").strip()
        address = request.POST.get("address", "").strip()
        industry = request.POST.get("industry", "").strip()
        if not name:
            messages.error(request, "Company name is required.")
            return render(request, "crmapp/company_create.html")
        Company.objects.create(
            name=name, website=website, phone=phone, address=address, industry=industry
        )
        messages.success(request, f"Company '{name}' created.")
        return redirect("crmapp:company_list")
    return render(request, "crmapp/company_create.html")


# ------------------------------------------------------------------
# Contacts
# ------------------------------------------------------------------
@login_required
def contact_list(request):
    contacts = (
        Contact.objects.select_related("company")
        .all()
        .order_by("last_name", "first_name")
    )
    return render(request, "crmapp/contact_list.html", {"contacts": contacts})


@login_required
def contact_detail(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    opportunities = contact.opportunities.all()  # type: ignore[attr-defined]
    return render(
        request,
        "crmapp/contact_detail.html",
        {"contact": contact, "opportunities": opportunities},
    )


@login_required
def contact_create(request):
    companies = Company.objects.all().order_by("name")
    if request.method == "POST":
        company_id = request.POST.get("company")
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        role = request.POST.get("role", "").strip()
        if not first_name or not last_name:
            messages.error(request, "First and last name are required.")
            return render(
                request, "crmapp/contact_create.html", {"companies": companies}
            )
        company = Company.objects.get(pk=company_id) if company_id else None
        Contact.objects.create(
            company=company,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            role=role,
        )
        messages.success(request, f"Contact '{first_name} {last_name}' created.")
        return redirect("crmapp:contact_list")
    return render(request, "crmapp/contact_create.html", {"companies": companies})


# ------------------------------------------------------------------
# Leads
# ------------------------------------------------------------------
@login_required
def lead_list(request):
    leads = (
        Lead.objects.select_related("company", "contact", "owner")
        .all()
        .order_by("-created_at")
    )
    return render(request, "crmapp/lead_list.html", {"leads": leads})


@login_required
def lead_detail(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    return render(request, "crmapp/lead_detail.html", {"lead": lead})


@login_required
def lead_create(request):
    companies = Company.objects.all().order_by("name")
    contacts = Contact.objects.all().order_by("last_name", "first_name")
    users = User.objects.all().order_by("username")
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        company_id = request.POST.get("company") or None
        contact_id = request.POST.get("contact") or None
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        source = request.POST.get("source", "").strip()
        status = request.POST.get("status", "new")
        notes = request.POST.get("notes", "").strip()
        owner_id = request.POST.get("owner") or None
        if not name:
            messages.error(request, "Lead name is required.")
            return render(
                request,
                "crmapp/lead_create.html",
                {"companies": companies, "contacts": contacts, "users": users},
            )
        company = Company.objects.get(pk=company_id) if company_id else None
        contact = Contact.objects.get(pk=contact_id) if contact_id else None
        owner = User.objects.get(pk=owner_id) if owner_id else None
        Lead.objects.create(
            name=name,
            company=company,
            contact=contact,
            email=email,
            phone=phone,
            source=source,
            status=status,
            notes=notes,
            owner=owner,
        )
        messages.success(request, f"Lead '{name}' created.")
        return redirect("crmapp:lead_list")
    return render(
        request,
        "crmapp/lead_create.html",
        {"companies": companies, "contacts": contacts, "users": users},
    )


# ------------------------------------------------------------------
# Opportunities
# ------------------------------------------------------------------
@login_required
def opportunity_list(request):
    opportunities = (
        Opportunity.objects.select_related("stage", "company", "owner")
        .all()
        .order_by("-created_at")
    )
    return render(
        request,
        "crmapp/opportunity_list.html",
        {"opportunities": opportunities},
    )


@login_required
def opportunity_detail(request, pk):
    opportunity = get_object_or_404(Opportunity, pk=pk)
    activities = opportunity.activities.all()  # type: ignore[attr-defined]
    return render(
        request,
        "crmapp/opportunity_detail.html",
        {"opportunity": opportunity, "activities": activities},
    )


@login_required
def opportunity_create(request):
    companies = Company.objects.all().order_by("name")
    contacts = Contact.objects.all().order_by("last_name", "first_name")
    stages = PipelineStage.objects.all().order_by("position")
    users = User.objects.all().order_by("username")
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        company_id = request.POST.get("company") or None
        contact_id = request.POST.get("contact") or None
        stage_id = request.POST.get("stage")
        value = request.POST.get("value") or 0
        expected_close = request.POST.get("expected_close_date") or None
        description = request.POST.get("description", "").strip()
        owner_id = request.POST.get("owner") or None
        if not name or not stage_id:
            messages.error(request, "Name and stage are required.")
            return render(
                request,
                "crmapp/opportunity_create.html",
                {
                    "companies": companies,
                    "contacts": contacts,
                    "stages": stages,
                    "users": users,
                },
            )
        stage = PipelineStage.objects.get(pk=stage_id)
        company = Company.objects.get(pk=company_id) if company_id else None
        contact = Contact.objects.get(pk=contact_id) if contact_id else None
        owner = User.objects.get(pk=owner_id) if owner_id else None
        opp = Opportunity.objects.create(
            name=name,
            company=company,
            contact=contact,
            stage=stage,
            value=value,
            expected_close_date=expected_close,
            description=description,
            owner=owner,
        )
        messages.success(request, f"Opportunity '{name}' created.")
        return redirect("crmapp:opportunity_detail", pk=opp.pk)
    return render(
        request,
        "crmapp/opportunity_create.html",
        {
            "companies": companies,
            "contacts": contacts,
            "stages": stages,
            "users": users,
        },
    )


@login_required
def opportunity_change_stage(request, pk):
    """Change opportunity stage (kanban move)."""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    if request.method == "POST":
        stage_id = request.POST.get("stage_id")
        if stage_id:
            new_stage = get_object_or_404(PipelineStage, pk=stage_id)
            opportunity.stage = new_stage
            if new_stage.is_closed_won and not opportunity.actual_close_date:
                opportunity.actual_close_date = timezone.now().date()
            opportunity.save()
            messages.success(request, f"Opportunity moved to '{new_stage.name}'.")
    return redirect("crmapp:pipeline_kanban")


# ------------------------------------------------------------------
# Pipeline Kanban
# ------------------------------------------------------------------
@login_required
def pipeline_kanban(request):
    """Visual kanban board: opportunities grouped by pipeline stage."""
    stages = PipelineStage.objects.all().order_by("position")
    kanban = []
    for stage in stages:
        opps = Opportunity.objects.filter(stage=stage).order_by("-value")
        kanban.append({"stage": stage, "opportunities": opps})
    total_pipeline = Opportunity.objects.aggregate(total=Sum("value"))["total"] or 0
    weighted_total = sum(o.weighted_value() for o in Opportunity.objects.all())
    return render(
        request,
        "crmapp/pipeline_kanban.html",
        {
            "kanban": kanban,
            "total_pipeline": total_pipeline,
            "weighted_total": weighted_total,
        },
    )


# ------------------------------------------------------------------
# Activities
# ------------------------------------------------------------------
@login_required
def add_activity(request, pk):
    """Add an activity to an opportunity."""
    opportunity = get_object_or_404(Opportunity, pk=pk)
    if request.method == "POST":
        type_ = request.POST.get("type", "call")
        subject = request.POST.get("subject", "").strip()
        notes = request.POST.get("notes", "").strip()
        due_date = request.POST.get("due_date") or None
        if not subject:
            messages.error(request, "Subject is required.")
            return redirect("crmapp:opportunity_detail", pk=pk)
        Activity.objects.create(
            opportunity=opportunity,
            type=type_,
            subject=subject,
            notes=notes,
            due_date=due_date,
            owner=request.user,
        )
        messages.success(request, "Activity added.")
    return redirect("crmapp:opportunity_detail", pk=pk)


# ------------------------------------------------------------------
# Revenue Forecast
# ------------------------------------------------------------------
@login_required
def revenue_forecast(request):
    """Revenue forecast by month based on expected close dates and stage probability."""
    months = {}
    opps = Opportunity.objects.exclude(stage__is_closed_lost=True)
    for opp in opps:
        if not opp.expected_close_date:
            continue
        month_key = opp.expected_close_date.replace(day=1)
        weighted = opp.weighted_value()
        months.setdefault(month_key, {"weighted": 0, "pipeline": 0, "count": 0})
        months[month_key]["weighted"] += weighted
        months[month_key]["pipeline"] += opp.value
        months[month_key]["count"] += 1

    sorted_months = sorted(months.items())
    total_weighted = sum(m["weighted"] for _, m in sorted_months)
    total_pipeline = sum(m["pipeline"] for _, m in sorted_months)

    return render(
        request,
        "crmapp/revenue_forecast.html",
        {
            "months": sorted_months,
            "total_weighted": total_weighted,
            "total_pipeline": total_pipeline,
        },
    )
