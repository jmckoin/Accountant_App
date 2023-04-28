import database
from connections import create_connection
import datetime
import pytz as pytz
from psycopg2.errorcodes import FOREIGN_KEY_VIOLATION
from psycopg2 import errors


class TaxReturn:
    def __init__(self, has_been_filed: bool, filed_timestamp: float, checked_by_cpa: bool, client_id: int,
                 _id: int = None):
        self.id = _id
        self.has_been_filed = has_been_filed
        self.filed_timestamp = filed_timestamp
        self.checked_by_cpa = checked_by_cpa
        self.client_id = client_id

    def __repr__(self):
        return f"Tax Return ID: ({self.id!r}), filed status: ({self.has_been_filed!r}), " \
               f"has been checked by CPA ({self.checked_by_cpa!r})," \
               f"\nbelonging to client ID: ({self.client_id!r})"

    def save(self):
        # try creating tax return object returns 1 if successful and None if fails
        try:
            connection = create_connection()
            current_datetime_utc = datetime.datetime.now(tz=pytz.utc)
            current_timestamp = current_datetime_utc.timestamp()
            new_tax_return_id = database.create_tax_return(connection, self.has_been_filed, current_timestamp,
                                                           self.checked_by_cpa, self.client_id)
            self.id = new_tax_return_id
            return 1
        except errors.lookup(FOREIGN_KEY_VIOLATION):
            return None

    @classmethod
    def get(cls, tax_return_id: int) -> "TaxReturn":
        # get tax return by id
        connection = create_connection()
        tax_return = database.get_tax_return(connection, tax_return_id)
        connection.close()
        return cls(tax_return[1], tax_return[2], tax_return[3], tax_return[4], tax_return[0])

    def mark(self):
        connection = create_connection()
        database.mark_cpa_checked(connection, self.id)
        connection.close()

    @classmethod
    def get_by_client(cls, client_id: int) -> "TaxReturn":
        # get by FK client id
        connection = create_connection()
        tax_return = database.get_tax_return_by_client(connection, client_id)
        connection.close()
        return cls(tax_return[1], tax_return[2], tax_return[3], tax_return[4], tax_return[0])
