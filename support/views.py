from .forms import ContactForm
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib import messages


def contact_us(request):
    form = ContactForm(request.POST or None)
    print(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            subject = "Message from Blaustock Website User"
            from_email = form.cleaned_data['from_email']
            message = form.cleaned_data['message'] + "\r\n Sent by " + form.cleaned_data['from_name'] + "\r\n Email  " + form.cleaned_data['from_email'] + "\r\n Phone " + str(form.cleaned_data['phone'])
            try:
                send_mail(subject, message, from_email, ['blaustock@gmail.com'])
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
            messages.success(
                request, ' Thank you for contacting us. This email is checked regularly during our business hours. We’ll get back to you as soon as possible, usually within a few hours.')
            return redirect('home')
        print('FOrm is invalid')
    return render(request, 'contactus.html', {'contact_form': form})