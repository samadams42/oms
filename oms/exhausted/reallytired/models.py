import re
from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum

class Region(models.Model):
    regionId = models.IntegerField(primary_key=True)
    regionName = models.CharField(max_length=50)
    regionManager = models.ForeignKey(User, on_delete=models.DO_NOTHING)


class AddressType(models.Model):
    addressTypeId = models.IntegerField(primary_key=True)
    addressType = models.CharField(max_length=50)

    def __str__(self):
        return self.addressType


class Address(models.Model):
    addressId = models.IntegerField(primary_key=True)
    addressTypeId = models.ForeignKey(AddressType, on_delete=models.DO_NOTHING)
    address1 = models.CharField(max_length=100)
    address2 = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2)
    zip = models.IntegerField()
    phone = models.CharField(max_length=15)


class PhoneType(models.Model):
    typeId = models.IntegerField(primary_key=True)
    type_name = models.CharField(max_length=25)


class Phone(models.Model):
    phoneId = models.IntegerField(primary_key=True)
    phone = models.CharField(max_length=10)
    phoneType = models.ForeignKey(PhoneType, on_delete=models.DO_NOTHING)


class Locations(models.Model):
    locationId = models.IntegerField(primary_key=True)
    regionId = models.ForeignKey(Region, on_delete=models.DO_NOTHING)
    locationName = models.CharField(max_length=10)
    locationCity = models.CharField(max_length=25)
    locationState = models.CharField(max_length=4)
    locationPhone = models.ForeignKey(Phone, on_delete=models.DO_NOTHING)
    locationManager = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{0} - {1}, {2}".format(self.locationName, self.locationCity, self.locationState)


class UserDetails(models.Model):
    detailId = models.IntegerField(primary_key=True)
    userId = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=25)
    locationId = models.ForeignKey(Locations, on_delete=models.DO_NOTHING)


class DriverType(models.Model):
    driverTypeId = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=50)

    def __str__(self):
        return self.type


class Driver(models.Model):
    driverId = models.IntegerField(primary_key=True)
    driverTypeId = models.ForeignKey(DriverType, on_delete=models.DO_NOTHING)
    locationId = models.ForeignKey(Locations, on_delete=models.DO_NOTHING)
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=30)
    email = models.EmailField()
    phone = models.CharField(max_length=10)

    def __str__(self):
        return "{1}, {2} ({0})".format(self.driverId, self.lastName, self.firstName)


class ComplianceType(models.Model):
    complianceTypeId = models.IntegerField(primary_key=True)
    complianceType = models.CharField(max_length=40)

    def __str__(self):
        return self.complianceType


class LicenseClass(models.Model):
    classId = models.IntegerField(primary_key=True)
    className = models.CharField(max_length=20)

    def __str__(self):
        return self.className


class Compliance(models.Model):
    complianceId = models.IntegerField(primary_key=True)
    complianceTypeId = models.ForeignKey(ComplianceType, on_delete=models.DO_NOTHING)
    driverId = models.ForeignKey(Driver, on_delete=models.DO_NOTHING, default=None)
    licenseNo = models.CharField(max_length=100)
    classId = models.ForeignKey(LicenseClass, on_delete=models.DO_NOTHING)
    issueDate = models.DateField()
    expirationDate = models.DateField()
    active = models.BooleanField(default=False)

    def __str__(self):
        return self.driverId

class Supplier(models.Model):
    supplierId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return "{0}".format(self.name)


class PartType(models.Model):
    typeId = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=50)

