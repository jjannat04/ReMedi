from django.shortcuts import render, get_object_or_404, redirect
from .models import Medicine, ReMediCorner
from django.db.models import Sum
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .forms import DonationForm

from django.utils import timezone

# A simple custom form to include the 'role' field
class SignUpForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'phone', 'license_number')
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # If the user is a pharmacist, deactivate them pending approval
            if user.role == User.Role.PHARMACIST:
                user.is_active = False 
                user.save()
                # Redirect to a "Wait for approval" page instead of logging them in
                return render(request, 'myapp/pending_approval.html')
            
            # Regular users (Donors/Patients) can log in immediately
            user.save()
            login(request, user)
            return redirect('marketplace')
    else:
        form = SignUpForm()
    return render(request, 'myapp/signup.html', {'form': form})


def marketplace(request):
    # Simplified Filter: Show everything that is verified and not yet sold
    medicines = Medicine.objects.filter(status='verified').filter(patient=None)
    
    # Debugging: Print to your terminal to see if Django finds anything
    print(f"DEBUG: Found {medicines.count()} verified medicines.")

    # Calculate Total Savings
    # We use .aggregate for better performance (Competitive Programmer style!)
    sold_meds = Medicine.objects.filter(status='sold')
    savings_data = sold_meds.aggregate(
        total_orig=Sum('original_price'), 
        total_resale=Sum('resale_price')
    )
    
    # Handle case where no meds are sold yet to avoid None errors
    total_saved = (savings_data['total_orig'] or 0) - (savings_data['total_resale'] or 0)

    return render(request, 'myapp/marketplace.html', {
        'medicines': medicines,
        'total_saved': total_saved
    })
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def verification_queue(request):
    if request.user.role != User.Role.PHARMACIST or not request.user.is_active:
        return HttpResponseForbidden("Your pharmacist account is either not verified or you don't have permission.")
    
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

def corner_map(request):
    corners = ReMediCorner.objects.all()
    return render(request, 'myapp/map.html', {'corners': corners})



@login_required
def donate_medicine(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            medicine = form.save(commit=False)
            medicine.donor = request.user  # Link the medicine to the logged-in user
            medicine.status = 'pending'    # Ensure it starts as pending
            medicine.save()
            return redirect('marketplace')
    else:
        form = DonationForm()
    return render(request, 'myapp/donate.html', {'form': form})

@login_required
def profile_view(request):
    # Meds the user donated
    my_donations = Medicine.objects.filter(donor=request.user).order_by('-id')
    
    # Meds the user ordered/purchased
    # We filter by patient=request.user
    my_orders = Medicine.objects.filter(patient=request.user).order_by('-ordered_at')
    
    return render(request, 'myapp/profile.html', {
        'donations': my_donations,
        'orders': my_orders
    })

@login_required
def order_medicine(request, med_id):
    medicine = get_object_or_404(Medicine, id=med_id)
    
    if medicine.status == 'verified' and medicine.patient is None:
        medicine.patient = request.user
        medicine.status = 'sold'  # Force the status change here
        medicine.ordered_at = timezone.now()
        medicine.save()
        return render(request, 'myapp/success.html', {'medicine': medicine})
    
    return redirect('marketplace')