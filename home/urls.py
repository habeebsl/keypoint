from django.urls import path
from .views import home_view, get_highlighted_text, get_tooltip_data


urlpatterns = [
    path("", home_view, name="home"),
    path("send_message", get_highlighted_text, name="highlight"),
    path("fetch-summary", get_tooltip_data, name="summary")
]