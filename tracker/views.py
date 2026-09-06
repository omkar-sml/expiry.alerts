from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import RegisterForm, MedicineForm, FoodForm
from .models import Medicine, FoodItem, Notification

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.username}! Your account was created.")
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    medicines = Medicine.objects.filter(user=request.user)
    foods = FoodItem.objects.filter(user=request.user)

    total_medicines = medicines.count()
    total_foods = foods.count()

    expiring_soon = 0
    expired = 0
    all_items = list(medicines) + list(foods)
    for item in all_items:
        if item.status == "Expiring Soon":
            expiring_soon += 1
        elif item.status == "Expired":
            expired += 1

    critical = sorted(
        [i for i in all_items if i.status in ["Expired", "Expiring Soon"]],
        key=lambda x: x.expiry_date
    )[:5]

    safe = len(all_items) - expiring_soon - expired

    recent_notifs = Notification.objects.filter(user=request.user, is_read=False).order_by('-created_at')[:3]

    # Prepare data for offline phone notification (JS)
    # List of critical items for JS Notification API
    notif_data = []
    for it in critical:
        notif_data.append({
            'name': it.name,
            'type': 'Medicine' if isinstance(it, Medicine) else 'Food',
            'status': it.status,
            'days': it.days_until_expiry,
            'expiry': it.expiry_date.strftime('%d %b %Y'),
        })

    context = {
        'total_medicines': total_medicines,
        'total_foods': total_foods,
        'expiring_soon': expiring_soon,
        'expired': expired,
        'safe': safe,
        'critical': critical,
        'medicines': medicines.order_by('expiry_date')[:3],
        'foods': foods.order_by('expiry_date')[:3],
        'recent_notifs': recent_notifs,
        'notif_data': notif_data,
    }
    return render(request, 'dashboard.html', context)

# ---------- Notifications ----------
@login_required
def notification_list(request):
    notifs = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = notifs.filter(is_read=False).count()
    level = request.GET.get('level')
    if level in ['warning','danger','info']:
        notifs = notifs.filter(level=level)
    return render(request, 'tracker/notifications.html', {'notifications': notifs, 'unread_count': unread_count, 'filter_level': level})

@login_required
def notification_mark_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    messages.success(request, "Notification marked as read.")
    return redirect('notification_list')

@login_required
def notification_mark_all_read(request):
    if request.method == 'POST':
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        messages.success(request, "All notifications marked as read.")
    return redirect('notification_list')

@login_required
def notification_delete(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    if request.method == 'POST':
        notif.delete()
        messages.success(request, "Notification deleted.")
    return redirect('notification_list')

def contact_view(request):
    return render(request, 'tracker/contact.html')

# ---------- Medicine CRUD ----------
@login_required
def medicine_list(request):
    medicines = Medicine.objects.filter(user=request.user)
    filter_status = request.GET.get('filter')
    if filter_status in ['Safe', 'Expiring Soon', 'Expired']:
        medicines = [m for m in medicines if m.status == filter_status]
    else:
        medicines = list(medicines)
    return render(request, 'tracker/medicine_list.html', {'medicines': medicines, 'filter_status': filter_status})

@login_required
def medicine_add(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST)
        if form.is_valid():
            med = form.save(commit=False)
            med.user = request.user
            med.save()
            messages.success(request, f"Medicine '{med.name}' added.")
            return redirect('medicine_list')
    else:
        form = MedicineForm()
    return render(request, 'tracker/medicine_form.html', {'form': form, 'title': 'Add Medicine', 'btn': 'Add Medicine'})

@login_required
def medicine_edit(request, pk):
    med = get_object_or_404(Medicine, pk=pk, user=request.user)
    if request.method == 'POST':
        form = MedicineForm(request.POST, instance=med)
        if form.is_valid():
            form.save()
            messages.success(request, f"Medicine '{med.name}' updated.")
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=med)
    return render(request, 'tracker/medicine_form.html', {'form': form, 'title': 'Edit Medicine', 'btn': 'Update Medicine'})

@login_required
def medicine_delete(request, pk):
    med = get_object_or_404(Medicine, pk=pk, user=request.user)
    if request.method == 'POST':
        name = med.name
        med.delete()
        messages.success(request, f"Medicine '{name}' deleted.")
        return redirect('medicine_list')
    return render(request, 'tracker/medicine_confirm_delete.html', {'item': med, 'type': 'Medicine'})

# ---------- Food CRUD ----------
@login_required
def food_list(request):
    foods = FoodItem.objects.filter(user=request.user)
    filter_status = request.GET.get('filter')
    if filter_status in ['Safe', 'Expiring Soon', 'Expired']:
        foods = [f for f in foods if f.status == filter_status]
    else:
        foods = list(foods)
    return render(request, 'tracker/food_list.html', {'foods': foods, 'filter_status': filter_status})

@login_required
def food_add(request):
    if request.method == 'POST':
        form = FoodForm(request.POST)
        if form.is_valid():
            food = form.save(commit=False)
            food.user = request.user
            food.save()
            messages.success(request, f"Food '{food.name}' added.")
            return redirect('food_list')
    else:
        form = FoodForm()
    return render(request, 'tracker/food_form.html', {'form': form, 'title': 'Add Food Item', 'btn': 'Add Food'})

@login_required
def food_edit(request, pk):
    food = get_object_or_404(FoodItem, pk=pk, user=request.user)
    if request.method == 'POST':
        form = FoodForm(request.POST, instance=food)
        if form.is_valid():
            form.save()
            messages.success(request, f"Food '{food.name}' updated.")
            return redirect('food_list')
    else:
        form = FoodForm(instance=food)
    return render(request, 'tracker/food_form.html', {'form': form, 'title': 'Edit Food Item', 'btn': 'Update Food'})

@login_required
def food_delete(request, pk):
    food = get_object_or_404(FoodItem, pk=pk, user=request.user)
    if request.method == 'POST':
        name = food.name
        food.delete()
        messages.success(request, f"Food '{name}' deleted.")
        return redirect('food_list')
    return render(request, 'tracker/food_confirm_delete.html', {'item': food, 'type': 'Food'})
