from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic.edit import DeleteView

from models import Host, Subnet
from forms import UserHostForm, UserForm, SubnetForm


@login_required
def index(request):
    return render(request, 'portal/index.html', {
        'own_hosts':  Host.objects.select_related('owner').filter(owner=request.user),
        'authorized_hosts':  Host.objects.select_related('owner').filter(admins=request.user),
        'own_subnets':  Subnet.objects.select_related('owner').filter(owner=request.user),
    })


def all_hosts(request):
    return render(request, 'portal/index.html', {
        'all_hosts':  Host.objects.select_related('owner').all(),
    })


@login_required
def own_hosts(request):
    return render(request, 'portal/index.html', {
        'own_hosts':  Host.objects.select_related('owner').filter(owner=request.user),
        'authorized_hosts':  Host.objects.select_related('owner').filter(admins=request.user),
    })


def all_subnets(request):
    return render(request, 'portal/index.html', {
        'all_subnets':  Subnet.objects.select_related('owner').all(),
    })


@login_required
def own_subnets(request):
    return render(request, 'portal/index.html', {
        'own_subnets':  Subnet.objects.select_related('owner').filter(owner=request.user),
    })


@login_required
def host_detail(request, name=None):
    host = name and Host.objects.get(name=name) or None
    form = UserHostForm(instance=host, request=request)

    if host is None or host.owner == request.user \
    or request.user in host.admins.all():
        can_edit = True
        if request.method == "POST":
            form = UserHostForm(request.POST, instance=host, request=request)
            if form.is_valid():
                form.save()
                messages.success(request, '%s saved.' % form.cleaned_data['name'])
                return HttpResponseRedirect('/')
            else:
                messages.warning(request, 'Form validation error. Details below.')
    else:
        can_edit = False

    return render(request, 'portal/edit_host.html', {
        'host': host,
        'form': form,
        'can_edit': can_edit,
    })


class HostDelete(DeleteView):
    model = Host
    slug_field = 'name'
    success_url = '/host/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(HostDelete, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(HostDelete, self).get_object()

        if obj.owner != self.request.user:
            raise Http404
        return obj


@login_required
def subnet_detail(request, network):
    subnet = Subnet.objects.get(network=network)
    form = SubnetForm(instance=subnet)

    if subnet.owner == request.user:
        can_edit = True
        if request.method == "POST":
            form = SubnetForm(request.POST, instance=subnet)
            if form.is_valid():
                form.save()
                messages.success(request, '%s saved.' % subnet)
                return HttpResponseRedirect('/')
            else:
                messages.warning(request, 'Form validation error. Details below.')
    else:
        can_edit = False

    return render(request, 'portal/edit_host.html', {
        'host': subnet,
        'form': form,
        'can_edit': can_edit,
    })


@login_required
def user_detail(request):
    if request.method == "POST":
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User settings saved.')
            return HttpResponseRedirect('/')
        else:
            messages.warning(request, 'Form validation error. Details below.')
    else:
        form = UserForm(instance=request.user)

    return render(request, 'registration/profile.html', {
        'form': form,
    })
