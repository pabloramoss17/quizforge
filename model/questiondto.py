import sirope

class QuestionDto:
    def __init__(self, question_text, options, correct_option):
        self._question_text = question_text
        self._options = options
        self._correct_option = correct_option

    @property
    def question_text(self):
        return self._question_text

    @property
    def options(self):
        return self._options

    @property
    def correct_option(self):
        return self._correct_option

    @property
    def namespace(self):
        return "questions"

    @staticmethod
    def find(s: sirope.Sirope, question_text: str) -> "QuestionDto":
        return s.find_first(QuestionDto, lambda q: q.question_text == question_text)
