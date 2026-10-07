from django.shortcuts import render

def index(request):
    return render(request, "index.html")


def hero_page(request):
    return render(request, "heropage.html")