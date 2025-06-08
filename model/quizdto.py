import sirope

class QuizDto:
    def __init__(self, title, description, user_email):
        self._title = title
        self._description = description
        self._user_email = user_email
        self._questions_oids = []
        self._oid = None 

    @property
    def title(self):
        return self._title

    @property
    def description(self):
        return self._description

    @property
    def user_email(self):
        return self._user_email

    @property
    def questions_oids(self):
        return self._questions_oids

    @property
    def oid(self):
        return self._oid

    def add_question_oid(self, question_oid):
        self._questions_oids.append(question_oid)

    @property
    def namespace(self):
        return "quizzes"

    @staticmethod
    def find(s: sirope.Sirope, title: str) -> "QuizDto":
        return s.find_first(QuizDto, lambda q: q.title == title)

