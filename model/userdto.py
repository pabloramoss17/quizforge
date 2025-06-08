import flask_login
import sirope
import werkzeug.security as safe

class UserDto(flask_login.UserMixin):
    def __init__(self, email, password):
        self._email = email
        self._password = safe.generate_password_hash(password)
        self._messages_oids = []

    @property
    def email(self):
        return self._email

    @property
    def oids_messages(self):
        if not self.__dict__.get("_messages_oids"):
            self._messages_oids = []
        return self._messages_oids

    def get_id(self):
        return self.email

    def chk_password(self, pswd):
        return safe.check_password_hash(self._password, pswd)

    def add_message_oid(self, message_oid):
        self.oids_messages.append(message_oid)

    @staticmethod
    def current_user():
        usr = flask_login.current_user
        if usr.is_anonymous:
            flask_login.logout_user()
            usr = None
        return usr

    @staticmethod
    def find(s: sirope.Sirope, email: str) -> "UserDto":
        return s.find_first(UserDto, lambda u: u.email == email)
