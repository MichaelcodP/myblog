from django.http import HttpResponse


def home(request):
    return HttpResponse(
        "<h1>Welcome to MyBlog API 🚀</h1><p>Backend is running successfully.</p>"
    )
