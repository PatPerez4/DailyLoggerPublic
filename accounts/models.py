from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
# Create your models here.



class Employee(models.Model):
    username = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    full_Name = models.CharField(max_length=200, null=True)
    number_of_Tickets_Completed_Today = models.CharField(max_length=200, null=True)
    dateCreated = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return self.full_Name

class Day(models.Model):
    productivity = models.CharField(max_length=200, null=True)
    dateCreated = models.DateTimeField(auto_now_add=True, null=True)
    def __str__(self):
        return str(self.dateCreated)
#class Site(models.Model):
#class Services(models.Model):

class Log(models.Model):
    ticket_Number = models.CharField(max_length=200, null=True)
    cognito_Number = models.CharField(max_length=200, null=True)
    #employee = models.ForeignKey(Employee, null=True, on_delete=models.SET_NULL)
    employee = models.CharField(max_length=200, null=True)
    site = models.CharField(max_length=200, null=True)
    SERVICES = (
            ('Iptv', 'Iptv'),
            ('Voice', 'Voice'),
            ('Data', 'Data'),
            ('Analog', 'Analog'),
            ('Outage', 'Outage'),
            ('Miscellaneous', 'Miscellaneous'),
            ('All_Services', 'All_Services'),
            )
    services = models.CharField(max_length=500, null=True, choices=SERVICES)
    SOURCE = (
            ('Install', 'Install'),
            ('Email Chain', 'Email Chain'),
            ('Fision Enterprise', 'Fision Enterprise'),
            ('Project', 'Project'),
            ('Collections', 'Collections'),
            ('Miscellaneous', 'Miscellaneous'),
            ('Cog Call Back', 'Cog Call Back'),
            ('Inbound Tech Call', 'Inbound Tech Call'),
            ('Inbound Account Manager', 'Inbound Account Manager'),
            ('Inbound CS Agent', 'Inbound CS Agent'),
            ('Salisbury Gen tech support', 'Salisbury Gen tech support'),
            ('Fiber support', 'Fiber support'),
            ('change orders/disconnects/reconnects', 'change orders/disconnects/reconnects'),
            ('Trouble Ticket', 'Trouble Ticket'),
            ('Secure Plus', 'Secure Plus'),
            ('Collection Disconnect', 'Collection Disconnect'),
            )
    source = models.CharField(max_length=500, null=True, choices=SOURCE)
    TROUBLESHOOT_REQUIRED = (
            ('No', 'No'),
            ('Yes', 'Yes'),
            )
    troubleshoot_Required = models.CharField(max_length=500, null=True, choices=TROUBLESHOOT_REQUIRED)
    notes = models.CharField(max_length=500, null=True)
    STATUS = (
            ('Resolved With Dispatch', 'Resolved With Dispatch'),
            ('Resolved no dispatch', 'Resolved no dispatch'),
            ('Resolved-NTF', 'Resolved-NTF'),
            ('Pending Dispatch', 'Pending Dispatch'),
            ('Supervisor escalation', 'Supervisor escalation'),
            ('Jira escalation', 'Jira escalation'),
            ('Avoidable Escalation', 'Avoidable Escalation'),
            ('Miscellaneous', 'Miscellaneous'),
            ('Invalid VNN assigned', 'Invalid VNN assigned'),
            ('Number not assigned', 'Number not assigned'),
            ('Provisioning', 'Provisioning'),
            ('Enable secure plus', 'Enable secure plus'),
            ('Remove eero secure plus', 'Remove eero secure plus'),
            ('Eero secure plus not active', 'Eero secure plus not active'),
            ('Outage', 'Outage'),
            ('CX Education', 'CX Education'),
            ('Tech Education', 'Tech Education'),
            )
    status = models.CharField(max_length=500, null=True, choices=STATUS)
    resolution = models.CharField(max_length=500, null=True)
    #created = models.DateTimeField(default=datetime.now())
    submission_Timer = models.CharField(max_length=200, null=True)
    clock = models.CharField(max_length=200, null=True)
    COMPLETION_STATUS = (
            ('Submitted', 'Submitted'),
            ('Reviewed', 'Reviewed'),
            ('Complete', 'Complete'),
            )
    completion_Status = models.CharField(max_length=500, null=True, choices=COMPLETION_STATUS)
    dateCreated = models.DateTimeField(auto_now_add=True, null=True)
    dateReviewed = models.DateTimeField(auto_now_add=True, null=True)
    SECURE_PLUS_CHECKER = (
            ('Eero Secure Plus Enabled', 'Eero Secure Plus Enabled'),
            ('Cannot activate Secure Plus', 'Cannot activate Secure Plus'),
            ('Removed Eero Secure Plus', 'Removed Eero Secure Plus'),
            )
    secure_Plus_Checker = models.CharField(max_length=500, null=True, choices=SECURE_PLUS_CHECKER)

    def __str__(self):
        return self.ticket_Number

