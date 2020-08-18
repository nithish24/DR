from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import *
from django.shortcuts import *
from DRapp.forms import *
from .models import *
import random,shutil
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
import time
from django.views.decorators.cache import never_cache

from .ImagePreProcess import *
from .PredictStage import *
import os

def prelogin(request):
    return render(request, 'login.html')


@login_required(login_url='')
def home(request):
    return render(request, "home.html")


@login_required(login_url='')
def add(request):
    form1 = PersonalDetails()
    return render(request, "add_patient.html", {'form1': form1})


@login_required(login_url='')
def pending(request):
    drlist = DiabeticRetinopathy.objects.values_list('patient_id_id', flat=True)
    main_list = list(Patient.objects.exclude(patient_id__in=drlist))
    return render(request, "pending.html", {'pending_list': main_list})


@login_required(login_url='')
def dr(request, id):
    checking_in_patient = Patient.objects.filter(patient_id=id).count()
    if checking_in_patient == 1:
        if request.method == 'POST':
            files = request.FILES
            files['left_retina_photo'].name = str(id) + '_left_retina.' + files['left_retina_photo'].name.split('.')[-1]
            files['right_retina_photo'].name = str(id) + '_right_retina.' + files['right_retina_photo'].name.split('.')[-1]
            diabeticret = DiabeticRetinopathy(patient_id_id=id, left_retina_photo=files['left_retina_photo'], right_retina_photo=files['right_retina_photo'])
            diabeticret.save()
            messages.success(request, "SUCCESSFULLY UPLOADED THE IMAGES TO THE SERVER!!")
            return redirect("/predict/"+str(id))
        else:
            checking = DiabeticRetinopathy.objects.filter(patient_id_id=id).count()
            if checking == 0:
                drform = DiabeticRetinopathyDetails()
                return render(request, "diabetic_retinopathy.html", {'id': id, 'form': drform, 'predicted': False})
            messages.success(request, "Retinal images was already present no need to add!!")
            return redirect("/predict/" + str(id))
    else:
        return HttpResponse("<script>alert('patient not found'); window.history.back();</script>")



@login_required(login_url='')
def insert(request):
    data = request.POST
    files = request.FILES
    if request.method == 'POST':
        check = Patient.objects.filter(phone_no=data['pno'], patient_name=data['pname'], patient_age=data['page'], blood_group=data['blood']).count()
        if check == 0:
            new_pid = Patient.objects.order_by('-patient_id').first()
            if new_pid == None:
                new_pid = 1
            else:
                new_pid = new_pid.patient_id + 1
            files['patient_photo'].name = str(new_pid) + '.' + files['patient_photo'].name.split('.')[-1]
            files['diab_report'].name = str(new_pid) + '.' + files['diab_report'].name.split('.')[-1]
            patient = Patient(
                patient_id=new_pid,
                patient_name=data['pname'],
                patient_age=data['page'],
                address=data['address'],
                phone_no=data['pno'],
                gender=data['gender'],
                blood_group=data['blood'],
                patient_photo=files['patient_photo'],
            )
            patient.save()
            diabetic_history = DiabeticHistory(
                patient_id_id=new_pid,
                diabetic_type=data['diabetic_type'],
                sugar_Fasting_value=data['sugar_Fasting_value'],
                sugar_Non_fasting_value=data['sugar_Non_fasting_value'],
                time_duration=data['time_duration'],
                diab_report=files['diab_report'],
            )
            diabetic_history.save()
            messages.success(request, "PATIENT ADDED SUCCESSFULLY! \n PLEASE ADD RETINA PHOTOS")
            return redirect("addDR/" + str(new_pid))
        else:
            return HttpResponse("<script>alert('Entries already Present'); window.history.back();</script>")
    else:
        return HttpResponse("Something went wrong")


@login_required(login_url='')
def get_all(request, list_type):
    if list_type in ['c', 'p']:
        drlist = DiabeticRetinopathy.objects.values_list('patient_id_id', flat=True)
        if list_type == 'c':
            all = list(Patient.objects.filter(patient_id__in=drlist))
        else:
            all = list(Patient.objects.exclude(patient_id__in=drlist))
        return render(request, "listall.html", {'all': all, 'type': list_type})
    else:
        return HttpResponse("<script>alert('Something Went Wrong'); window.history.back();</script>")


@login_required(login_url='')
def search(request):
    if request.method == 'POST':
        data = request.POST
        search_key = data['parameter']
        res1 = ''

        if str(search_key).isalpha():
            res1 = Patient.objects.filter(patient_name__icontains=search_key)
        elif str(search_key).isnumeric():
            res1 = Patient.objects.filter(phone_no=int(search_key))
        return render(request, "search_result.html", {'search_result': res1, 'search_key': search_key})
    else:
        return HttpResponse("Something went wrong")


