from .config import (SUCCESS_CODE, SUCCESS_MESSAGE)

class Response:
    def __init__(self, question_type, questions, hint):
        self.question_type = question_type
        self.questions = questions
        self.hint = hint
    
    def to_dict(self):
        return {
            "status": {
                "code": SUCCESS_CODE,
                "message": SUCCESS_MESSAGE
            },
            "payload": {
                "question_type": self.question_type,
                "questions": self.questions,
                "hint": self.hint
            }
        }
