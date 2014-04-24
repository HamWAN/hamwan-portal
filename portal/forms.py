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


class SubnetForm(forms.ModelForm):
    class Meta:
        model = Subnet
        fields = ['notes']


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
