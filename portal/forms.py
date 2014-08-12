import ipaddr

from django import forms
from django.contrib.auth.models import User

from models import Host, IPAddress, Subnet


class HostForm(forms.ModelForm):
    class Meta:
        model = Host
        # fields = '__all__'  # needed in future version of Django
        exclude = ['site']


class UserHostForm(HostForm):
    """Allows users to edit their Host details."""
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UserHostForm, self).__init__(*args, **kwargs)

        self.fields['admins'].widget.attrs['size'] = "10"
        user_qs = User.objects.order_by('username')
        self.fields['admins'].queryset = user_qs
        self.fields['owner'].queryset = user_qs
        self.fields['owner'].initial = self.request.user

    def clean_name(self):
        """Require hostname to start with callsign"""
        instance = getattr(self, 'instance', None)
        name = self.cleaned_data['name'].lower()

        if instance and instance.pk and instance.name.lower() == name:
            # hostname hasn't changed, allow
            return self.cleaned_data['name']

        user = self.request.user.username.lower()
        if name != user and not name.endswith('.%s' % user):
            raise forms.ValidationError("Name must end with %s." % user)
        return self.cleaned_data['name']


class IPAddressForm(forms.ModelForm):
    class Meta:
        model = IPAddress


class UserIPAddressForm(IPAddressForm):
    """Allows users to edit their IPAddress details."""
    def clean_ip(self):
        """Require IP address to be in user's subnet"""
        subnets = Subnet.objects.filter(owner=self.instance.host.owner)

        try:
            ip = ipaddr.IPAddress(self.cleaned_data['ip'])
        except ValueError, e:
            raise forms.ValidationError(e)

        if not any([ip in subnet.network for subnet in subnets]):
            raise forms.ValidationError('Address must be in your subnet.')

        return ip


class IPAddressFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        super(IPAddressFormset, self).clean()

        if any(self.errors):
            return

        if sum([form.cleaned_data.get('primary', False) for form in self.forms]) > 1:
            raise forms.ValidationError("Only one interface may be primary.")


class SubnetForm(forms.ModelForm):
    class Meta:
        model = Subnet


class UserSubnetForm(SubnetForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UserSubnetForm, self).__init__(*args, **kwargs)

        user_qs = User.objects.order_by('username')
        self.fields['owner'].queryset = user_qs
        self.fields['owner'].initial = self.request.user

    def clean_network(self):
        """Require network to be in user's subnet"""
        subnets = Subnet.objects.filter(owner=self.request.user)

        try:
            net = ipaddr.IPNetwork(self.cleaned_data['network'])
        except ValueError, e:
            raise forms.ValidationError(e)

        if not any([net in subnet.network for subnet in subnets]):
            raise forms.ValidationError('Network must be in your subnet.')

        return net



class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
