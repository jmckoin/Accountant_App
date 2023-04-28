import database
from connections import create_connection
from typing import List


class CPA:
    def __init__(self, name: str, _id: int = None):
        self.id = _id
        self.name = name

    def __repr__(self):
        return f"CPA with name: ({self.name!r}) and ID: ({self.id!r})"

    def save(self):
        connection = create_connection()
        new_cpa_id = database.add_cpa(connection, self.name)
        connection.close()
        self.id = new_cpa_id

    @classmethod
    def get(cls, cpa_id: int) -> "CPA":
        connection = create_connection()
        cpa = database.get_cpa(connection, cpa_id)
        connection.close()
        return cls(cpa[1], cpa[0])

    @classmethod
    def all(cls) -> List["CPA"]:
        # Get all CPAs
        connection = create_connection()
        cpas = database.get_cpas(connection)
        connection.close()
        return [cls(cpa[1], cpa[0]) for cpa in cpas]
