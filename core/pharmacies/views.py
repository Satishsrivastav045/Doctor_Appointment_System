from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import MedicineStock, Pharmacy


def medicine_search(request):
    query = request.GET.get("q", "").strip()
    location = request.GET.get("location", "").strip()

    medicines = MedicineStock.objects.select_related("pharmacy").filter(quantity__gt=0)
    if query:
        medicines = medicines.filter(
            Q(medicine_name__icontains=query)
            | Q(brand_name__icontains=query)
            | Q(strength__icontains=query)
        )
    if location:
        medicines = medicines.filter(
            Q(pharmacy__district__icontains=location)
            | Q(pharmacy__city_or_block__icontains=location)
            | Q(pharmacy__village_or_area__icontains=location)
            | Q(pharmacy__full_address__icontains=location)
        )

    pharmacies = Pharmacy.objects.prefetch_related("medicines").order_by("-is_verified", "shop_name")

    return render(
        request,
        "medicine_search.html",
        {
            "medicines": medicines.order_by("-pharmacy__is_verified", "medicine_name"),
            "pharmacies": pharmacies[:8],
            "query": query,
            "location": location,
        },
    )


@login_required
def pharmacy_dashboard(request):
    if not hasattr(request.user, "pharmacy_profile"):
        messages.error(request, "You are not allowed to open the pharmacy dashboard.")
        return redirect("/patient-dashboard/")

    pharmacy = request.user.pharmacy_profile
    medicines = pharmacy.medicines.all()
    available_count = medicines.filter(quantity__gt=0).count()

    return render(
        request,
        "pharmacy_dashboard.html",
        {
            "pharmacy": pharmacy,
            "medicines": medicines,
            "pharmacy_stats": {
                "total": medicines.count(),
                "available": available_count,
                "low_stock": medicines.filter(quantity__lte=5, quantity__gt=0).count(),
            },
        },
    )


@login_required
def upsert_medicine(request, medicine_id=None):
    if not hasattr(request.user, "pharmacy_profile"):
        messages.error(request, "Only pharmacy owners can manage medicines.")
        return redirect("/pharmacies/")

    pharmacy = request.user.pharmacy_profile
    medicine = None
    if medicine_id:
        medicine = get_object_or_404(MedicineStock, id=medicine_id, pharmacy=pharmacy)

    if request.method == "POST":
        name = request.POST.get("medicine_name", "").strip()
        if not name:
            messages.error(request, "Medicine name is required.")
            return redirect(request.path)

        data = {
            "medicine_name": name,
            "brand_name": request.POST.get("brand_name", "").strip(),
            "strength": request.POST.get("strength", "").strip(),
            "form": request.POST.get("form", "").strip(),
            "price": request.POST.get("price") or 0,
            "quantity": request.POST.get("quantity") or 0,
            "prescription_required": request.POST.get("prescription_required") == "on",
        }
        if medicine:
            for field, value in data.items():
                setattr(medicine, field, value)
            medicine.save()
            messages.success(request, "Medicine updated.")
        else:
            MedicineStock.objects.create(pharmacy=pharmacy, **data)
            messages.success(request, "Medicine added.")
        return redirect("/pharmacy-dashboard/")

    return render(
        request,
        "medicine_form.html",
        {
            "medicine": medicine,
            "pharmacy": pharmacy,
        },
    )

# Create your views here.
