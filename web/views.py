from dataclasses import field
from django import forms
from logging import PlaceHolder
from django.http import HttpResponse
from django.shortcuts import redirect, render
from web import models
import re


def manager(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    return render(request, 'manager.html', {"name": name})

def reader(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["cno"]
    return render(request, 'reader.html', {"name": name})

def manager_card(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    nid = request.POST.get("nid")
    if (not nid):
        nid = ""
        queryset = models.card.objects.all()
        return render(request, 'manager_card.html', {"queryset": queryset, "name": name, "nid": nid})

    queryset = models.card.objects.filter(cno=nid)
    if queryset:

        request.session["info"]["nid"] = nid
        request.session.set_expiry(60 * 60 * 24 * 7)
        print(request.session["info"])
        return render(request, 'manager_card.html', {"queryset": queryset, "name": name, "nid": nid})
    else:
        return render(request, 'manager_card.html', {"error_msg": "无该借书证，请检查", "name": name, "nid": nid})

def manager_card_delete(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    nid = request.GET.get('nid')
    print(nid)
    models.card.objects.filter(cno=nid).delete()
    return redirect('/manager/card/', {"name": name})

class CardModelform(forms.ModelForm):
    class Meta:
        model = models.card
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control"}

def manager_card_add(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    if request.method == "GET":
        form = CardModelform()
        return render(request, 'manager_card_add.html', {"form": form, "name": name})

    form = CardModelform(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/manager/card/')

    return render(request, 'manager_card_add.html', {"form": form, "name": name})

class BookModelform(forms.ModelForm):
    num = forms.IntegerField(label='数量')
    book_id = forms.CharField(label='书号')

    class Meta:
        model = models.book
        fields = ['book_id', 'type', 'title',
                  'publisher', 'author', 'year', 'price', 'num']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control"}


def book_add(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    form = BookModelform()
    if request.method == "GET":
        return render(request, 'book_add.html', {"form": form, "name": name})
    data = request.POST
    form = BookModelform(data=request.POST)
    bno = data['book_id']
    if form.is_valid():
        obj = models.book.objects.filter(bno=bno)
        if obj:
            print(data['num'])
            row_object = obj[0]
            row_object.stock = row_object.stock+int(data['num'])
            row_object.total = row_object.total+int(data['num'])
            row_object.save()
        else:
            models.book.objects.create(bno=bno, type=data['type'], title=data['title'], publisher=data['publisher'],
                                       year=data['year'], author=data['author'], price=data['price'], total=data['num'], stock=data['num'])
        return redirect('/book/add/suc/', {"name": name})
    return render(request, 'book_add.html', {"form": form, "name": name})


def book_add_suc(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    if request.method == "GET":
        return render(request, 'book_add_suc.html')
    return redirect('/book/add/', {"name": name})


def book_list(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    search_b = request.GET.get('b', "")
    search_t = request.GET.get('t', "")
    search_a = request.GET.get('a', "")
    search_p = request.GET.get('p', "")
    search_pl = request.GET.get('pl', "")
    search_pr = request.GET.get('pr', "")
    search_yl = request.GET.get('yl', "")
    search_yr = request.GET.get('yr', "")
    order = request.GET.get('order', "")

    res = models.book.objects.all().order_by('bno')

    if search_b:
        res = res.filter(bno__contains=search_b)
    if search_t:
        res = res.filter(title__contains=search_t)
    if search_a:
        res = res.filter(author__contains=search_a)
    if search_p:
        res = res.filter(publisher__contains=search_p)
    res = res.all()[:50]

    return render(request, 'book_list.html', {"name": name, "queryset": res,"search_b":search_b, "search_t": search_t, "search_a": search_a, "search_p": search_p, "search_pl": search_pl, "search_pr": search_pr, "search_yl": search_yl, "search_yr": search_yr, "order": order})

def book_list2(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    search_b = request.GET.get('b', "")
    search_t = request.GET.get('t', "")
    search_a = request.GET.get('a', "")
    search_p = request.GET.get('p', "")
    search_pl = request.GET.get('pl', "")
    search_pr = request.GET.get('pr', "")
    search_yl = request.GET.get('yl', "")
    search_yr = request.GET.get('yr', "")
    order = request.GET.get('order', "")

    res = models.book.objects.all().order_by('bno')

    if search_b:
        res = res.filter(bno__contains=search_b)
    if search_t:
        res = res.filter(title__contains=search_t)
    if search_a:
        res = res.filter(author__contains=search_a)
    if search_p:
        res = res.filter(publisher__contains=search_p)
    res = res.all()[:50]

    return render(request, 'book_list2.html', {"name": name, "queryset": res,"search_b":search_b, "search_t": search_t, "search_a": search_a, "search_p": search_p, "search_pl": search_pl, "search_pr": search_pr, "search_yl": search_yl, "search_yr": search_yr, "order": order})
class Borrowform(forms.Form):
    nid = forms.CharField(
        label="卡号",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    bno = forms.CharField(
        label="书号",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    borrow_date = forms.DateField(
        label="借期(YYYY-MM-DD)",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    return_date = forms.DateField(
        label="预计还期(YYYY-MM-DD)",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )


def book_borrow(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    nid = request.session["info"]["nid"]
    if request.method == "GET":
        form = Borrowform()
        return render(request, 'book_borrow.html', {"form": form, "name": name, "nid": nid})

    form = Borrowform(data=request.POST)

    if form.is_valid():
        data = form.cleaned_data
        nid = data.get('nid') 
        borrow_book = models.book.objects.filter(bno=data['bno'])
        if borrow_book:
            the_book = models.book.objects.filter(bno=data['bno'])[0]

        if (not borrow_book):
            return render(request, 'book_borrow.html', {"form": form, "error_msg": "该图书不存在，请检查", "name": name, "nid": nid})
        elif the_book.stock <= 0:
            earliest_books = models.borrow_list.objects.filter(
                book_id=data['bno']).order_by("return_time")
            if earliest_books:
                earliest_book = earliest_books[0]
                return render(request, 'book_borrow.html', {"form": form, "name": name, "nid": nid, "error_msg": "库存不足，借阅失败,预计最快归还时间: ", "date": earliest_book.return_time})
            else:
                return render(request, 'book_borrow.html', {"form": form, "error_msg": "该图书无库存，请检查", "name": name, "nid": nid})
        else:
            the_book.stock -= 1
            the_book.save()
            models.borrow_list.objects.create(
                book_id=data['bno'], card_id=nid, manager_id=id, borrow_time=data['borrow_date'], return_time=data['return_date'])
            return render(request, 'book_borrow.html', {"form": form, "suc_msg": "借阅成功", "name": name, "nid": nid})
    return render(request, 'book_borrow.html', {"form": form, "name": name, "nid": nid})



def book_borrow2(request):
    name = request.session["info"]["name"]
    nid = request.session["info"]["id"]
    if request.method == "GET":
        form = Borrowform()
        return render(request, 'book_borrow2.html', {"form": form, "name": name, "nid": nid})

    form = Borrowform(data=request.POST)
    if form.is_valid():
        data = form.cleaned_data
        nid = data.get('nid') 
        borrow_book = models.book.objects.filter(bno=data['bno'])
        if borrow_book:
            the_book = models.book.objects.filter(bno=data['bno'])[0]

        if (not borrow_book):
            return render(request, 'book_borrow2.html', {"form": form, "error_msg": "该图书不存在，请检查", "name": name, "nid": nid})
        elif the_book.stock <= 0:
            earliest_books = models.borrow_list.objects.filter(
                book_id=data['bno']).order_by("return_time")
            if earliest_books:
                earliest_book = earliest_books[0]
                return render(request, 'book_borrow2.html', {"form": form, "name": name, "nid": nid, "error_msg": "库存不足，借阅失败,预计最快归还时间: ", "date": earliest_book.return_time})
            else:
                return render(request, 'book_borrow2.html', {"form": form, "error_msg": "该图书无库存，请检查", "name": name, "nid": nid})
        else:
            the_book.stock -= 1
            the_book.save()
            models.borrow_list.objects.create(
                book_id=data['bno'], card_id=nid, borrow_time=data['borrow_date'], return_time=data['return_date'])
            return render(request, 'book_borrow2.html', {"form": form, "suc_msg": "借阅成功", "name": name, "nid": nid})
    return render(request, 'book_borrow2.html', {"form": form, "name": name, "nid": nid})

class Reborrowform(forms.Form):
    nid = forms.CharField(
        label="卡号",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    bno = forms.CharField(
        label="书号",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )
    return_date = forms.DateField(
        label="预计还期(YYYY-MM-DD)",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )


def book_reborrow(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    nid = request.session["info"]["nid"]
    if request.method == "GET":
        form = Reborrowform()
        return render(request, 'book_reborrow.html', {"form": form, "name": name, "nid": nid})

    form = Reborrowform(data=request.POST)

    if form.is_valid():
        data = form.cleaned_data
        nid = data.get('nid') 
        borrow_book = models.book.objects.filter(bno=data['bno'])
        new_return_time = data.get('return_date')

        try:
            borrow_list = models.borrow_list.objects.get(card_id=nid, book_id=data['bno'])
        except models.borrow_list.DoesNotExist:
            return render(request, 'book_reborrow.html', {"form": form, "error_msg": "该借阅记录不存在，请检查", "name": name, "nid": nid})

        borrow_list.return_time = new_return_time
        borrow_list.save()

        return render(request, 'book_reborrow.html', {"form": form, "suc_msg": "续借成功", "name": name, "nid": nid})

    return render(request, 'book_reborrow.html', {"form": form, "name": name, "nid": nid})

def book_reborrow2(request):
    name = request.session["info"]["name"]
    nid = request.session["info"]["id"]
    if request.method == "GET":
        form = Reborrowform()
        return render(request, 'book_reborrow2.html', {"form": form, "name": name, "nid": nid})

    form = Reborrowform(data=request.POST)
    if form.is_valid():
        data = form.cleaned_data
        nid = data.get('nid') 
        borrow_book = models.book.objects.filter(bno=data['bno'])
        new_return_time = data.get('return_date')

        try:
            borrow_list = models.borrow_list.objects.get(card_id=nid, book_id=data['bno'])
        except models.borrow_list.DoesNotExist:
            return render(request, 'book_reborrow2.html', {"form": form, "error_msg": "该借阅记录不存在，请检查", "name": name, "nid": nid})

        borrow_list.return_time = new_return_time
        borrow_list.save()

        return render(request, 'book_reborrow2.html', {"form": form, "suc_msg": "续借成功", "name": name, "nid": nid})

    return render(request, 'book_reborrow2.html', {"form": form, "name": name, "nid": nid})
class Returnform(forms.Form):
    bno = forms.CharField(
        label="书号",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

def book_return(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    nid = request.session["info"]["nid"]

    if request.method == "GET":
        form = Returnform()
        return render(request, 'book_return.html', {"form": form, "name": name, "nid": nid})
    form = Returnform(data=request.POST)
    if form.is_valid():
        data = form.cleaned_data
        bno = data['bno']
        cno = nid
        info = models.borrow_list.objects.filter(book_id=bno, card_id=cno)
        if info:
            obj = info[0]
            obj.delete()
            the_book = models.book.objects.filter(bno=data['bno'])[0]
            the_book.stock += 1
            the_book.save()
            return render(request, 'book_return.html', {"form": form, "suc_msg": "归还成功", "name": name, "nid": nid})
        else:
            return render(request, 'book_return.html', {"form": form, "error_msg": "归还失败，该书不存在该借书证借阅列表中", "name": name, "nid": nid})
    return render(request, 'book_return.html', {"form": form, "name": name, "nid": nid})

def book_return2(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    nid = request.session["info"]["nid"]

    if request.method == "GET":
        form = Returnform()
        return render(request, 'book_return2.html', {"form": form, "name": name, "nid": nid})
    form = Returnform(data=request.POST)
    if form.is_valid():
        data = form.cleaned_data
        bno = data['bno']
        cno = nid
        info = models.borrow_list.objects.filter(book_id=bno, card_id=cno)
        if info:
            obj = info[0]
            obj.delete()
            the_book = models.book.objects.filter(bno=data['bno'])[0]
            the_book.stock += 1
            the_book.save()
            return render(request, 'book_return2.html', {"form": form, "suc_msg": "归还成功", "name": name, "nid": nid})
        else:
            return render(request, 'book_return2.html', {"form": form, "error_msg": "归还失败，该书不存在该借书证借阅列表中", "name": name, "nid": nid})
    return render(request, 'book_return2.html', {"form": form, "name": name, "nid": nid})

def book_modify(request):
    name = request.session["info"]["name"]
    id = request.session["info"]["id"]
    if request.method == "GET":
        request.session["info"]["nid"] = ""
        request.session.set_expiry(60 * 60 * 24 * 7)
        return render(request, 'book_modify.html', {'name': name})

    nid = request.POST.get("nid")
    card = models.card.objects.filter(cno=nid)

    if card:

        books = models.borrow_list.objects.filter(card_id=nid).order_by('book_id')
        request.session["info"]["nid"] = nid
        request.session.set_expiry(60 * 60 * 24 * 7)
        print(request.session["info"])

        queryset = []
        for obj in books:
            book = models.book.objects.get(bno=obj.book_id)
            borrow_info = models.borrow_list.objects.get(book=obj.book_id)
            book.borrow_time = borrow_info.borrow_time
            book.return_time = borrow_info.return_time
            queryset.append(book)
        return render(request, 'book_modify.html', {"queryset": queryset, "name": name, "nid": nid})
    else:
        return render(request, 'book_modify.html', {"error_msg": "无该借书证，请检查", "name": name, "nid": nid})


def book_modify2(request):
    name = request.session["info"]["name"]
    uno = request.session["info"]["id"]  

    if request.method == "GET":
        request.session["info"]["nid"] = ""
        request.session.set_expiry(60 * 60 * 24 * 7)
        books = models.borrow_list.objects.filter(card_id=uno).order_by('book_id')  # 使用读者身份号查询借阅的图书信息
        request.session["info"]["nid"] = uno
        request.session.set_expiry(60 * 60 * 24 * 7)
        print(request.session["info"])

        queryset = []
        for obj in books:
            book = models.book.objects.get(bno=obj.book_id)
            borrow_info = models.borrow_list.objects.get(book=obj.book_id)
            book.borrow_time = borrow_info.borrow_time
            book.return_time = borrow_info.return_time
            queryset.append(book)
        return render(request, 'book_modify2.html', {"queryset": queryset, "name": name, "nid": uno})




