from . import views
from django.urls import path
# from django.views.generic import TemplateView


app_name = 'support'

urlpatterns = [

    path('contact-us', views.contact_us, name='contactus'),
    # path('send_message', views.send_message, name='send_message'),
    # path('support/contact-us', TemplateView.as_view(template_name="contactus.html"), name="contactus"),

]
