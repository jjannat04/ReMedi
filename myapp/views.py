from django.shortcuts import render, get_object_or_404, redirect
from .models import Medicine, ReMediCorner
from django.db.models import Sum
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from .models import User
from .forms import DonationForm

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
    # Fetch donations made by the current user
    my_donations = Medicine.objects.filter(donor=request.user).order_by('-id')
    return render(request, 'myapp/profile.html', {'donations': my_donations})