@never_cache
def loggingin(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('home/')
    else:
        messages.error(request, "INVALID CREDENTIALS")
        return redirect('/')


@login_required(login_url='')
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'LOGOUT SUCCESSFUL')
        return redirect("/")
    else:
        return HttpResponse('User not logged in')


@login_required(login_url='')
def preprocess(request, id):
    class_id_dict = {
        0:"No DR",
        1:"Mild DR",
        2:"Moderate DR",
        3:"Severe DR",
        4:"Proliferative DR"
    }
    checking_in_patient = Patient.objects.filter(patient_id=id).count()
    checking_in_dr = DiabeticRetinopathy.objects.filter(patient_id_id=id).count()
    if checking_in_patient == 1 and checking_in_dr == 1:
        data = DiabeticRetinopathy.objects.get(patient_id_id=id)
        if request.method == 'GET':
            if data.left_predicted_stage:
                return render(request, "predict.html",
                              {'data': data, 'result': 1, 'left_eye': data.left_predicted_stage, 'right_eye': data.right_predicted_stage,
                               'time_duration': ""})
            return render(request, "predict.html", {'data': data, 'no_result': 1, 'id': id})
        elif request.method == 'POST':
            start = time.time()

            Base_dir = str(settings.BASE_DIR.replace('\\', '/'))

            right_path = Base_dir+str(data.right_retina_photo.url)
            left_path = Base_dir+str(data.left_retina_photo.url)
            #print(left_path)

            left_path_normalized = left_path.split('/')
            left_file_name = left_path_normalized.pop()
            left_path_normalized = "/".join(left_path_normalized) + "/normalized_" + left_file_name

            right_path_normalized = right_path.split('/')
            right_file_name = right_path_normalized.pop()
            right_path_normalized = "/".join(right_path_normalized) + "/normalized_" + right_file_name

            imgObj = imgpp()
            preObj = integration()

            if imgObj.preprocess_automate(left_path,right_path):

                left_class_0, left_class_1 = preObj.integrate_automate(left_path_normalized)
                right_class_0, right_class_1 = preObj.integrate_automate(right_path_normalized)

                if left_class_0 == 0:
                    left_eye = 0
                elif left_class_0 == 1:
                    left_eye = left_class_1+1

                if right_class_0 == 0 :
                    right_eye = 0
                elif left_class_0 == 1:
                    right_eye = right_class_1+1

                del imgObj, preObj, Base_dir, right_path, left_path, left_path_normalized, left_file_name, right_path_normalized, right_file_name

                end = time.time()
                time_consumed = end - start

                left_eye_name = class_id_dict[left_eye]
                right_eye_name = class_id_dict[right_eye]

                data.left_predicted_stage = left_eye_name
                data.right_predicted_stage = right_eye_name
                data.save()
                return render(request, "predict.html", {'data': data, 'result': 1, 'left_eye': left_eye_name, 'right_eye': right_eye_name, 'time_duration': time_consumed})
            else:
                return HttpResponse("Something went wrong")
    else:
        return HttpResponse("<script>alert('patient not found under predict stage please check in pending list'); window.history.back();</script>")


@login_required(login_url='')
def delete(request, id):
    checking_in_patient = Patient.objects.filter(patient_id=id).count()
    if checking_in_patient == 1:
        try:
            p_del = Patient.objects.get(patient_id=id)
            p_dir = str(settings.BASE_DIR.replace('\\', '/'))+str("/media/")+str(id)
            if os.path.exists(p_dir):
                shutil.rmtree(p_dir)
                p_del.delete()
            messages.success(request, "Patient Records Deleted")
        except:
            messages.error(request, "Something went wrong")
        finally:
            return redirect('/list/c')
    else:
        return HttpResponse("<script>alert('patient not found'); window.history.back();</script>")


@login_required(login_url='')
def view_patient(request, id):
    if id > 0:
        res1 = Patient.objects.filter(patient_id=id)
    if res1.count() == 1:
        res2 = DiabeticHistory.objects.filter(patient_id=list(res1)[0].patient_id)
        status = False
        res3 = DiabeticRetinopathy.objects.filter(patient_id=list(res1)[0].patient_id)
        if res3.count() == 1:
            status = True
        return render(request, "patient_personal_details.html", {'ppd': res1, 'pdh': res2, 'dr': res3, 'status': status,'id':id})
    else:
        return HttpResponse("Patient Not Found")

