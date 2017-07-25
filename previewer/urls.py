from django.conf.urls import url

from views import MockDataTemplateView

urlpatterns = [
    url(r'(?P<template_name>.*\.html)$', MockDataTemplateView.as_view())
    ]
