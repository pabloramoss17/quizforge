import sirope
from datetime import datetime

class AttemptDto:
    def __init__(self, user_email, quiz_title, answers, score):
        self._user_email = user_email
        self._quiz_title = quiz_title
        self._answers = answers 
        self._score = score
        self._date = datetime.now()

    @property
    def user_email(self):
        return self._user_email

    @property
    def quiz_title(self):
        return self._quiz_title

    @property
    def answers(self):
        return self._answers

    @property
    def score(self):
        return self._score

    @property
    def date(self):
        return self._date

    @staticmethod
    def find_by_user(s: sirope.Sirope, user_email: str):
        return list(s.filter(AttemptDto, lambda a: a.user_email == user_email))