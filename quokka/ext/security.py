from flask_security.forms import RegisterForm, Required, LoginForm
from flask_security import Security as _Security
from flask_security import MongoEngineUserDatastore
from flask_wtf import RecaptchaField
from wtforms import TextField
from quokka.modules.accounts.models import Role, User
from quokka.core.templates import render_template
from quokka.core.fields import CaptchaField


class Security(_Security):
    def render_template(self, *args, **kwargs):
        return render_template(*args, **kwargs)


class ExtendedRegisterForm(RegisterForm):
    name = TextField('Name', [Required()])


class RecaptchaForm(ExtendedRegisterForm):
    recaptcha = RecaptchaField()


class ExtendedLoginForm(LoginForm):
    captcha = CaptchaField("Captcha")

def configure(app, db):
    register_form = ExtendedRegisterForm
    confirm_register_form = ExtendedRegisterForm
    if app.config.get('SECURITY_RECAPTCHA_ENABLED'):
        register_form = RecaptchaForm
        confirm_register_form = RecaptchaForm
    app.security = Security(
        app=app,
        datastore=MongoEngineUserDatastore(db, User, Role),
        register_form=register_form,
        confirm_register_form=confirm_register_form,
        login_form = ExtendedLoginForm
    )
