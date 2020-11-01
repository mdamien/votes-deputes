"""nosdeputes URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from .views import homepage, depute, depute_dossier, depute_etape, depute_article, \
    top_pour, top_contre, top_pour_pourcentage, top_contre_pourcentage, top_pour_lois, \
    deputes_inactifs, depute_scrutin

urlpatterns = [
    path('', homepage),
    path('deputes/inactifs', deputes_inactifs),
    path('top/pour', top_pour),
    path('top/pour/lois', top_pour_lois),
    path('top/pour-pourcentage', top_pour_pourcentage),
    path('top/contre', top_contre),
    path('top/contre-pourcentage', top_contre_pourcentage),
    path('<dep_id>', depute),
    path('<dep_id>/dossier/<dos_id>', depute_dossier),
    path('<dep_id>/etape/<etape_id>', depute_etape),
    path('<dep_id>/scrutin/<scrutin_id>', depute_scrutin),
    path('<dep_id>/etape/<etape_id>/article/<article>', depute_article),
]
