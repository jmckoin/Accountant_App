import database
from connections import create_connection
from psycopg2.errorcodes import FOREIGN_KEY_VIOLATION
from psycopg2 import errors


class Assistant:
    def __init__(self, name: str, cpa_id: int, _id: int = None):
        self.id = _id
        self.name = name
        self.cpa_id = cpa_id

    def __repr__(self):
        return f"Assistant with name: ({self.name!r}) and ID: ({self.id!r}) " \
               f"added to CPA with CPA ID: ({self.cpa_id!r}))"

    def save(self):
        try:
            connection = create_connection()
            new_assistant_id = database.add_assistant(connection, self.name, self.cpa_id)
            connection.close()
            self.id = new_assistant_id
            return 1
        except errors.lookup(FOREIGN_KEY_VIOLATION):
            return None

