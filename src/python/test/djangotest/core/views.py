import sys
import os
sys.path.append(
    os.path.join(
        os.path.dirname(
            os.path.dirname(
                os.path.dirname(
                    os.path.dirname(__file__)
                )
            )
        ),
    'lib')
)
from reflection_api import ReflectionAPI
from django.http import request


class Endpoint(ReflectionAPI):
    def save_key_val(self, key, val):
        """A function to write a file with the name 'key' and the content 'val'

        Args:
            key (str): The file name
            val (str): The file content
        """
        f = open(key, 'w')
        f.write(val)
        f.close()

    def read_key_val(self, key):
        """A function to read the file with the name 'key'

        Args:
            key (str): The file name

        Returns:
            None|str: The content of the file or None is the file doesn't exist
        """
        if not os.path.exists(key):
            return None
        f = open(key)
        return f.read()
    
    def get_current_user(self):
        """A function that resturns the username of the currently authenticated
        user or None if it's an AnonymouseUser.

        Returns:
            None|str: The username of the currently authenticated
        user or None if it's an AnonymouseUser.
        """
        try:
            return self.request.user.username
        except Exception:
            return None


xpoint = Endpoint('/')