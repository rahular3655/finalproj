from django import forms 

class CoupnApplyForm(forms.Form):
    code = forms.CharField()