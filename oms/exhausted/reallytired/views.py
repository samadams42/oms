import csv
from datetime import datetime
from django.db import connection
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from .tokens import account_activation_token
from .forms import *
#from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum
from decimal import Decimal

parts = Part.objects.all().values('partId', 'partNo', 'partDesc', 'partCost', 'supplierId__name', 'partdetail__partInv',
                                  'partdetail__partInvCost').order_by('-supplierId_id')
user = ''
today = datetime.now()


def reg_view(request):
    msg = ''
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'ACTION REQUIRED: Please confirm your email address to activate your account.'
            message = render_to_string('acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            msg = 'Email sent. Please confirm your email address.'
            return redirect('login_new')
            return HttpResponse('Please check your email.')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'msg': msg, 'form': form})


def login_new(request):
    return render(request, 'login_newuser.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('/login')
        return HttpResonse('Thank you for confirming your email! You can now login to your account.')
    else:
        return HttpResponse('Activation link is invalid!')


def login_view(request):
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request, username=username, password=password)
        login(request, user)
        return redirect('/')
    context = {
        'form': form,
    }
    return render(request, 'login.html', context=context)


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully!')
            return redirect('/login')
    else:
        form = UserRegisterForm()
    return render(request, 'register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('../login')


### DASHBOARD ###
@login_required()
def index(request):
    print(request.user)
    user = User.objects.get(username=request.user)
    print(user.first_name)
    print(user.last_name)
    print(user.email)
    context = {
        'parts': parts,
        'user': user
    }
    return render(request, 'index.html', context=context)


### INVENTORY ###
@login_required()
def inventory(request):
    locations = Locations.objects.all()
    parts = Part.objects.all().order_by('-supplierId_id')

    context = {
        'parts': parts,
        'locations': locations
    }
    return render(request, 'inventory.html', context=context)


@login_required()
def inv_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="parts.csv"'
    writer = csv.writer(response)
    writer.writerow(['PartNo', 'PartDescription', 'Cost Per Part', 'Part Inventory', 'Part Cost'])
    parts = Part.objects.all().values_list('partNo', 'partDesc', 'partCost', 'partdetails__partInv',
                                           'partdetails__partInvCost')
    for part in parts:
        writer.writerow(part)
    return response


@login_required()
@csrf_exempt
def inv_add(request):
    locations = Locations.objects.all()
    parts = Part.objects.all().values('partId', 'partNo', 'partDesc', 'partCost', 'supplierId__name',
                                      'partdetail__partInv', 'partdetail__partInvCost')
    form = AddPartForm(request.POST or None)
    print(form.is_valid())
    if form.is_valid():
        form.save()
        return redirect('inventory')
    else:
        print(form.errors)
    context = {
        'form': form,
        'parts': parts,
        'locations': locations,
    }
    return render(request, 'inv_add.html', context=context)


@login_required()
def inv_details(request, partId):
    obj = get_object_or_404(Part, partId=partId)
    parts = Part.objects.all().order_by('-supplierId_id')

    if not obj:
        obj = get_object_or_404(Part, partId=partId)

    if (obj.supplierId_id == 2):
        image = Part.objects.get(partId=partId).partNo + ".jpg"
    else:
        image = 'noPhotoFound.png'

    context = {
        'parts': parts,
        'obj': obj,
        'image': image
    }
    return render(request, 'inv_details.html', context=context)


@csrf_exempt
def inv_edit(request, partId):
    locations = Locations.objects.all()
    obj = get_object_or_404(Part, partId=partId)
    parts = Part.objects.all().order_by('-supplierId_id')
    if (obj.supplierId_id == 2):
        image = Part.objects.get(partId=partId).partNo + ".jpg"
    else:
        image = 'noPhotoFound.png'

    if request.method == "POST":
        form = EditPartForm(request.POST, instance=obj)
        print(request.method)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            d = PartDetail.objects.get(partId=partId)
            d.partInv = form.data['quantity']
            d.save()
            d.partInvCost = int(form.data['quantity']) * Decimal(form.data['partCost'])
            d.save()
            return redirect('inventory')
    else:
        form = EditPartForm(instance=obj)
    return render(request, 'inv_edit.html', {'form': form, 'locations': locations, 'parts': parts, 'image': image})


@login_required()
def inv_delete(request, partId):
    Part.objects.filter(partId=partId).delete()
    locations = Locations.objects.all()
    parts = Part.objects.all().values('partId', 'partNo', 'partDesc', 'partCost', 'supplierId__name',
                                      'partdetail__partInv', 'partdetail__partInvCost')
    context = {
        'parts': parts,
        'locations': locations,
    }
    return render(request, 'inventory.html', context=context)


### ORDERS ###
@login_required()
def orders(request):
    return render(request, 'orders.html')


### DRIVERS ###
@login_required()
def drivers(request):
    parts = Part.objects.all()
    context = {
        'parts':parts
    }
    return render(request, 'drivers.html', context=context)


### TRAILERS ###
@login_required()
def trailers(request):
    return render(request, 'trailers.html')


### POS ###
@login_required()
def pos(request):
    txs = PartTransactions.objects.all()
    user = request.user
    details = {}
    context = {
        'txs': txs,
        'details': details,
        'user': user
    }
    return render(request, 'pos.html', context=context)


@csrf_exempt
def select_driver(request):
    parts = Part.objects.all()
    drivers = Driver.objects.all()
    if request.method == "POST":
        driver = get_object_or_404(Driver, driverId=request.POST.get('driver'))
        txId = PartTransactions.objects.all().order_by('-txId')[0].txId + 1
        txNumber = str(today.year) + "-" + driver.locationId.locationName + "-" + (str(txId).zfill(4))
        print(request.user.id)
        tx = PartTransactions(txId=txId, typeId_id=1, driverId=driver,
                              userId_id=User.objects.get(id=request.user.id).id,
                              txNumber=txNumber)
        tx.save()
        return redirect('/pos/inv_req/' + str(txId))
    context = {
        'drivers': drivers,
        'parts': parts
    }
    return render(request, 'select_driver.html', context=context)


def print_barcodes(request):
    parts = Part.objects.all()
    return render(request, 'barcode.html', context={'parts': parts})


@csrf_exempt
def inv_req(request, txId):
    parts = Part.objects.all()
    ge_parts = Part.objects.filter(supplierId_id=2)
    arrow_parts = Part.objects.filter(supplierId_id=1)
    total = PartTransactionDetail.objects.filter(txId_id=txId).aggregate(Sum('cost'))['cost__sum']
    print(type(total))
    if total is not None:
        total = round(total, 2)
    else:
        total = round(0.00, 2)
    tx = get_object_or_404(PartTransactions, txId=txId)
    tx_list = PartTransactionDetail.objects.filter(txId_id=tx.txId)
    driver = tx.driverId
    context = {
        'parts': parts,
        'ge_parts': ge_parts,
        'arrow_parts': arrow_parts,
        'tx_list': tx_list,
        'tx': tx,
        'driver': driver,
        'total': total
    }
    if request.method == "POST":
        print(request.POST)
        part = get_object_or_404(Part, partId=request.POST.get('part'))
        partId = part.partId
        print(partId)
        details = PartDetail.objects.get(partId_id=partId)
        details.partInv -= 1
        details.save()
        if (PartTransactionDetail.objects.filter(txId_id=txId).count() > 0) and (
                PartTransactionDetail.objects.filter(txId_id=txId, partId_id=partId).count() > 0):
            print(txId)
            print(partId)
            d = PartTransactionDetail.objects.get(txId=PartTransactions.objects.get(txId=txId),
                                                  partId=Part.objects.get(partId=partId))
            d.quantity += 1
            d.cost += part.partCost
            d.save()
            return redirect('/pos/inv_req/' + str(txId))
        else:
            new = PartTransactionDetail(partId_id=partId, txId_id=txId, quantity=1, cost=part.partCost)
            new.save()
            return redirect('/pos/inv_req/' + str(txId))

    return render(request, 'inv_req.html', context=context)


def inv_req_delete(request, partId, txId):
    tx = get_object_or_404(PartTransactions, txId=txId)
    txId = tx.txId
    part = get_object_or_404(Part, partId=partId)
    d = PartTransactionDetail.objects.get(txId=PartTransactions.objects.get(txId=txId),
                                          partId=Part.objects.get(partId=partId))
    if d.quantity == 1:
        d.delete()
    else:
        d.quantity -= 1
        d.cost += part.partCost
        d.save()
    return redirect('/pos/inv_req/' + str(txId))


### REPORTS ###
@login_required()
def reports(request):
    return render(request, 'reports.html')


@login_required()
def inv_exp(request, txId):
    tx = get_object_or_404(PartTransactions, txId=txId)
    details = PartTransactionDetail.objects.filter(txId=tx)
    context = {
        'tx': tx,
        'details': details
    }
    return render(request, 'inv_exp.html', context=context)


def rolling_parts(request):
    parts = Part.objects.all().order_by('-supplierId_id')
    locations = Locations.objects.all()
    location = 6
    year = 2020

    context = {
        'location':location,
        'year':year,
        'parts': parts,
        'locations': locations,
    }
    return render(request, 'rolling_parts.html', context=context)

def monthly_driver(request):
    parts = Part.objects.all()
    locations = Locations.objects.all()
    location = 6
    year = 2020

    context = {
        'location':location,
        'year':year,
        'parts': parts,
        'locations': locations,
    }
    return render(request, 'monthly_driver.html', context=context)

def weekly_driver(request):
    parts = Part.objects.all()
    context = {
        'parts':parts
    }
    return render(request, 'weekly_driver.html', context=context)