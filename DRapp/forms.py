from django.forms import *

from DRapp.models import *


class PersonalDetails(forms.Form):
    pname = CharField(label='Enter patient\'s name', max_length=30, required=True, widget=TextInput(attrs={'id': 'name'}))
    page = IntegerField(label='Enter patient\'s age', max_value=100,min_value=10, required=True, widget=NumberInput(attrs={'id': 'patient_age'}))
    address = CharField(label='Enter patient\'s address', max_length=100, required=True)
    pno = IntegerField(label='Enter patient\'s phone Number', max_value=9999999999, min_value=1000000000, required=True,widget=TextInput(attrs={'id':'phone'}))
    gender = ChoiceField(label='Gender', choices=(('M', 'Male'), ('F', 'Female')))
    blood = ChoiceField(label="Blood Group", choices=(('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')))
    patient_photo = ImageField(label='Upload Patient Photo', required=True, widget=FileInput(attrs={'id':'patient_photo','title': 'formats supported jpg,png and jpeg'}))
    diabetic_type = ChoiceField(label='Diabetic Type', choices=(('type1', 'TYPE1'), ('type2', 'TYPE2')), required=True)
    sugar_Fasting_value = IntegerField(label='Sugar Fasting Value', required=True)
    sugar_Non_fasting_value = IntegerField(label='Sugar Non Fasting Value', required=True)
    time_duration = IntegerField(label="Duration of Diabeties", max_value=70, min_value=2, required=True, widget=NumberInput(attrs={'id': 'diab_duration'}))
    diab_report = FileField(label='Upload Diabetic Report', required=True, widget=FileInput(attrs={'id': 'diab_report','title': 'formats supported txt,doc and docx'}))


class DiabeticRetinopathyDetails(forms.Form):
    left_retina_photo = ImageField(label='Left Retina photo', required=True, widget=FileInput(attrs={'id': 'left_retina_photo','title': 'formats supported jpg,png and jpeg'}))
    right_retina_photo = ImageField(label='Right Retina photo', required=True, widget=FileInput(attrs={'id': 'right_retina_photo','title': 'formats supported jpg,png and jpeg'}))


class PpdForm(ModelForm):
    class Meta:
        model = Patient
        fields = '__all__'
        widgets = {
            'patient_id': TextInput(attrs={'disabled': True}),
            'patient_name': TextInput(attrs={'disabled': True}),
        }


class PdhForm(ModelForm):
    class Meta:
        model = DiabeticHistory
        fields = '__all__'
        exclude = ['patient_id']


class DRForm(ModelForm):
    class Meta:
        model = DiabeticRetinopathy
        fields = ['left_retina_photo', 'right_retina_photo']

