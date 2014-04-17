from ipaddr import IPAddress

from django import forms
from django.contrib.auth.models import User

from models import Host, Subnet


class HostForm(forms.ModelForm):
    class Meta:
        model = Host
        # fields = '__all__'  # needed in future version of Django


class UserHostForm(HostForm):
    """Allows users to edit their Host details."""
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UserHostForm, self).__init__(*args, **kwargs)

        self.fields['admins'].widget.attrs['size'] = "10"
        user_qs = User.objects.order_by('username')
        self.fields['admins'].queryset = user_qs
        self.fields['owner'].queryset = user_qs

    def clean_name(self):
        """Require hostname to start with callsign"""
        name = self.cleaned_data['name']
        user = self.request.user.username
        if name != user and not name.endswith('.%s' % user):
            raise forms.ValidationError("Name must end with %s." % user)
        return name


    def clean_eth_ipv4(self):
        instance = getattr(self, 'instance', None)
        ip = self.cleaned_data['eth_ipv4']
        print repr(ip)
        if instance and instance.pk and instance.eth_ipv4 == ip:
            # allow editing hosts outside your allocation, but can't change ip
            return ip
        elif any([IPAddress(ip) in net.network for net in self.request.user.subnets_owned.all()]):
            # allow saving hosts with IPs in user's subnet allocations
            return ip
        else:
            raise forms.ValidationError("IP must be in your subnet.")


class SubnetForm(forms.ModelForm):
    class Meta:
        model = Subnet
        fields = ['notes']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
