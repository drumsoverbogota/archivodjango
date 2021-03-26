from django.contrib.auth.mixins import LoginRequiredMixin

from django.utils import timezone

from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DetailView
from django.views.generic import DeleteView
from django.shortcuts import render
from django.urls import reverse

from .models import Entrada
from .forms import CreateEntradaForm

class EntradaDetailView(DetailView):
    template_name = 'entrada/detail.html'
    model = Entrada

class EntradaEditView(LoginRequiredMixin, UpdateView):
    login_url = '/login'
    template_name = 'entrada/edit.html'
    form_class = CreateEntradaForm
    model = Entrada

    def form_valid(self, form):

        nueva_entrada = form.save(commit=False)
        nueva_entrada.fecha = timezone.now()
        nueva_entrada.save()

        form.save_m2m()
        self.success_url = reverse('entrada:detail', kwargs={
                                   'pk': nueva_entrada.id})
        return super().form_valid(form)

class EntradaCreateView(LoginRequiredMixin, CreateView):
    login_url = '/login'
    template_name = 'entrada/edit.html'
    form_class = CreateEntradaForm
    success_url = '/'

    def form_valid(self, form):

        nueva_entrada = form.save(commit=False)
        nueva_entrada.fecha = timezone.now()
        nueva_entrada.save()

        form.save_m2m()
        self.success_url = reverse('entrada:detail', kwargs={
                                   'pk': nueva_entrada.id})
        return super().form_valid(form)

class DeleteEntradaView(LoginRequiredMixin, DeleteView):
    login_url = '/login'
    template_name = 'entrada/delete.html'
    model = Entrada
    success_url = '/'