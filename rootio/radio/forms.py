# -*- coding: utf-8 -*-

from flask.ext.wtf import Form
from flask.ext.babel import gettext as _
from wtforms.ext.sqlalchemy.orm import model_form
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms import StringField, SelectField, SubmitField, FormField, TextField, TextAreaField, HiddenField, RadioField, IntegerField
from wtforms_components.fields import TimeField
from wtforms.validators import Required, AnyOf
import pytz

from .fields import DurationField, InlineFormField, JSONField
from .validators import HasInlineForm
from .models import Station, StationAnalytic, Program, ProgramType, ScheduledBlock, Person, Language, Location
from .widgets import ChoicesSelect

from ..user.models import User
from ..telephony.forms import PhoneNumberForm

from ..utils import OrderedForm, GENDER_TYPE
from ..extensions import db

LocationFormBase = model_form(Location, db_session=db.session, base_class=Form,
    field_args = {'latitude':{'description': '+N / -S'},
                 'longitude':{'description': '+E / -W'}},
    exclude=['created_at','updated_at'])
class LocationForm(LocationFormBase):
    submit = SubmitField(_('Save'))


def all_users():
    return User.query.all()

#define field help text here, instead of in model info
StationFormBase = model_form(Station, db_session=db.session, base_class=OrderedForm,
    field_args={
        'name':{'description':_('Name or callsign of station')},
        'frequency':{'description':_('Station broadcast frequency')},
        'location':{'validators':[HasInlineForm,]},
        'phone':{'description': _('Station contact telephone number'),'validators':[HasInlineForm,]},
        'owner':{'description': _('User who is the owner of the station')},
        'languages':{'description':_("Primary languages the station will broadcast in")},
        'client_update_frequency':{'description':_("How frequently the transmitter should check for updates, in seconds")},
        'broadcast_ip':{'description':_("IP address of the transmitter on the local network. Should start with 230.")},
    },
    exclude=['scheduled_programs','blocks','created_at','updated_at','analytics'])
class StationForm(StationFormBase):
    owner = QuerySelectField(query_factory=all_users,allow_blank=False) #TODO: default this to be the logged in user?
    phone_inline = InlineFormField(PhoneNumberForm,description='/telephony/phonenumber/add/ajax/')
        #inline form and POST url for phone creation modal
        #ugly overloading of the description field. WTForms won't let us attach any old random kwargs...
    location_inline = InlineFormField(LocationForm, description='/radio/location/add/ajax/')
    timezone = SelectField(choices=[(val, val) for val in pytz.common_timezones], default="UTC")
    submit = SubmitField(_('Save'))
    field_order = ('owner','name','location','timezone','*')


StationAnalyticForm = model_form(StationAnalytic, db_session=db.session, base_class=Form)


def all_languages():
    return Language.query.all()
def all_program_types():
    return ProgramType.query.all()
class ProgramForm(Form):
    #can't use model_form, because we want to use a custom field for time duration
    name = StringField()
    description = TextAreaField()
    duration = DurationField(description=_("Duration of the program, in HH:MM(:SS)"))
    language = QuerySelectField(query_factory=all_languages,allow_blank=False)
    program_type = QuerySelectField(query_factory=all_program_types,allow_blank=False)
    submit = SubmitField(_('Save'))


ProgramTypeFormBase = model_form(ProgramType, db_session=db.session, base_class=Form,
    field_args={
        'definition':{"description":_("This field expects JSON")},
        'phone_functions':{"description":_("This field expects JSON")},
    }, exclude=['created_at','updated_at'])
class ProgramTypeForm(ProgramTypeFormBase):
    definition = JSONField()
    phone_functions = JSONField()
    submit = SubmitField(_('Save'))


PersonFormBase = model_form(Person, db_session=db.session, base_class=Form)
class PersonForm(PersonFormBase):
    gender_code = RadioField(u"Gender", [AnyOf([str(val) for val in GENDER_TYPE.keys()])],
            choices=[(str(val), label) for val, label in GENDER_TYPE.items()])
    submit = SubmitField(_('Save'))


LanguageFormBase = model_form(Language, db_session=db.session, base_class=Form,
    only=['name','iso639_1','iso639_2','locale_code'],) #explicitly include only these fields, so we don't have to exclude m2m fks
class LanguageForm(LanguageFormBase):
    submit = SubmitField(_('Save'))


def all_stations():
    return Station.query.all()
class BlockForm(Form):
    name = StringField()
    station = QuerySelectField(query_factory=all_stations,allow_blank=False)
    start_time = TimeField()
    end_time = TimeField()
    recurrence = HiddenField()
    submit = SubmitField(_('Save'))


def all_programs():
    return Program.query.all()
def all_blocks():
    return ScheduledBlock.query.all()
class ScheduleProgramForm(Form):
    station = QuerySelectField(query_factory=all_stations,allow_blank=False)
    program = QuerySelectField(query_factory=all_programs,allow_blank=True,blank_text='- select program -')
    #block = QuerySelectField(query_factory=all_blocks,allow_blank=False) #let user select block?
    air_time = TimeField(description=_("Time to begin airing"))
    recurrence = HiddenField()
    #priority = IntegerField(description=_("Ascending values"))
    # other options for flexibility?
    submit = SubmitField(_('Save'))
