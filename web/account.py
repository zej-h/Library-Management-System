from django.shortcuts import render, HttpResponse, redirect
from django import forms
from io import BytesIO

from web import models

class LoginForm(forms.Form):
    id = forms.CharField(
        label="用户名",
        widget=forms.TextInput(attrs={"class":"form-control"})
    )
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(attrs={"class":"form-control"})
    )

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
    

def login(request):
    """ 登录 """
    if request.method == "GET":
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    form = LoginForm(data=request.POST)
    if form.is_valid():
        data=request.POST
        if "admin_login" in request.POST:
            # 管理员身份登录代码
            admin_object = models.manager.objects.filter(id=data['id'],password=data['password']).first()
            if not admin_object:
                form.add_error("password", "用户名或密码错误")
                return render(request, 'login.html', {'form': form})
            request.session["info"] = {'id': admin_object.id, 'name': admin_object.name,'nid':""}
            request.session.set_expiry(60 * 60 * 24 * 7)
            return redirect("/book/list/")
            
        elif "reader_login" in request.POST:
            # 读者身份登录代码
            admin_object = models.card.objects.filter(cno=data['id'],password=data['password']).first()
            if not admin_object:
                form.add_error("password", "用户名或密码错误")
                return render(request, 'login.html', {'form': form})
            request.session["info"] = {'id': admin_object.cno, 'name': admin_object.name,'nid':""}
            request.session.set_expiry(60 * 60 * 24 * 7)
            return redirect("/book/list2/")
            
    return render(request, 'login.html', {'form': form})

class CardModelform(forms.ModelForm):
    class Meta:
        model = models.card
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control"}

def register(request):
    if request.method == "GET":
        form = CardModelform()
        return render(request, 'register.html', {'form': form})
    form = CardModelform(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/login/')

    return render(request, 'register.html', {"form": form})


def logout(request):
    """ 注销 """
    request.session.clear()
    return redirect('/login/')