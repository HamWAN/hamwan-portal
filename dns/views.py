import itertools
from ipaddr import IPAddress

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.db.models import Q

from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from models import Record
from portal.models import Subnet
from portal.network import reverse
from forms import RecordForm


class RecordCreate(CreateView):
    model = Record
    form_class = RecordForm
    success_url = '/dns/'
    template_name = 'dns/record_form.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RecordCreate, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(RecordCreate, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class RecordUpdate(UpdateView):
    model = Record
    form_class = RecordForm
    success_url = '/dns/'
    template_name = 'dns/record_form.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RecordUpdate, self).dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super(RecordUpdate, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs


class RecordDelete(DeleteView):
    model = Record
    success_url = '/dns/'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(RecordDelete, self).dispatch(*args, **kwargs)

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(RecordDelete, self).get_object()
        subdomain = "%s.hamwan.net" % self.request.user.username.lower()
        subnets = Subnet.objects.filter(owner=self.request.user)

        if obj.name != subdomain and \
           not obj.name.endswith(".%s" % subdomain):
            # name doesn't end with user.hamwan.net, check reverse
            try:
                ip = IPAddress(reverse(obj.name))
            except ValueError:
                raise Http404
            if not any([(ip in subnet.network) for subnet in subnets]):
                # reverse is not valid either
                raise Http404
        return obj


class RecordListView(ListView):
    model = Record
    template_name = 'dns/index.html'
    paginate_by = 200


@login_required
def own_dns(request):
    # own_hosts = Host.objects.select_related('owner').filter(owner=request.user)
    hostname_suffix = "%s.hamwan.net" % request.user.username
    user_subnets = Subnet.objects.filter(owner=request.user)
    return render(request, 'dns/dns.html', {
        'own_dns':  Record.objects.filter(
            Q(name__iendswith=hostname_suffix) | \
            Q(name__in=set(itertools.chain(
                *[subnet.get_all_reverse() for subnet in user_subnets])))
        ),
    })
