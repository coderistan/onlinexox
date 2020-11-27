# coding: utf-8
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.http.request import HttpRequest
import urllib

def index(request):
    return render(request,"index.html",{})

def computer(request):
    return render(request,"computer.html",{})

def friend(request:HttpRequest):
    if request.GET.get("invite"):
        invite_url = urllib.parse.urljoin(request.get_raw_uri(),"?invite={}".format(request.GET.get("invite")))

        return render(request,"friend.html",{
            "davet_kodu":request.GET.get("invite"),
            "davet_link":invite_url,
            "invite":True})
            
    else:
        random_string = get_random_string(length=16)
        invite_url = urllib.parse.urljoin(request.get_raw_uri(),"?invite={}".format(random_string))

        return render(request,"friend.html",{
            "davet_kodu":random_string,
            "davet_link":invite_url,
            "invite":False})