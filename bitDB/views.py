from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.http import HttpResponseRedirect

from bitDB.forms import Form_cache, Form_DB
from bitDB.caches import CacheForViewDB, CacheForViewCache

def get_name(request):
    if request.method == 'POST':
        data=request._get_post()
        if 'transfer' in data:
            return act_trasfer(request)
        elif 'reset' in data:
            return act_reset(request)
        elif 'add' in data:
            return act_add(request)
        elif 'delete' in data:
            return act_delete(request)
        elif 'change' in data:
            return act_change(request)
        elif 'apply' in data:
            return act_apply(request)
        elif 'root' in data:
            return act_add_root(request)
    # if a GET (or any other method) we'll create a blank form
    else:
        form1 = Form_cache(action=None)
        form2 = Form_DB()
        return render(request, 'index.html', {'form1': form1, 'form2': form2})

def act_trasfer(request):
    form1 = Form_cache(action=None)
    form2 = Form_DB(request.POST)
    if form2.is_valid():
        transfer_elementID = form2.cleaned_data['choice_element']
        cache_obj = CacheForViewCache()
        cache_obj.transfer_data(elementID=int(transfer_elementID))
        return HttpResponseRedirect('/index/')
    return render(request, 'index.html', {'form1': form1, 'form2': form2})

def act_reset(request):
    cache_obj = CacheForViewCache()
    cache_obj.reset_data()
    return HttpResponseRedirect('/index/')

def act_add(request):
    form1 = Form_cache(request.POST, action='add')
    form2 = Form_DB()
    if form1.is_valid():
        parent_elementID = form1.cleaned_data['choice_element']
        value = form1.cleaned_data['add_change']
        cache_obj = CacheForViewCache()
        cache_obj.add_data(value=value, parent_elementID=int(parent_elementID))
        return HttpResponseRedirect('/index/')
    return render(request, 'index.html', {'form1': form1, 'form2': form2})

def act_delete(request):
    form1 = Form_cache(request.POST, action='delete')
    form2 = Form_DB()
    if form1.is_valid():
        elementID = form1.cleaned_data['choice_element']
        cache_obj = CacheForViewCache()
        cache_obj.delete_data(elementID=int(elementID))
        return HttpResponseRedirect('/index/')
    return render(request, 'index.html', {'form1': form1, 'form2': form2})

def act_change(request):
    form1 = Form_cache(request.POST, action='change')
    form2 = Form_DB()
    if form1.is_valid():
        elementID = form1.cleaned_data['choice_element']
        value = form1.cleaned_data['add_change']
        cache_obj = CacheForViewCache()
        cache_obj.change_data(value=value, elementID=int(elementID))
        return HttpResponseRedirect('/index/')
    return render(request, 'index.html', {'form1': form1, 'form2': form2})

def act_apply(request):
    cache_obj = CacheForViewCache()
    cache_obj.apply_data()
    return HttpResponseRedirect('/index/')

def act_add_root(request):
    form1 = Form_cache(request.POST, action='root')
    form2 = Form_DB()
    if form1.is_valid():
        parent_elementID = form1.cleaned_data['choice_element']
        value = form1.cleaned_data['add_change']
        cache_obj = CacheForViewCache()
        cache_obj.add_data(value=value, parent_elementID=0)
        return HttpResponseRedirect('/index/')
    return render(request, 'index.html', {'form1': form1, 'form2': form2})
