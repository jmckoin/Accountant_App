import database
from connections import create_connection
from psycopg2.errorcodes import FOREIGN_KEY_VIOLATION
from psycopg2 import errors


class Client:
    def __init__(self, name: str, address: str, income: float, material_provided_flag: bool, cpa_id: int,
                 _id: int = None):
        self.id = _id
        self.name = name
        self.address = address
        self.income = income
        self.material_provided_flag = material_provided_flag
        self.cpa_id = cpa_id

    def __repr__(self):
        return f"Client ID: ({self.id!r}), name: ({self.name!r}), address: ({self.address!r})," \
               f" income: ({self.income!r}),\ntax material provided: ({self.material_provided_flag!r}), " \
               f"Assigned CPA: ({self.cpa_id!r})"

    def save(self):
        try:
            connection = create_connection()
            new_client_id = database.add_client(connection, self.name, self.address, self.income,
                                                self.material_provided_flag, self.cpa_id)
            connection.close()
            self.id = new_client_id
            return 1
        except errors.lookup(FOREIGN_KEY_VIOLATION):
            return None

    @classmethod
    def get(cls, client_id: int) -> "Client":
        # get client by id
        connection = create_connection()
        client = database.get_client(connection, client_id)
        connection.close()
        return cls(client[1], client[2], client[3], client[4], client[5], client[0])

    def mark(self):
        connection = create_connection()
        database.mark_materials_complete(connection, self.id)
        connection.close()

