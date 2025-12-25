from django import forms 
from .models import User, UserRole, Department

class StudentBulkUploadForm(forms.Form):
    csv_file = forms.FileField()
    
    
class ManualStudentAddForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["full_name", "register_number", "email", "department"]
        
        def save(self, commit=True):
            user = super().save(commit=False)
            user.role = UserRole.STUDENT
            if commit:
                user.save()
            return user
        
        
class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)