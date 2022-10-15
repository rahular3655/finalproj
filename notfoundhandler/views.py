from django.shortcuts import redirect
from django.shortcuts import render
from adminprev.views import adminsignin


# Create your views here.
def error_404(request,exception):
    user=request.user
    try:
        if user.is_admin == True:
            return redirect(adminsignin)
    except AttributeError:
        pass
    return render(request,'4044.html')