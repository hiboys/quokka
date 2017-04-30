# coding: utf-8

from mongoengine import fields
from mongoengine.base.datastructures import BaseList
from wtforms import ValidationError
from wtforms.fields import Field
from quokka.core import widgets
from flask import request
from flask_captcha.views import validate_captcha


class MultipleObjectsReturned(Exception):
    pass


def match_all(i, kwargs):
    # use generator expression?
    return all(getattr(i, k) == v for k, v in kwargs.items())


def getinstance(_instance):
    return _instance.__class__.objects.get(pk=_instance.pk)


def only_matches(obj, kwargs, silent=True):
    if not kwargs and silent:
        return obj
    return filter(lambda i: match_all(i, kwargs), obj)


def _exclude(self):
    def inner(*args, **kwargs):
        _values = only_matches(self, kwargs, silent=False)
        values = [item for item in self if item not in _values]
        return FilteredList(values, getinstance(self._instance), self._name)
    return inner


def _filter(self):
    def inner(*args, **kwargs):
        values = only_matches(self, kwargs)
        return FilteredList(values, getinstance(self._instance), self._name)
    return inner


def _get(self):
    def inner(*args, **kwargs):
        values = only_matches(self, kwargs)
        values = list(values)
        if len(values) > 1:
            raise MultipleObjectsReturned("More than one object returned")
        return values and values[0]
    return inner


def _delete(self):
    def inner(*args, **kwargs):
        values = only_matches(self, kwargs)
        for item in values:
            self.remove(item)
        self._instance.save()
        self._instance.reload()
        if len(values) > 1:
            return FilteredList(values,
                                getinstance(self._instance),
                                self._name)
        else:
            return values and values[0]
    return inner


def _create(self):
    def inner(*args, **kwargs):
        instance = self._instance
        item_cls = instance._fields[self._name].field.document_type_obj
        item = item_cls(**kwargs)
        self.append(item)
        instance.save()
        return item
    return inner


def update_item(item, new_values):
    if not isinstance(new_values, dict):
        return
    for k, v in new_values.items():
        setattr(item, k, v)


def _update(self):
    def inner(new_values, **kwargs):
        values = only_matches(self, kwargs)
        for item in values:
            update_item(item, new_values)
        self._instance.save()
        self._instance.reload()
        if len(values) > 1:
            return FilteredList(values,
                                getinstance(self._instance),
                                self._name)
        else:
            return values and values[0]
    return inner


def _count(self):
    def inner(*args, **kwargs):
        return len(self)
    return inner


def inject(obj):
    setattr(obj, 'filter', _filter(obj))
    setattr(obj, 'get', _get(obj))
    setattr(obj, 'delete', _delete(obj))
    setattr(obj, 'create', _create(obj))
    setattr(obj, 'exclude', _exclude(obj))
    setattr(obj, 'count', _count(obj))
    setattr(obj, 'update', _update(obj))


class FilteredList(BaseList):
    def __init__(self, *args, **kwargs):
        super(FilteredList, self).__init__(*args, **kwargs)
        inject(self)


class ListField(fields.ListField):

    validators = []  # should be removed when flask.mongoengine updates
    filters = []  # should be removed ""

    def __get__(self, *args, **kwargs):
        value = super(ListField, self).__get__(*args, **kwargs)
        inject(value)
        return value


class Captcha(object):
    """Validates a ReCaptcha."""

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        captcha_key = request.form.get("captcha_key", "")
        captcha_value = request.form.get("captcha_value", "").strip().lower()
        if not validate_captcha(captcha_key, captcha_value):
            raise ValidationError("unvalid captcha")


class CaptchaField(Field):
    widget = widgets.CaptchaWidget()

    # error message if recaptcha validation fails
    captcha_error = None

    def __init__(self, label='', validators=None, **kwargs):
        validators = validators or [Captcha()]
        super(CaptchaField, self).__init__(label, validators, **kwargs)

