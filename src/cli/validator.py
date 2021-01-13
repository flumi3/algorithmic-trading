import re

from prompt_toolkit.document import Document
from prompt_toolkit.validation import Validator, ValidationError


class NumberValidator(Validator):
    def validate(self, document: Document) -> None:
        text: str = document.text

        if text and not text.isdigit():
            index = 0
            # Get index of first non numeric character. We want to move the cursor here.
            for index, char in enumerate(text):
                if not char.isdigit():
                    break
            raise ValidationError(message="This input contains non-numeric characters", cursor_position=index)


class FloatValidator(Validator):
    def validate(self, document: Document) -> None:
        text: str = document.text

        if text and not text.isdigit():
            if not re.search(r"\d+\.\d+", text):
                index = 0
                # Get index of first non numeric character. We want to move the cursor here.
                for index, char in enumerate(text):
                    if not char.isdigit():
                        break
                raise ValidationError(message="This input contains non-numeric characters", cursor_position=index)


class YesNoValidator(Validator):
    def validate(self, document: Document) -> None:
        text: str = document.text

        if text and (text != "y") and (text != "n") and (len(text) > 0):
            index = 0
            for index, char in enumerate(text):
                if char != "y" and char != "n":
                    break
            raise ValidationError(message="This input contains invalid characters.", cursor_position=index)