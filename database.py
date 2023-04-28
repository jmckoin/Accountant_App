from typing import List, Tuple
from psycopg2.extras import execute_values
from psycopg2.errorcodes import FOREIGN_KEY_VIOLATION
from psycopg2 import errors
# type hinting

CPA = Tuple[int, str]
Clients = Tuple[int, str, str, float, bool, int]
Assistants = Tuple[int, str, int]
Tax_Returns = Tuple[int, bool, float, bool, bool, int]

'''
CPAs - CPA_ID, name
Clients - Client_ID, name, address, income, material_provided_flag, CPA_ID (FK)
Assistants - Assistant_ID, name, CPA_ID (FK)
Tax_Returns - Tax_Return_ID, has_been_filed, filed_timestamp, checked_by_CPA, filed_by_CPA, Client_ID (FK)
'''

# Create tables queries

CREATE_CPAS = """CREATE TABLE IF NOT EXISTS CPAs
(CPA_ID SERIAL PRIMARY KEY, name TEXT);"""
CREATE_CLIENTS = """ CREATE TABLE IF NOT EXISTS Clients
(Client_ID SERIAL PRIMARY KEY, name TEXT, address TEXT, income MONEY, material_provided_flag BOOLEAN, 
CPA_ID INTEGER REFERENCES CPAs(CPA_ID));"""
CREATE_ASSISTANTS = """CREATE TABLE IF NOT EXISTS Assistants
(Assistant_ID SERIAL PRIMARY KEY, name TEXT, CPA_ID INTEGER REFERENCES CPAs(CPA_ID));"""
CREATE_TAX_RETURNS = """CREATE TABLE IF NOT EXISTS Tax_Returns
(Tax_Return_ID SERIAL PRIMARY KEY, has_been_filed BOOLEAN, filed_timestamp NUMERIC, checked_by_CPA BOOLEAN,
 Client_ID INTEGER REFERENCES Clients(Client_ID));"""

# selection queries

SELECT_CPA = "SELECT * FROM CPAs WHERE CPA_ID = %s;"
SELECT_ALL_CPAS = "SELECT * FROM CPAs;"
SELECT_CLIENT = "SELECT * FROM Clients WHERE Client_ID = %s;"
SELECT_TAX_RETURN_BY_CLIENT = """SELECT * FROM Tax_Returns WHERE Client_ID = %s;"""
SELECT_TAX_RETURN = """SELECT * FROM Tax_Returns WHERE Tax_Return_ID = %s;"""

# insertion queries

INSERT_CPA_RETURN_ID = "INSERT INTO CPAs (name) VALUES (%s) RETURNING CPA_ID;"
INSERT_ASSISTANT_RETURN_ID = "INSERT INTO Assistants (name, CPA_ID) VALUES (%s, %s) RETURNING Assistant_ID;"
INSERT_CLIENT_RETURN_ID = """INSERT INTO Clients (name, address, income, material_provided_flag, CPA_ID)
                        VALUES (%s, %s, %s, %s, %s) RETURNING Client_ID;"""
INSERT_TAX_RETURN_RETURNS_ID = """INSERT INTO Tax_Returns (has_been_filed, filed_timestamp, checked_by_CPA, Client_ID)
                        VALUES (%s, %s, %s, %s) RETURNING Tax_Return_ID"""

# update queries

UPDATE_MATERIALS_FLAG = """UPDATE Clients SET material_provided_flag = True WHERE Client_ID = %s;"""
UPDATE_CPA_CHECKED = """UPDATE Tax_Returns SET checked_by_CPA = True WHERE Tax_Return_ID = %s;"""
UPDATE_FILED_TIMESTAMP = """UPDATE Tax_Returns SET filed_timestamp = %s WHERE Tax_Return_ID = %s;"""

# drop tables to clear database

DROP_TABLES = "DROP TABLE CPAs, Assistants, Clients, Tax_Returns;"


def create_tables(connection):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_CPAS)
            cursor.execute(CREATE_CLIENTS)
            cursor.execute(CREATE_ASSISTANTS)
            cursor.execute(CREATE_TAX_RETURNS)


# CPA functions


def add_cpa(connection, name: str):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_CPA_RETURN_ID, (name,))
            cpa_id = cursor.fetchone()[0]
            return cpa_id


def get_cpa(connection, cpa_id: int) -> CPA:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_CPA, (cpa_id,))
            return cursor.fetchone()


def get_cpas(connection) -> List[CPA]:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_ALL_CPAS)
            return cursor.fetchall()


# Tax Assistant functions

def add_assistant(connection, name: str, cpa_id: int):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_ASSISTANT_RETURN_ID, (name, cpa_id))
            assistant_id = cursor.fetchone()[0]
            return assistant_id


# Client functions

def add_client(connection, name: str, address: str, income: float, material_provided_flag: bool, cpa_id: int):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_CLIENT_RETURN_ID, (name, address, income, material_provided_flag, cpa_id))
            client_id = cursor.fetchone()[0]
            return client_id


def get_client(connection, client_id: int) -> Clients:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_CLIENT, (client_id,))
            return cursor.fetchone()


def mark_materials_complete(connection, client_id: int):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(UPDATE_MATERIALS_FLAG, (client_id,))


# Tax Return functions

def create_tax_return(connection, has_been_filed: bool, filed_timestamp: float, checked_by_cpa: bool,
                      client_id: int):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(INSERT_TAX_RETURN_RETURNS_ID, (has_been_filed, filed_timestamp, checked_by_cpa,
                                                          client_id))
            new_tax_return_id = cursor.fetchone()[0]
            return new_tax_return_id


def get_tax_return_by_client(connection, client_id: int) -> Tax_Returns:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_TAX_RETURN_BY_CLIENT, (client_id,))
            return cursor.fetchone()


def get_tax_return(connection, tax_return_id: int) -> Tax_Returns:
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(SELECT_TAX_RETURN, (tax_return_id,))
            return cursor.fetchone()


def mark_cpa_checked(connection, tax_return_id: int):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(UPDATE_CPA_CHECKED, (tax_return_id,))


def change_filed_timestamp(connection, filed_timestamp: float, tax_return_id: int):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(UPDATE_FILED_TIMESTAMP, (filed_timestamp, tax_return_id))
