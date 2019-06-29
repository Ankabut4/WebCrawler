"""
Definition of urls for webcrawler.
"""

from datetime import datetime
from django.conf.urls import url
import django.contrib.auth.views

import app.forms
import app.views

# Uncomment the next lines to enable the admin:
# from django.conf.urls import include
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = [
    # Examples:
    url(r'^$', app.views.scan_sites, name='home'),
    url(r'^contact$', app.views.contact, name='contact'),
    url(r'^about$', app.views.about, name='about'),
	url(r'^scan-sites$', app.views.scan_sites, name='scan-sites'),
    url(r'^ajax-scan-sites$', app.views.ajax_scan_sites, name='ajax-scan-sites'),
    url(r'^ajax-search$', app.views.ajax_search, name='ajax-search$'),
    url(r'^json-status$', app.views.json_status, name='json-status'),
    url(r'^json-sites$', app.views.json_sites, name='json-sites'),
    url(r'^json-stats', app.views.json_stats, name='json-stats'),
    url(r'^login/$',
        django.contrib.auth.views.login,
        {
            'template_name': 'app/login.html',
            'authentication_form': app.forms.BootstrapAuthenticationForm,
            'extra_context':
            {
                'title': 'Log in',
                'year': datetime.now().year,
            }
        },
        name='login'),
    url(r'^logout$',
        django.contrib.auth.views.logout,
        {
            'next_page': '/',
        },
        name='logout'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
]