class Part(models.Model):
    partId = models.AutoField(primary_key=True)
    supplierId = models.ForeignKey(Supplier, on_delete=models.DO_NOTHING)
    partNo = models.CharField(max_length=20)
    partDesc = models.CharField(max_length=100)
    partCost = models.DecimalField(max_digits=10, decimal_places=2)
    partQty = models.IntegerField()
    partLocation = models.ForeignKey(Locations, on_delete=models.DO_NOTHING, default=4)
    partCustom1 = models.CharField(max_length=50, null=True)
    partCustom2 = models.CharField(max_length=50, null=True)
    partCustom3 = models.CharField(max_length=50, null=True)
    partType = models.ForeignKey(PartType, on_delete=models.DO_NOTHING)
    partBarcode = models.CharField(max_length=13, null=True)

    def __str__(self):
        return "Part No: {0}, Part Name: {1}".format(self.partNo, self.partDesc)

    @property
    def quantity(self):
        return PartDetail.objects.get(partId_id=self.partId).partInv
    @property
    def cost(self):
        return PartDetail.objects.get(partId_id=self.partId).partInvCost

    @property
    def quantity_january(self):
        return PartTransactionDetail.objects.filter(partId_id=self.partId, txId__date__year=2020, txId__date__month=1).aggregate(Sum('quantity'))['quantity__sum']

    @property
    def quantity_february(self):
        return PartTransactionDetail.objects.filter(partId_id=self.partId, txId__date__year=2020,
                                                    txId__date__month=2).aggregate(Sum('quantity'))['quantity__sum']

    @property
    def cost_february(self):
        cost = PartTransactionDetail.objects.filter(partId_id=self.partId, txId__date__year=2020,
                                                    txId__date__month=2).aggregate(Sum('cost'))['cost__sum']
        if cost == None:
            return '$0.00'
        else:
            cost = round(cost, 2)
            return '$'+str(cost)

    @property
    def quantity_march(self):
        return PartTransactionDetail.objects.filter(partId_id=self.partId, txId__date__year=2020,
                                                    txId__date__month=3).aggregate(Sum('quantity'))['quantity__sum']

    @property
    def quantity_april(self):
        return PartTransactionDetail.objects.filter(partId_id=self.partId, txId__date__year=2020,
                                                    txId__date__month=4).aggregate(Sum('quantity'))['quantity__sum']

    @property
    def quantity_may(self):
        return PartTransactionDetail.objects.filter(partId_id=self.partId, txId__date__year=2020,
                                                    txId__date__month=5).aggregate(Sum('quantity'))['quantity__sum']

    @property
    def quantity_june(self):
        return PartTransactionDetail.objects.filter(partId_id=self.partId, txId__date__year=2020,
                                                    txId__date__month=6).aggregate(Sum('quantity'))['quantity__sum']

    @property
    def quantity_july(self):
        return PartTransactionDetail.objects.filter(partId_id=self.partId, txId__date__year=2020,
                                                    txId__date__month=7).aggregate(Sum('quantity'))['quantity__sum']

    @property
    def quantity_august(self):
        return PartTransactionDetail.objects.filter(partId_id=self.partId, txId__date__year=2020,
                                                    txId__date__month=8).aggregate(Sum('quantity'))['quantity__sum']

    @property
    def quantity_september(self):
        return PartTransactionDetail.objects.filter(partId_id=self.partId, txId__date__year=2020,
                                                    txId__date__month=9).aggregate(Sum('quantity'))['quantity__sum']

    @property
    def quantity_october(self):
        return PartTransactionDetail.objects.filter(partId_id=self.partId, txId__date__year=2020,
                                                    txId__date__month=10).aggregate(Sum('quantity'))['quantity__sum']

    @property
    def quantity_november(self):
        return PartTransactionDetail.objects.filter(partId_id=self.partId, txId__date__year=2020,
                                                    txId__date__month=11).aggregate(Sum('quantity'))['quantity__sum']

    @property
    def quantity_december(self):
        return PartTransactionDetail.objects.filter(partId_id=self.partId, txId__date__year=2020,
                                                    txId__date__month=12).aggregate(Sum('quantity'))['quantity__sum']

class Dock(models.Model):
    dockId = models.IntegerField(primary_key=True)
    dock = models.CharField(max_length=10)
    dock_location = models.ForeignKey(Locations, on_delete=models.DO_NOTHING)


class Lane(models.Model):
    laneId = models.IntegerField(primary_key=True)
    dock = models.ForeignKey(Dock, on_delete=models.DO_NOTHING)
    lane = models.CharField(max_length=10)

class LaneAssignment(models.Model):
    laneAssignmentId = models.IntegerField(primary_key=True)
    lane = models.ForeignKey(Lane, on_delete=models.DO_NOTHING)
    driver = models.ForeignKey(Driver, on_delete=models.DO_NOTHING)
    laneAssignmentDate = models.DateField()


class Tote(models.Model):
    toteId = models.IntegerField(primary_key=True)
    tote = models.CharField(max_length=10)
    lane = models.ForeignKey(Lane, on_delete=models.DO_NOTHING)


class PartDetail(models.Model):
    partDetailId = models.AutoField(primary_key=True)
    partId = models.ForeignKey(Part, on_delete=models.DO_NOTHING)
    locationId = models.ForeignKey(Locations, on_delete=models.DO_NOTHING)
    partInv = models.IntegerField()
    partInvCost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return"{0}".format(self.partInvCost)


