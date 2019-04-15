from django import forms

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from bitDB.models import Element
from bitDB.caches import CacheForViewDB, CacheForViewCache

class Form_cache(forms.Form):
    def __init__(self, *args, **kwargs):
        self.action=kwargs.pop('action')
        self.cache = CacheForViewCache()
        super(Form_cache, self).__init__(*args, **kwargs)
        self.fields["choice_element"].choices = self.cache.get_choicelist()

    choice_element = forms.ChoiceField( label=None,
                                        #((1, _("TEST"))) - need for debugging
                                        choices=((1, _("TEST1")),
                                                 (2, _("TEST2"))
                                                ),
                                        required=False,
                                        widget=forms.Select(attrs={'size': '26'})
                                        )
    add_change = forms.CharField(label='Add/Change element',
                                 required=False,
                                 max_length=20)

    def clean(self):
        cleaned_data = super(Form_cache, self).clean()
        add_change = cleaned_data.get("add_change")
        choice_element = cleaned_data.get("choice_element")
        if self.action=='root':
            if (add_change is None) or add_change=='':
                raise forms.ValidationError("You did not fill in the Add/Change Element field")
        elif (self.action=='add') or (self.action=='change'):
            if (choice_element is None) or choice_element=='':
                raise forms.ValidationError("You have not selected any element!")
            choice_element = int(choice_element)
            if self.cache.check_element_is_removed(choice_element):
                raise forms.ValidationError("Removed element. Cannot be selected!")
            elif self.cache.check_element_is_delete(choice_element):
                raise forms.ValidationError("Element will be deleted. Cannot be selected!")
            elif (add_change is None) or add_change=='':
                raise forms.ValidationError("You did not fill in the Add/Change Element field")
        elif (self.action=='delete'):
            if (choice_element is None) or choice_element=='':
                raise forms.ValidationError("You have not selected any element!")
            choice_element = int(choice_element)
            if self.cache.check_element_is_removed(choice_element):
                raise forms.ValidationError("Removed element. Cannot be selected!")
            elif self.cache.check_element_is_delete(choice_element):
                raise forms.ValidationError("Element will be deleted. Cannot be selected!")
        return cleaned_data

class Form_DB(forms.Form):
    def __init__(self, *args, **kwargs):
        self.cache=CacheForViewCache()
        self.cache_DB=CacheForViewDB()
        super(Form_DB, self).__init__(*args, **kwargs)
        self.fields["choice_element"].choices = self.cache_DB.get_choicelist()

    choice_element = forms.ChoiceField(label=None,
                                        #((1, _("TEST"))) - need for debugging
                                       choices=((1, _("TEST1")),
                                                (2, _("TEST2"))
                                                ),
                                       required=True,
                                       widget=forms.Select(attrs={'size': '26'})
                                       )
    def clean(self):
        cleaned_data = super(Form_DB, self).clean()
        choice_element = cleaned_data.get("choice_element")
        if choice_element is None:
            raise forms.ValidationError("You have not selected any element!")
        choice_element = int(choice_element)
        if self.cache_DB.check_element_is_removed(choice_element):
            raise forms.ValidationError("Removed element. Cannot be selected!")
        if self.cache.check_id_in_cache(choice_element):
            raise forms.ValidationError("This element cache already has!")
        return cleaned_data
