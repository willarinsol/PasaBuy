from django.shortcuts import render

def index(request):
    return render(request, "index.html")


def hero_page(request):
    return render(request, "heropage.html")


def browser(request):
    return render(request, "browser.html")


def my_orders(request):
    return render(request, "myorders.html")


def upload_id(request):
    return render(request, "index.html", {"initial_view": "upload"})