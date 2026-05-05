from django.shortcuts import render, get_object_or_404, redirect
from .models import Medicine
from django.db.models import Sum

def marketplace(request):
    verified_meds = Medicine.objects.filter(status='verified')
    
    # Calculate total savings for the "Impact Dashboard"
    total_original = verified_meds.aggregate(Sum('original_price'))['original_price__sum'] or 0
    total_resale = verified_meds.aggregate(Sum('resale_price'))['resale_price__sum'] or 0
    total_saved = int(total_original - total_resale)
    
    context = {
        'meds': verified_meds,
        'total_saved': total_saved,
    }
    return render(request, 'myapp/marketplace.html', context)

# 2. Pharmacist Dashboard: List meds waiting for the Triple-Check
def verification_queue(request):
    pending_meds = Medicine.objects.filter(status='pending')
    return render(request, 'myapp/queue.html', {'meds': pending_meds})

# 3. Perform Audit: The actual verification action
def verify_medicine(request, med_id):
    medicine = get_object_or_404(Medicine, id=med_id)
    if request.method == 'POST':
        medicine.is_physical_intact = 'intact' in request.POST
        medicine.is_authentic = 'authentic' in request.POST
        medicine.is_expiry_valid = 'expiry' in request.POST
        medicine.save()
        return redirect('verification_queue')
    return render(request, 'myapp/verify_form.html', {'med': medicine})