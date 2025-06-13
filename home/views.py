import json
from decouple import config
from django.shortcuts import render
from django.http import JsonResponse

from .utils import get_response
import wikipediaapi

def home_view(request):
    if not request.session.get("last_highlight", ""):
        request.session["last_highlight"] = ""
    return render(request, "home.html", {"highlight": request.session["last_highlight"]})

def get_highlighted_text(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print(data)
        text = data.get("message", "")
        if text:
            response = get_response(text)
            print(response)
            if not response:
                return JsonResponse({"error": True})
            request.session["last_highlight"] = response
            return JsonResponse({"highlight": response})
        
def get_tooltip_data(request):
    data = request.GET.get("term", "")
    print(data)
    wiki = wikipediaapi.Wikipedia(
        user_agent=f"KeyPoint/1.0 ({config('EMAIL')})",
        language='en')
    page = wiki.page(data)

    if page.exists():
        summary = page.summary[0:500]
        link = page.fullurl
        return JsonResponse({
            "summary": summary,
            "link": link
        })
    else:
        return JsonResponse({"summary": False})
    