class Ddt(models.Model):
    action = models.CharField(max_length=200, null=True)
    CID = models.CharField(max_length=200, null=True)
    SUB_Start = models.CharField(max_length=200, null=True)
    SUB_Stop = models.CharField(max_length=200, null=True)
    amdocs_Plus = models.CharField(max_length=200, null=True)
    serial = models.CharField(max_length=200, null=True)
    dateCreated = models.DateTimeField(auto_now_add=True, null=True)
    completion_Status = models.CharField(max_length=200, null=True)
    def __str__(self):
        return str(self.CID)

class NoSchedule(models.Model):
    MDU_ID = models.CharField(max_length=200, null=True)
    MNAME = models.CharField(max_length=200, null=True)
    CustomerNumber = models.CharField(max_length=200, null=True)
    SITE_ID = models.CharField(max_length=200, null=True)
    CustomerName = models.CharField(max_length=200, null=True)
    FullAddress = models.CharField(max_length=200, null=True)
    TicketNumber = models.CharField(max_length=200, null=True)
    OPRID = models.CharField(max_length=200, null=True)
    ContactEmployee = models.CharField(max_length=200, null=True)
    TroubleCallReceived = models.CharField(max_length=200, null=True)
    CallReason = models.CharField(max_length=200, null=True)
    NoScheduleReason = models.CharField(max_length=200, null=True)
    dateCreated = models.DateTimeField(auto_now_add=True, null=True)
    completion_Status = models.CharField(max_length=200, null=True)
    def __str__(self):
        return str(self.TicketNumber)

class Provisioning(models.Model):
    MDU_ID = models.CharField(max_length=200, null=True)
    PROPERTYNAME = models.CharField(max_length=200, null=True)
    CUST_ACCT = models.CharField(max_length=200, null=True)
    SITE_ID = models.CharField(max_length=200, null=True)
    CUSTOMERNAME = models.CharField(max_length=200, null=True)
    FULLADDRESS = models.CharField(max_length=200, null=True)
    ONTSERIAL = models.CharField(max_length=200, null=True)
    OFFERNUM = models.CharField(max_length=200, null=True)
    ORDERNUMBER = models.CharField(max_length=200, null=True)
    ORDERDATE = models.CharField(max_length=200, null=True)
    CUSTOMEREFFECTIVEDATE = models.CharField(max_length=200, null=True)
    BILLINGEFFECTIVEDATE = models.CharField(max_length=200, null=True)
    ORDERTYPE = models.CharField(max_length=200, null=True)
    COMPLETE = models.CharField(max_length=200, null=True)
    ORDERSTATUS = models.CharField(max_length=200, null=True)
    OLDSERVICE = models.CharField(max_length=200, null=True)
    NEWSERVICE = models.CharField(max_length=200, null=True)
    dateCreated = models.DateTimeField(auto_now_add=True, null=True)
    completion_Status = models.CharField(max_length=200, null=True)
    def __str__(self):
        return str(self.OFFERNUM)

class Duplicate(models.Model):
    MDU_ID = models.CharField(max_length=200, null=True)
    PROPERTYNAME = models.CharField(max_length=200, null=True)
    CUST_ACCT = models.CharField(max_length=200, null=True)
    SITE_ID = models.CharField(max_length=200, null=True)
    CUSTOMERNAME = models.CharField(max_length=200, null=True)
    FULLADDRESS = models.CharField(max_length=200, null=True)
    ONTSERIAL = models.CharField(max_length=200, null=True)
    OFFERNUM = models.CharField(max_length=200, null=True)
    ORDERNUMBER = models.CharField(max_length=200, null=True)
    ORDERDATE = models.CharField(max_length=200, null=True)
    CUSTOMEREFFECTIVEDATE = models.CharField(max_length=200, null=True)
    BILLINGEFFECTIVEDATE = models.CharField(max_length=200, null=True)
    ORDERTYPE = models.CharField(max_length=200, null=True)
    COMPLETE = models.CharField(max_length=200, null=True)
    ORDERSTATUS = models.CharField(max_length=200, null=True)
    OLDSERVICE = models.CharField(max_length=200, null=True)
    NEWSERVICE = models.CharField(max_length=200, null=True)
    dateCreated = models.DateTimeField(auto_now_add=True, null=True)
    completion_Status = models.CharField(max_length=200, null=True)
    def __str__(self):
        return str(self.OFFERNUM)

class CollectionDisconnect(models.Model):
    AccountNumber = models.CharField(max_length=200, null=True)
    OfferNumber = models.CharField(max_length=200, null=True)
    ActionSuspendDowngrade = models.CharField(max_length=200, null=True)
    PropertyName = models.CharField(max_length=200, null=True)
    Date = models.CharField(max_length=200, null=True)
    dateCreated = models.DateTimeField(auto_now_add=True, null=True)
    completion_Status = models.CharField(max_length=200, null=True)
    def __str__(self):
        return str(self.OfferNumber)