class Reconcile(models.Model):
    reconcileId = models.AutoField(primary_key=True)
    reconcileDate = models.DateTimeField()
    reconciledBy = models.ForeignKey(User, on_delete=models.DO_NOTHING)


class ReconcileLog(models.Model):
    reconcileLogId = models.AutoField(primary_key=True)
    partId = models.ForeignKey(Part, on_delete=models.DO_NOTHING)
    oldCount = models.IntegerField()
    newCount = models.IntegerField()
    diff = models.IntegerField()


class PartTransactionTypes(models.Model):
    typeId = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=20)


class PartTransactions(models.Model):
    txId = models.IntegerField(primary_key=True)
    txNumber = models.CharField(max_length=25, default=0)
    typeId = models.ForeignKey(PartTransactionTypes, on_delete=models.DO_NOTHING, default=1)
    driverId = models.ForeignKey(Driver, on_delete=models.DO_NOTHING)
    userId = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    date = models.DateTimeField(auto_now_add=True)

    @property
    def total_cost(self):
        total_cost = PartTransactionDetail.objects.filter(txId_id=self.txId).aggregate(Sum('cost'))['cost__sum']
        if total_cost != None:
            total_cost=round(total_cost, 2)
        return total_cost


class BarcodeType(models.Model):
    typeId = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=20)


class Barcode(models.Model):
    barcodeId = models.IntegerField(primary_key=True)
    barcode = models.CharField(max_length=20)
    typeId = models.ForeignKey(BarcodeType, on_delete=models.DO_NOTHING)
    partId = models.ForeignKey(Part, on_delete=models.DO_NOTHING, blank=True)
    txId = models.ForeignKey(PartTransactions, on_delete=models.DO_NOTHING, blank=True)
    txId = models.ForeignKey(PartTransactions, on_delete=models.DO_NOTHING, blank=True)


class PartTransactionDetail(models.Model):
    detailId = models.IntegerField(primary_key=True)
    txId = models.ForeignKey(PartTransactions, on_delete=models.DO_NOTHING)
    partId = models.ForeignKey(Part, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

class TransactionType (models.Model):
    type_id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=20)


class Transaction(models.Model):
    tx_id = models.IntegerField(primary_key=True)
    tx_user = models.ForeignKey(User, related_name="transaction_user", on_delete=models.DO_NOTHING)
    tx_number = models.CharField(max_length=25)
    tx_type = models.ForeignKey(TransactionType, related_name="transaction_type", on_delete=models.DO_NOTHING)
    tx_driver = models.ForeignKey(Driver, related_name="transaction_driver", on_delete=models.DO_NOTHING, null=True)
    tx_tote = models.ForeignKey(Dock, related_name="transaction_tote", on_delete=models.DO_NOTHING, null=True)
    tx_date = models.DateTimeField(auto_now=True)
    tx_location = models.ForeignKey(Locations, related_name="location", on_delete=models.DO_NOTHING)

    def get_by_driver(self, driver):
        txs = self.objects.filter(tx_driver=driver)
        return txs

    def get_by_location(self, location):
        txs = self.objects.filter(tx_location=location)
        return txs

    def get_by_region(self, region):
        txs = self.objects.filter(tx_location__location_region=region)


class TransactionDetail(models.Model):
    tx_detail_id = models.IntegerField(primary_key=True)
    tx_id = models.ForeignKey(Transaction, on_delete=models.DO_NOTHING)
    part = models.ForeignKey(Part, on_delete=models.DO_NOTHING)
    quantity = models.IntegerField()

    def get_cost_by_part(self):
        part = Part.objects.filter(part=self.part)
        cost = part.part_cost * self.quantity
        return cost

    def get_total_cost(self):
        txs = self.objects.filter(tx_id=self.tx_id)
        total_cost = 0.00
        for tx in txs:
            part = Part.objects.filter(part=tx.part)
            total_cost += (part.part_cost * tx.quantity)
        return total_cost

    def get_total_parts(self):
        txs = self.objects.filter(tx_id=self.tx_id)
        total_parts = 0
        for tx in txs:
            total_parts += tx.quantity
        return total_parts


class Barcode(models.Model):
    barcode = models.CharField(primary_key=True, max_length=(255))
    part = models.ForeignKey(Part, on_delete=models.CASCADE)
    default_quantity = models.IntegerField(default=1)