@login_required(login_url = '')
def print(request,id):
    if id > 0:
        res1 = Patient.objects.filter(patient_id=id)
    if res1.count() == 1:
        res2 = DiabeticHistory.objects.filter(patient_id=list(res1)[0].patient_id)
        status = False
        res3 = DiabeticRetinopathy.objects.filter(patient_id=list(res1)[0].patient_id)
        if res3.count() == 1:
            status = True
        return render(request, "print_pdf.html", {'ppd': res1, 'pdh': res2, 'dr': res3, 'status': status,'id':id})
    else:
        return HttpResponse("Patient Not Found")


@login_required(login_url='')
def edit_patient(request, id):
    checking = Patient.objects.filter(patient_id=id)
    if checking.count() == 1:
        data1 = checking.first()
        data2 = DiabeticHistory.objects.get(patient_id_id=id)
        checking2 = DiabeticRetinopathy.objects.filter(patient_id_id=id)
        dr = DRForm()
        flag = False
        if checking2.count() == 1:
            data3 = checking2.first()
            dr = DRForm(instance=data3)
            flag = True
        ppd = PpdForm(instance=data1)
        pdh = PdhForm(instance=data2)
        return render(request, 'edit_patient.html', {'ppd': ppd, 'pdh': pdh, 'dr': dr, 'flag': flag})
    else:
        return HttpResponse("<script>alert('patient not found'); window.history.back();</script>")


@login_required(login_url='')
def update(request):
    if request.method == 'POST':
        data = request.POST
        files = request.FILES
        data1 = Patient.objects.filter(patient_id=data['patient_id'])
        data1.update(patient_age=data['patient_age'], address=data['address'], phone_no=data['phone_no'], )
        for objects in data1:
            objects.save()
        data2 = DiabeticHistory.objects.get(patient_id_id=data['patient_id'])
        data2.diabetic_type = data['diabetic_type']
        data2.sugar_Fasting_value = data['sugar_Fasting_value']
        data2.sugar_Non_fasting_value = data['sugar_Non_fasting_value']
        data2.time_duration = data['time_duration']
        data3 = DiabeticRetinopathy.objects.filter(patient_id_id=data['patient_id'])
        try:
            files['diab_report'].name = str(data['patient_id']) + '.' + files['diab_report'].name.split('.')[-1]
            fullname = str(settings.BASE_DIR.replace('\\', '/')) + str("/media/") + str(data['patient_id']) + '/' + files['diab_report'].name
            if os.path.exists(fullname):
                os.remove(fullname)
            data2.diab_report = files['diab_report']
        except:
            pass
        data2.save()
        try:
            files['left_retina_photo'].name = str(data['patient_id']) + '_left_retina.' + files['left_retina_photo'].name.split('.')[-1]
            files['right_retina_photo'].name = str(data['patient_id']) + '_right_retina.' + files['right_retina_photo'].name.split('.')[-1]
            fullname = str(settings.BASE_DIR.replace('\\', '/')) + str("/media/") + str(data['patient_id']) + '/' + \
                       files['left_retina_photo'].name
            if os.path.exists(fullname):
                os.remove(fullname)
            fullname = str(settings.BASE_DIR.replace('\\', '/')) + str("/media/") + str(data['patient_id']) + '/' + files['right_retina_photo'].name
            if os.path.exists(fullname):
                os.remove(fullname)
            fullname1 = str(settings.BASE_DIR.replace('\\', '/')) + str("/media/") + str(data['patient_id']) + '/normalized_' + files['left_retina_photo'].name
            if os.path.exists(fullname1):
                os.remove(fullname1)
            fullname2 = str(settings.BASE_DIR.replace('\\', '/')) + str("/media/") + str(data['patient_id']) + '/normalized_' + files['right_retina_photo'].name
            if os.path.exists(fullname2):
                os.remove(fullname2)
            data3 = DiabeticRetinopathy.objects.get(patient_id_id=data['patient_id'])
            data3.left_retina_photo = files['left_retina_photo']
            data3.right_retina_photo = files['right_retina_photo']
            data3.left_predicted_stage = ""
            data3.right_predicted_stage = ""
            data3.save()
            messages.success(request, "PATIENT DETAILS UPDATED SUCCESSFULLY!")
            return redirect('/predict/' + str(data['patient_id']))
        except:
            if data3.count() == 0:
                messages.success(request, "PATIENT DETAILS UPDATED SUCCESSFULLY! \n PLEASE ADD RETINA PHOTOS")
                return redirect('/addDR/' + str(data['patient_id']))
        messages.success(request, 'PATIENT DETAILS UPDATED SUCCESSFULLY!')
        return redirect("/view/" + str(data['patient_id']))
    else:
        return HttpResponse("<script>alert('Something Went Wrong'); window.history.back();</script>")

