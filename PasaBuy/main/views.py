from django.shortcuts import render

def index(request):
    return render(request, "index.html")


def hero_page(request):
    return render(request, "heropage.html")


def order_page(request):
    return render(request, 'orderpage.html')


def user_page(request):
    return render(request, 'userpage.html')