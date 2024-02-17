from ipaddr import IPAddress

from django import forms

from portal.models import Subnet
from models import Record


class RecordForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(RecordForm, self).__init__(*args, **kwargs)
        self.fields['domain'].required = True
        self.fields['name'].required = True
        self.fields['type'].required = True
        self.fields['content'].required = True

    def clean_name(self):
        """Require name to end with callsign.hamwan.net"""
        instance = getattr(self, 'instance', None)
        name = self.cleaned_data['name'].lower()
        user = self.request.user
        subdomain = "%s.hamwan.net" % user.username.lower()
        subnets = Subnet.objects.filter(owner=user)

        if instance and instance.pk:
            # record is being edited. Make sure original values belong to user.
            if instance.name != subdomain and \
               not instance.name.endswith(".%s" % subdomain):
                try:
                    ip = self._rev_to_ip(instance.name)
                except ValueError:
                    raise forms.ValidationError("This record isn't yours.")
                if not any([(ip in subnet.network) for subnet in subnets]):
                    # reverse is not valid either
                    raise forms.ValidationError("This record isn't yours.")

        if name != subdomain and \
           not name.endswith(".%s" % subdomain):
            # name doesn't end with user.hamwan.net, check reverse
            try:
                ip = self._rev_to_ip(name)
            except ValueError:
                raise forms.ValidationError("This record isn't yours.")
            if ip is None or \
               not any([(ip in subnet.network) for subnet in subnets]):
                # reverse is not valid either
                raise forms.ValidationError("Name must end with %s." % subdomain)

        return name

    def _rev_to_ip(self, name):
        rev = name.split('.in-addr.arpa')[0]
        rev = rev.split('.')
        if len(rev) != 4:
            return None
        return IPAddress('.'.join(rev[::-1]))

    class Meta:
        model = Record
        exclude = []
