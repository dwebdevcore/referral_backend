from django.contrib.admin import ModelAdmin
from django.forms import MediaDefiningClass


class DoNotShowFullResultCountModelAdmin(ModelAdmin):
    show_full_result_count = False


class TimeStampedModelAdminMetaclass(MediaDefiningClass):
    def __new__(mcs, name, bases, attrs) -> 'TimeStampedModelAdmin':
        new = super().__new__(mcs, name, bases, attrs)
        new.list_display = [
                               'pk',
                           ] + list(new.list_display) + [
                               'created',
                               'modified',
                           ]
        return new


class TimeStampedModelAdmin(DoNotShowFullResultCountModelAdmin,
                            metaclass=TimeStampedModelAdminMetaclass):
    pass
