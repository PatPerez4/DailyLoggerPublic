from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta, timezone, date
from django.views.decorators.csrf import csrf_exempt
from django.utils.datastructures import MultiValueDictKeyError
from django.db import connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.forms import formset_factory

from pyexcel_xls import get_data as xls_get
from pyexcel_xlsx import get_data as xlsx_get
import pytz
import json
import openpyxl
import csv, io

from .models import *
from .forms import LogForm, ListForm, RegisterForm, EmployeeForm
from .filters import LogFilter

utc=pytz.UTC

def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = RegisterForm()
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                user = form.save()
                username = form.cleaned_data.get('username')

                messages.success(request, 'Account was created for ' + username)

                return redirect('login')

        context = {'form':form}
        return render(request, 'accounts/register.html', context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user= authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Username or Password is incorrect')
        context = {}
        return render(request, 'accounts/login.html', context)

def logoutUser(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home(request):
    querys = Log.objects.raw('SELECT *, ticket_Number AS id FROM accounts_log WHERE dateCreated <= now() - interval 30 minute AND source = "Install" AND completion_Status = "Submitted"')
    length = len(querys)
    if length == 1:
        messages.error(request, 'There is ' + str(length) + ' Cognito left backed up past 30 minutes')
    elif length > 1:
        messages.error(request, 'There are ' + str(length) + ' Cognitos left backed up past 30 minutes')
    logs = Log.objects.filter(completion_Status='Reviewed')
    name = str(request.user.employee)
    context = {'logs' : logs, 'querys' : querys, 'length' : length, 'name' : name}
    return render(request, 'accounts/index.html', context)

@login_required(login_url='login')
def data(request):
    logs = Log.objects.raw('WITH emp_stats AS (SELECT employee, count(*) as "total", sum(case when source = "Install" then 1 else 0 end) AS cogTotal, sum(case when source = "change orders/disconnects/reconnects" then 1 else 0 end) AS changeTotal, sum(case when source = "Trouble Ticket" then 1 else 0 end) AS troubleTotal, sum(case when source = "Collection Disconnect" then 1 else 0 end) AS collectionTotal, sum(case when source = "Secure Plus" then 1 else 0 end) AS eeroTotal, sum(case when source != "Install" and source != "change orders/disconnects/reconnects" and source != "Trouble Ticket" and source != "Collection Disconnect" and source != "Secure Plus" then 1 else 0 end) AS manualTotal FROM accounts_log WHERE DATE(dateCreated) = DATE(NOW()) GROUP BY employee) SELECT @id := @id + 1 id, employee, total, cogTotal, changeTotal, troubleTotal, collectionTotal, eeroTotal, manualTotal FROM emp_stats, (SELECT @id := 0) n;')
    context = {'logs' : logs}
    return render(request, 'accounts/data.html', context)

@login_required(login_url='login')
def cogreview(request):
    logs = Log.objects.filter(completion_Status='Submitted')
    context = {'logs' : logs}
    return render(request, 'accounts/cogreview.html', context)


@login_required(login_url='login')
def log(request):
    form = LogForm()
    if request.method == 'POST':
        form = LogForm(request.POST)
        if form.is_valid() and request.POST.get('ticket_Number').isnumeric():
            if request.POST.get('source') == 'Cog Call Back':
                email = EmailMessage(
                    'Cog Call Back created for #' + request.POST.get('ticket_Number') + '',
                    'Relevant notes: ',
                    settings.EMAIL_HOST_USER,
                    ['patrick.perez@hotwirecommunication.com'],
                )
                email.fail_silently=False
                email.send()
            new_form = form.save(commit=False)
            new_form.employee = request.user.employee
            new_form.completion_Status = 'Reviewed'
            new_form.save()
            return redirect('/autoLog')
        else:
            messages.warning(request, 'Provided ticket number is in non-numeric format')
    context = {'form':form}
    return render(request, 'accounts/log.html', context)

@login_required(login_url='login')
def update(request, pk):
    log = Log.objects.get(id=pk)
    form = LogForm(instance=log)
    if request.method == 'POST':
        form = LogForm(request.POST, instance=log)
        if form.is_valid():
            form.save()
            return redirect('/autoLog')
    context = {'form':form, 'log':log}
    return render(request, 'accounts/update.html', context)

@login_required(login_url='login')
def autoLog(request):
    logs = Log.objects.filter(completion_Status='Reviewed') & Log.objects.filter(employee=request.user.employee)
    messages.info(request, 'Please remember for change order and trouble tickets to always close the amdocs order or schedule a technician if necessary. If you cannot close the order on amdocs, click the button to reassign the order to Cesare')
    context = {'logs' : logs}
    return render(request, 'accounts/autoLog.html', context)

@login_required(login_url='login')
def dailyWork(request):
    #logs = Log.objects.filter(dateCreated=datetime.today()) & Log.objects.filter(employee=request.user.employee)
    querys = Log.objects.raw('SELECT * FROM accounts_log WHERE employee = "' + str(request.user.employee) + '" AND completion_Status = "Complete" AND CAST(dateCreated as DATE) = CAST(CURRENT_TIMESTAMP() AS DATE)')
    length = len(querys)
    if length == 1:
        messages.info(request, 'You have completed ' + str(length) + ' ticket today')
    elif length > 1:
        messages.info(request, 'You have completed ' + str(length) + ' tickets today')
    logs = Log.objects.raw('SELECT * FROM accounts_log WHERE employee = "' + str(request.user.employee) + '" AND CAST(dateCreated as DATE) = CAST(CURRENT_TIMESTAMP() AS DATE)',)
    context = {'logs' : logs, 'querys' : querys, 'length' : length}
    return render(request, 'accounts/dailyWork.html', context)

def export(request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=export.csv'

    # opts = queryset.model._meta
    # field_names = [field.name for field in opts.fields]

    writer = csv.writer(response)
    # write a first row with header information
    # writer.writerow(field_names)

    # write data rows
    # I suggest you to check what output of `queryset`
    # because your `queryset` using `cursor.fetchall()`
    # print(queryset)
    for row in queryset:
        writer.writerow(row)
    return response

@login_required(login_url='login')
def view(request):
    query = Log.objects.all().order_by('-dateCreated')
    myFilter = LogFilter(request.GET, queryset=query)
    myQuery = myFilter.qs
    paginator = Paginator(myQuery, 30)
    page = request.GET.get('page')
    try:
        logs = paginator.page(page)
    except PageNotAnInteger:
        logs = paginator.page(1)
    except EmptyPage:
        logs = paginator.page(paginator.num_pages)
    #query = Log.objects.all().order_by('-dateCreated')
    #page = request.GET.get('page', 1)
    #paginator = Paginator(query, 10)
    #myFilter = LogFilter(request.GET, queryset=query)
    #logs = paginator.page(page)
    #logs = myFilter.qs
    #querystring = request.GET.copy()
    new_request = ''
    for i in request.GET:
        if i != 'page':
            val = request.GET.get(i)
            new_request += f"&{i}={val}"
    querySecond = Log.objects.raw('SELECT id FROM accounts_log WHERE CAST(dateCreated AS DATE) = CAST(CURRENT_TIMESTAMP() AS DATE) AND completion_Status = "Completed"')
    totalTickets = len(querySecond)
    totalTickets = str(totalTickets)
    context = {'logs' : logs, 'myFilter' : myFilter, 'new_request' : new_request, 'totalTickets' : totalTickets, myQuery : 'myQuery'}
    return render(request, 'accounts/view.html', context)

@login_required(login_url='login')
def complete(request, pk):
    log = Log.objects.get(id=pk)
    if request.method == "POST":
        log.completion_Status = 'Complete'
        timeCreate = log.dateCreated.time()
        now = datetime.now().time()
        timeDif = datetime.combine(date.today(), now) - datetime.combine(date.today(), timeCreate)
        s = timeDif.seconds
        hours, remainder = divmod(s, 3600)
        minutes, seconds = divmod(remainder, 60)
        log.clock = '{} hours, {} minutes, {} seconds'.format(int(hours), int(minutes), int(seconds))
        log.save()
        return redirect('/autoLog')
    context = {'log':log}
    return render(request, 'accounts/complete.html', context)

@login_required(login_url='login')
def sendBackTroubleTicket(request, pk):
    log = Log.objects.get(id=pk)
    num = log.ticket_Number
    noSchedule = NoSchedule.objects.get(TicketNumber=num)
    if request.method == "POST":
        noSchedule.completion_Status = 'Submitted'
        noSchedule.save()
        log.delete()
        return redirect('/autoLog')
    context = {'log':log, 'noSchedule':noSchedule}
    return render(request, 'accounts/sendBackTroubleTicket.html', context)

@login_required(login_url='login')
def sendBackChangeOrder(request, pk):
    log = Log.objects.get(id=pk)
    num = log.ticket_Number
    provisioning = Provisioning.objects.get(OFFERNUM=num)
    if request.method == "POST":
        provisioning.completion_Status = 'Submitted'
        provisioning.save()
        log.delete()
        return redirect('/autoLog')
    context = {'log':log, 'provisioning':provisioning}
    return render(request, 'accounts/sendBackChangeOrder.html', context)

@login_required(login_url='login')
def sendBackDdt(request, pk):
    log = Log.objects.get(id=pk)
    num = log.ticket_Number
    ddt = Ddt.objects.get(CID=num)
    if request.method == "POST":
        ddt.completion_Status = 'Submitted'
        ddt.save()
        log.delete()
        return redirect('/autoLog')
    context = {'log':log, 'ddt':ddt}
    return render(request, 'accounts/sendBackDdt.html', context)

@login_required(login_url='login')
def sendBackCollectionDisconnect(request, pk):
    log = Log.objects.get(id=pk)
    num = log.ticket_Number
    collectionDisconnect = CollectionDisconnect.objects.get(OfferNumber=num)
    if request.method == "POST":
        collectionDisconnect.completion_Status = 'Submitted'
        collectionDisconnect.save()
        log.delete()
        return redirect('/autoLog')
    context = {'log':log, 'collectionDisconnect':collectionDisconnect}
    return render(request, 'accounts/sendBackCollectionDisconnect.html', context)

@login_required(login_url='login')
def sendToBoss(request, pk):
    log = Log.objects.get(id=pk)
    if request.method == "POST":
        log.employee = 'Cesare Johnson'
        if log.notes:
            log.notes = log.notes + ' -' + str(request.user.employee)
        else:
            log.notes = ' -' + str(request.user.employee)
        log.save()
        return redirect('/autoLog')
    context = {'log':log}
    return render(request, 'accounts/sendToBoss.html', context)

@login_required(login_url='login')
def delete(request, pk):
    log = Log.objects.get(id=pk)
    if request.method == "POST":
        log.delete()
        return redirect('/autoLog')
    context = {'log':log}
    return render(request, 'accounts/delete.html', context)

@login_required(login_url='login')
def t2Prov(request):
    context = {}
    if request.method == "GET":
        return render(request, 'accounts/t2Prov.html', context)
    try:
        csv_file = request.FILES['file']
    except MultiValueDictKeyError:
        return render(request, 'accounts/t2Prov.html')
    
    if request.method == "POST":
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        
        for column in csv.reader(io_string, delimiter=','):
            try:
                if 'MDU' not in column[0] and 'Textbox' not in column[0] and 'Report Run' not in column[0]:
                    if not NoSchedule.objects.filter(TicketNumber = column[6]).exists():
                        _, created = NoSchedule.objects.update_or_create( 
                        MDU_ID=column[0],
                        MNAME=column[1],
                        CustomerNumber=column[2],
                        SITE_ID=column[3],
                        CustomerName=column[4],
                        FullAddress=column[5],
                        TicketNumber=column[6],
                        OPRID=column[7],
                        ContactEmployee=column[8],
                        TroubleCallReceived=column[9],
                        CallReason=column[10],
                        NoScheduleReason=column[11],
                        completion_Status='Submitted'
                    )
            except IndexError:
                pass
        return redirect('/t2ProvGrabber')
    context = {}
    return render(request, 'accounts/t2Prov.html', context)

@login_required(login_url='login')
def troubleTicket(request):
    context = {}
    if request.method == "GET":
        return render(request, 'accounts/troubleTicket.html', context)
    try:
        csv_file = request.FILES['file']
    except MultiValueDictKeyError:
        return render(request, 'accounts/troubleTicket.html')
    
    if request.method == "POST":
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        
        for column in csv.reader(io_string, delimiter=','):
            try:
                if 'TroubleCall' not in column[0] and 'Textbox' not in column[0] and 'Report Run' not in column[0]:
                    if not NoSchedule.objects.filter(TicketNumber = column[1]).exists():
                        _, created = NoSchedule.objects.update_or_create( 
                        MDU_ID=column[2],
                        MNAME=column[3],
                        CustomerNumber=column[4],
                        SITE_ID=column[5],
                        CustomerName=column[6],
                        FullAddress=column[7],
                        TicketNumber=column[1],
                        OPRID=column[8],
                        ContactEmployee=column[9],
                        TroubleCallReceived=column[0],
                        CallReason=column[10],
                        NoScheduleReason=column[11],
                        completion_Status='Submitted'
                    )
            except IndexError:
                pass
        return redirect('/t2ProvGrabber')
    context = {}
    return render(request, 'accounts/troubleTicket.html', context)

def strip_non_ascii(string):
    ''' Returns the string without non ASCII characters'''
    stripped = (c for c in string if 0 < ord(c) < 127)
    return ''.join(stripped)

@login_required(login_url='login')
def changeOrder(request):
    context = {}
    if request.method == "GET":
        return render(request, 'accounts/changeOrder.html', context)
    try:
        csv_file = request.FILES['file']
    except MultiValueDictKeyError:
        return render(request, 'accounts/changeOrder.html')
    
    if request.method == "POST":
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        
        for column in csv.reader(io_string, delimiter=','):
            try:
                if 'OFFERNUM' not in column[0] and 'Textbox' not in column[0] and 'Report Run' not in column[0]:
                    if not Provisioning.objects.filter(OFFERNUM = column[0]).exists():
                        if 'COMPLETED' not in column[10]:
                            _, created = Provisioning.objects.update_or_create( 
                            MDU_ID=strip_non_ascii(column[2]),
                            PROPERTYNAME=strip_non_ascii(column[3]),
                            CUST_ACCT=strip_non_ascii(column[4]),
                            SITE_ID=strip_non_ascii(column[5]),
                            CUSTOMERNAME=strip_non_ascii(column[6]),
                            FULLADDRESS=strip_non_ascii(column[7]),
                            ONTSERIAL=strip_non_ascii(column[8]),
                            OFFERNUM=strip_non_ascii(column[0]),
                            ORDERDATE=strip_non_ascii(column[9]),
                            BILLINGEFFECTIVEDATE=strip_non_ascii(column[1]),
                            ORDERTYPE=strip_non_ascii(column[10]),
                            OLDSERVICE=strip_non_ascii(column[11]),
                            NEWSERVICE=strip_non_ascii(column[12]),
                            completion_Status='Submitted'
                        )
                        else:
                            _, created = Provisioning.objects.update_or_create( 
                            MDU_ID=strip_non_ascii(column[2]),
                            PROPERTYNAME=strip_non_ascii(column[3]),
                            CUST_ACCT=strip_non_ascii(column[4]),
                            SITE_ID=strip_non_ascii(column[5]),
                            CUSTOMERNAME=strip_non_ascii(column[6]),
                            FULLADDRESS=strip_non_ascii(column[7]),
                            ONTSERIAL=strip_non_ascii(column[8]),
                            OFFERNUM=strip_non_ascii(column[0]),
                            ORDERDATE=strip_non_ascii(column[9]),
                            BILLINGEFFECTIVEDATE=strip_non_ascii(column[1]),
                            ORDERTYPE=strip_non_ascii(column[10]),
                            OLDSERVICE=strip_non_ascii(column[11]),
                            NEWSERVICE=strip_non_ascii(column[12]),
                            completion_Status='Complete'
                        )
                    else:
                        if (Log.objects.filter(ticket_Number = strip_non_ascii(column[0]))).exists():
                            log = Log.objects.filter(ticket_Number = strip_non_ascii(column[0])) & Log.objects.filter(source = 'change orders/disconnects/reconnects')
                            if log[0].cognito_Number is None:
                                name = log[0].employee
                                firstName = name.partition(' ')[0]
                                lastName = name.partition(' ')[2]
                                userTier = User.objects.filter(first_name=firstName) & User.objects.filter(last_name=lastName)
                                
                                email = EmailMessage(
                                    'Open change order/disconnect/reconnect ticket #' + strip_non_ascii(column[0]) + '',
                                    'Hello ' + name + ', it seems that you have left a change order/disconnect/reconnect ticket open on Amdocs with an offer number of #' + strip_non_ascii(column[0]) + '. If this is correct, please close it whenever possible. If you feel that this is an error, please contact Cesare Johnson. Thank you and have a great day!',
                                    settings.EMAIL_HOST_USER,
                                    [userTier[0].email, 'cjohnson@hotwirecommunication.com', 'patrick.perez@hotwirecommunication.com'],
                                    ['shivase.singh@hotwirecommunication.com', 'jason.besley@hotwirecommunication.com'],
                                )
                                email.fail_silently=False
                                email.send()
                                log[0].cognito_Number = '1'
                                log[0].save()
                        else:
                            _, created = Duplicate.objects.update_or_create( 
                            MDU_ID=strip_non_ascii(column[2]),
                            PROPERTYNAME=strip_non_ascii(column[3]),
                            CUST_ACCT=strip_non_ascii(column[4]),
                            SITE_ID=strip_non_ascii(column[5]),
                            CUSTOMERNAME=strip_non_ascii(column[6]),
                            FULLADDRESS=strip_non_ascii(column[7]),
                            ONTSERIAL=strip_non_ascii(column[8]),
                            OFFERNUM=strip_non_ascii(column[0]),
                            ORDERDATE=strip_non_ascii(column[9]),
                            BILLINGEFFECTIVEDATE=strip_non_ascii(column[1]),
                            ORDERTYPE=strip_non_ascii(column[10]),
                            OLDSERVICE=strip_non_ascii(column[11]),
                            NEWSERVICE=strip_non_ascii(column[12]),
                            completion_Status='Change Order'
                            )
            except IndexError:
                pass
        return redirect('/t2ProvGrabber')
    context = {}
    return render(request, 'accounts/changeOrder.html', context)

@login_required(login_url='login')
def ddt(request):
    context = {}
    if request.method == "GET":
        return render(request, 'accounts/ddt.html', context)
    try:
        csv_file = request.FILES['file']
    except MultiValueDictKeyError:
        return render(request, 'accounts/ddt.html')
    
    if request.method == "POST":
        data_set = csv_file.read().decode('UTF-8')
        io_string = io.StringIO(data_set)
        
        for column in csv.reader(io_string, delimiter=','):
            try:
                if 'ACCOUNT' not in column[0] and 'Complete' not in column[15]:
                    if not Ddt.objects.filter(CID = column[3]).exists():
                        _, created = Ddt.objects.update_or_create( 
                        action=column[0],
                        CID=column[3],
                        SUB_Start=column[2],
                        SUB_Stop=column[7],
                        amdocs_Plus=column[23],
                        serial=column[5],
                        completion_Status='Submitted'
                    )
            except IndexError:
                pass
        return redirect('/t2ProvGrabber')
    context = {}
    return render(request, 'accounts/ddt.html', context)

@login_required(login_url='login')
def collectionDisconnect(request):
    context = {}
    if request.method == "GET":
        return render(request, 'accounts/collectionDisconnect.html', context)
    try:
        csv_file = request.FILES['file']
    except MultiValueDictKeyError:
        return render(request, 'accounts/collectionDisconnect.html')
    
    if request.method == "POST":
        data_set = csv_file.read().decode('cp1253')
        io_string = io.StringIO(data_set)
        
        for column in csv.reader(io_string, delimiter=','):
            try:
                if 'Account Number' not in strip_non_ascii(column[0]):
                    if not CollectionDisconnect.objects.filter(OfferNumber = strip_non_ascii(column[1])).exists():
                        _, created = CollectionDisconnect.objects.update_or_create( 
                        AccountNumber=strip_non_ascii(column[0]),
                        OfferNumber=strip_non_ascii(column[1]),
                        ActionSuspendDowngrade=strip_non_ascii(column[2]),
                        PropertyName=strip_non_ascii(column[3]),
                        completion_Status='Submitted'
                    )
            except IndexError:
                pass
        return redirect('/t2ProvGrabber')
    context = {}
    return render(request, 'accounts/collectionDisconnect.html', context)

@login_required(login_url='login')
def t2ProvGrabber(request):
    ddts = NoSchedule.objects.filter(completion_Status='Submitted')
    context = {'ddts' : ddts}
    return render(request, 'accounts/t2ProvGrabber.html', context)

@login_required(login_url='login')
def troubleTicketGrabber(request):
    #ddts = NoSchedule.objects.filter(completion_Status='Submitted')
    ddts = NoSchedule.objects.raw("SELECT * FROM accounts_noschedule WHERE completion_Status = 'Submitted' ORDER BY CASE when CallReason = 'Voicemail Issue' THEN 1 WHEN CallReason = 'Voice Static/Humming' THEN 2 WHEN CallReason = 'No Recvg Inc''g Calls' THEN 3 WHEN CallReason = 'No Outgoing Calls' THEN 4 ELSE 5 END;")
    context = {'ddts' : ddts}
    return render(request, 'accounts/troubleTicketGrabber.html', context)

@login_required(login_url='login')
def changeOrderGrabber(request):
    #ddts = Provisioning.objects.filter(completion_Status='Submitted')
    ddts = Provisioning.objects.raw('SELECT * FROM accounts_provisioning WHERE completion_Status = "Submitted" ORDER BY CASE `ORDERTYPE` WHEN "PENDING RESTART" THEN 1 WHEN "PENDING DISCONNECTION" THEN 2 ELSE 3 END;')
    #discs = Provisioning.objects.raw("select * from accounts_provisioning where ORDERTYPE LIKE '%COMPLETED DISCONNECT%' AND (ORDERDATE LIKE '%/2021' OR ORDERDATE LIKE '8/%/2020' OR ORDERDATE LIKE '9/%/2020' OR ORDERDATE LIKE '10/%/2020' OR ORDERDATE LIKE '11/%/2020' OR ORDERDATE LIKE '12/%/2020');")
    context = {'ddts' : ddts}
    return render(request, 'accounts/changeOrderGrabber.html', context)

@login_required(login_url='login')
def ddtGrabber(request):
    ddts = Ddt.objects.filter(completion_Status='Submitted')
    context = {'ddts' : ddts}
    return render(request, 'accounts/ddtGrabber.html', context)

@login_required(login_url='login')
def collectionDisconnectGrabber(request):
    collectionDisconnects = CollectionDisconnect.objects.filter(completion_Status='Submitted')
    context = {'collectionDisconnects' : collectionDisconnects}
    return render(request, 'accounts/collectionDisconnectGrabber.html', context)

@login_required(login_url='login')
def t2ProvCheck(request, pk):
    ddt = NoSchedule.objects.get(id=pk)
    if request.method == "POST":
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO accounts_log (ticket_Number, employee, site, services, source, completion_Status, dateCreated) SELECT TicketNumber, "' + str(request.user.employee) + '", MNAME, CallReason, "change orders/disconnects/reconnects", "Reviewed", now() FROM accounts_noschedule WHERE id =' + pk + '')
            cursor.execute('UPDATE accounts_noschedule SET completion_status="Reviewed" WHERE id =' + pk + '')
        return redirect('/autoLog')
    context = {'ddt':ddt}
    return render(request, 'accounts/t2ProvCheck.html', context)

@login_required(login_url='login')
def troubleTicketCheck(request, pk):
    ddt = NoSchedule.objects.get(id=pk)
    if request.method == "POST":
        #if NoSchedule.objects.filter()
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO accounts_log (ticket_Number, employee, site, services, source, completion_Status, notes, dateCreated) SELECT TicketNumber, "' + str(request.user.employee) + '", MNAME, CallReason, "Trouble Ticket", "Reviewed", CustomerNumber, now() FROM accounts_noschedule WHERE id =' + pk + '')
            cursor.execute('UPDATE accounts_noschedule SET completion_status="Reviewed" WHERE id =' + pk + '')
        return redirect('/autoLog')
    context = {'ddt':ddt}
    return render(request, 'accounts/troubleTicketCheck.html', context)

@login_required(login_url='login')
def changeOrderCheck(request, pk):
    ddt = Provisioning.objects.get(id=pk)
    if request.method == "POST":
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO accounts_log (ticket_Number, employee, site, services, source, completion_Status, notes, dateCreated) SELECT OFFERNUM, "' + str(request.user.employee) + '", PROPERTYNAME, ORDERTYPE, "change orders/disconnects/reconnects", "Reviewed", CUST_ACCT, now() FROM accounts_provisioning WHERE id =' + pk + '')
            cursor.execute('UPDATE accounts_provisioning SET completion_status="Reviewed" WHERE id =' + pk + '')
        return redirect('/autoLog')
    context = {'ddt':ddt}
    return render(request, 'accounts/changeOrderCheck.html', context)

@login_required(login_url='login')
def ddtCheck(request, pk):
    ddt = Ddt.objects.get(id=pk)
    if request.method == "POST":
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO accounts_log (ticket_Number, employee, services, source, completion_Status, dateCreated) SELECT CID, "' + str(request.user.employee) + '", action, "Secure Plus", "Reviewed", now() FROM accounts_ddt WHERE id =' + pk + '')
            cursor.execute('UPDATE accounts_ddt SET completion_status="Reviewed" WHERE id =' + pk + '')
        return redirect('/autoLog')
    context = {'ddt':ddt}
    return render(request, 'accounts/ddtCheck.html', context)

@login_required(login_url='login')
def collectionDisconnectCheck(request, pk):
    collectionDisconnect = CollectionDisconnect.objects.get(id=pk)
    if request.method == "POST":
        with connection.cursor() as cursor:
            cursor.execute('INSERT INTO accounts_log (ticket_Number, employee, site, services, source, completion_Status, notes, dateCreated) SELECT OfferNumber, "' + str(request.user.employee) + '", PropertyName, ActionSuspendDowngrade, "Collection Disconnect", "Reviewed", AccountNumber, now() FROM accounts_collectiondisconnect WHERE id =' + pk + '')
            cursor.execute('UPDATE accounts_collectiondisconnect SET completion_status="Reviewed" WHERE id =' + pk + '')
        return redirect('/autoLog')
    context = {'collectionDisconnect':collectionDisconnect}
    return render(request, 'accounts/collectionDisconnectCheck.html', context)

def t2ProvView(request, pk):
    ddt = NoSchedule.objects.get(id=pk)
    context = {'ddt':ddt}
    return render(request, 'accounts/t2ProvView.html', context)

def troubleTicketView(request, pk):
    ddts = NoSchedule.objects.filter(TicketNumber=pk)
    context = {'ddts':ddts}
    return render(request, 'accounts/troubleTicketView.html', context)

def changeOrderView(request, pk):
    ddts = Provisioning.objects.filter(OFFERNUM=pk)
    context = {'ddts':ddts}
    return render(request, 'accounts/changeOrderView.html', context)

def ddtView(request, pk):
    ddts = Ddt.objects.filter(CID=pk)
    context = {'ddts':ddts}
    return render(request, 'accounts/ddtView.html', context)

def collectionDisconnectView(request, pk):
    collectionDisconnects = CollectionDisconnect.objects.filter(OfferNumber=pk)
    context = {'collectionDisconnects':collectionDisconnects}
    return render(request, 'accounts/collectionDisconnectView.html', context)

def dropdown(request):
    form = ListForm()
    options = User.objects.all()
    ddts = NoSchedule.objects.raw("SELECT * FROM accounts_noschedule WHERE completion_Status = 'Submitted' ORDER BY CASE when CallReason = 'Voicemail Issue' THEN 1 WHEN CallReason = 'Voice Static/Humming' THEN 2 WHEN CallReason = 'No Recvg Inc''g Calls' THEN 3 WHEN CallReason = 'No Outgoing Calls' THEN 4 ELSE 5 END;")
    if request.method == 'POST':
        datas = []
        for data in request.POST.getlist('id'):
            datas.append(data)
        
        x = 0
        for item in request.POST.getlist('employee'):
            print(request.POST)
            print('Ticket Number: ' + datas[x])
            print('Employee ID: ' + item)
            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO accounts_log (ticket_Number, employee, site, services, source, completion_Status, dateCreated) SELECT TicketNumber, "' + str(User.objects.get(id=item).get_full_name()) + '", MNAME, CallReason, "Trouble Ticket", "Reviewed", now() FROM accounts_noschedule WHERE ticketNumber =' + str(datas[x]) + '')
                cursor.execute('UPDATE accounts_noschedule SET completion_status="Reviewed" WHERE TicketNumber =' + str(datas[x]) + '')
            x = x + 1

    context = {'options':options, 'ddts' : ddts, 'form':form}
    return render(request, 'accounts/dropdown.html', context)

def troubleTicketDropdown(request):
    form = ListForm()
    options = User.objects.all()
    ddts = NoSchedule.objects.raw("SELECT * FROM accounts_noschedule WHERE completion_Status = 'Submitted' ORDER BY CASE when CallReason = 'Voicemail Issue' THEN 1 WHEN CallReason = 'Voice Static/Humming' THEN 2 WHEN CallReason = 'No Recvg Inc''g Calls' THEN 3 WHEN CallReason = 'No Outgoing Calls' THEN 4 ELSE 5 END;")
    if request.method == 'POST':
        datas = []
        for data in request.POST.getlist('id'):
            datas.append(data)
        
        x = 0
        for item in request.POST.getlist('employee'):
            print(request.POST)
            print('Ticket Number: ' + datas[x])
            print('Employee ID: ' + item)
            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO accounts_log (ticket_Number, employee, site, services, source, completion_Status, dateCreated) SELECT TicketNumber, "' + str(User.objects.get(id=item).get_full_name()) + '", MNAME, CallReason, "Trouble Ticket", "Reviewed", now() FROM accounts_noschedule WHERE ticketNumber =' + str(datas[x]) + '')
                cursor.execute('UPDATE accounts_noschedule SET completion_status="Reviewed" WHERE TicketNumber =' + str(datas[x]) + '')
            x = x + 1

    context = {'options':options, 'ddts' : ddts, 'form':form}
    return render(request, 'accounts/troubleTicketDropdown.html', context)

def changeOrderDropdown(request):
    form = ListForm()
    options = User.objects.all()
    ddts = NoSchedule.objects.raw("SELECT * FROM accounts_provisioning WHERE completion_Status = 'Submitted' ORDER BY CASE 'ORDERTYPE' WHEN 'PENDING RESTART' THEN 1 WHEN 'PENDING DISCONNECTION' THEN 2 ELSE 3 END;")
    if request.method == 'POST':
        datas = []
        for data in request.POST.getlist('id'):
            datas.append(data)
        
        x = 0
        for item in request.POST.getlist('employee'):
            print(request.POST)
            print('Ticket Number: ' + datas[x])
            print('Employee ID: ' + item)
            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO accounts_log (ticket_Number, employee, site, services, source, completion_Status, notes, dateCreated) SELECT OFFERNUM, "' + str(User.objects.get(id=item).get_full_name()) + '", PROPERTYNAME, ORDERTYPE, "change orders/disconnects/reconnects", "Reviewed", CUST_ACCT, now() FROM accounts_provisioning WHERE OFFERNUM =' + str(datas[x]) + '')
                cursor.execute('UPDATE accounts_provisioning SET completion_status="Reviewed" WHERE OFFERNUM =' + str(datas[x]) + '')
            x = x + 1

    context = {'options':options, 'ddts' : ddts, 'form':form}
    return render(request, 'accounts/changeOrderDropdown.html', context)

def ddtDropdown(request):
    form = ListForm()
    options = User.objects.all()
    ddts = Ddt.objects.filter(completion_Status='Submitted')
    if request.method == 'POST':
        datas = []
        for data in request.POST.getlist('id'):
            datas.append(data)
        
        x = 0
        for item in request.POST.getlist('employee'):
            print(request.POST)
            print('Ticket Number: ' + datas[x])
            print('Employee ID: ' + item)
            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO accounts_log (ticket_Number, employee, services, source, completion_Status, dateCreated) SELECT CID, "' + str(User.objects.get(id=item).get_full_name()) + '", action, "Secure Plus", "Reviewed", now() FROM accounts_ddt WHERE CID =' + str(datas[x]) + '')
                cursor.execute('UPDATE accounts_ddt SET completion_status="Reviewed" WHERE CID =' + str(datas[x]) + '')
            x = x + 1

    context = {'options':options, 'ddts' : ddts, 'form':form}
    return render(request, 'accounts/ddtDropdown.html', context)

def collectionDisconnectDropdown(request):
    form = ListForm()
    options = User.objects.all()
    ddts = CollectionDisconnect.objects.filter(completion_Status='Submitted')
    if request.method == 'POST':
        datas = []
        for data in request.POST.getlist('id'):
            datas.append(data)
        
        x = 0
        for item in request.POST.getlist('employee'):
            print(request.POST)
            print('Ticket Number: ' + datas[x])
            print('Employee ID: ' + item)
            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO accounts_log (ticket_Number, employee, site, services, source, completion_Status, notes, dateCreated) SELECT OfferNumber, "' + str(User.objects.get(id=item).get_full_name()) + '", PropertyName, ActionSuspendDowngrade, "Collection Disconnect", "Reviewed", AccountNumber, now() FROM accounts_collectiondisconnect WHERE OfferNumber =' + str(datas[x]) + '')
                cursor.execute('UPDATE accounts_collectiondisconnect SET completion_status="Reviewed" WHERE OfferNumber =' + str(datas[x]) + '')
            x = x + 1

    context = {'options':options, 'ddts' : ddts, 'form':form}
    return render(request, 'accounts/collectionDisconnectDropdown.html', context)