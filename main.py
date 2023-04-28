'''
Main to do things
'''
from datetime import datetime, timezone
import datetime

from connections import create_connection
import database
from CPAs import CPA
from Assistants import Assistant
from Clients import Client
from Tax_Returns import TaxReturn

DATABASE_PROMPT = "Enter the DATABASE_URL value or leave empty to load from .env file: "
MENU_PROMPT = """ -- Menu -- 

1) Add CPA
2) Add tax assistant
3) Add a client
4) Mark client required materials completed
5) Check client required materials status
6) Mark that a tax return has been filed
7) Check if a tax returned has been filed for client
8) Mark that a CPA checked a return
9) Check return for CPA verified status
10) Exit

Enter your choice: """


# Creating an instance of Employee object, and using the methods inside.


# prompt user to add CPA to database
def prompt_create_cpa():
    cpa_name = input("What is the CPA's name?: ")
    cpa = CPA(cpa_name)
    cpa.save()
    print(f"{cpa} added")


# prompt user to add assistant to database with value error catching
def prompt_create_assistant():
    try:
        cpa_id = int(input("What is the ID of the CPA they assist?: "))
        assistant_name = input("What is the tax filing assistant's name?: ")
        assistant = Assistant(assistant_name, cpa_id)
        result = assistant.save()
        if result is None:
            print("CPA ID does not exist in the database")
            user_input = input("Would you like to see the list of available CPAs? (y/n)\n")
            if user_input == 'n':
                pass
            elif user_input == 'y':
                list_avail_cpas()
            else:
                print("Invalid Entry.")
        else:
            print(f"{assistant}")
    except ValueError as err:
        print(err)


# list out all the CPAs in database
def list_avail_cpas():
    for cpa in CPA.all():
        print(f"CPA ID: {cpa.id}, Name: {cpa.name}")


# Prompt user to add clients to database
def prompt_create_client():
    try:
        client_name = input("What is the client's name?: ")
        client_address = input("What is the client's address?: ")
        client_income = float(input("What is the client's income?: "))
        material_provided_flag = set_material_flag()
        cpa_id = int(input("What is the CPA ID of the CPA assigned to this client?:"))
        client = Client(client_name, client_address, client_income, material_provided_flag, cpa_id)
        result = client.save()

        # give user option of view CPAs in database
        if result is None:
            print("CPA ID does not exist in the database")
            user_input = input("Would you like to see the list of available CPAs? (y/n)\n")
            if user_input == 'n':
                pass
            elif user_input == 'y':
                list_avail_cpas()
            else:
                print("Invalid Entry.")
        else:
            print(f"{client}")
    except ValueError as err:
        print(err)


# handle setting the tax material provided flag
def set_material_flag():
    error_flag = True
    while error_flag:
        user_input = input("Has client provided tax materials? (y/n): ")
        if user_input == 'y':
            return True
        elif user_input == 'n':
            return False
        else:
            print("Invalid input. 'y' or 'n' has to be entered to continue.")


def prompt_mark_client_materials():
    try:
        client_id = int(input("Enter client ID you would like to mark required materials complete: "))
        Client.get(client_id).mark()
        client = Client.get(client_id)
        print(f"{client}\nWas updated.")

    except (ValueError, TypeError) as err:
        print(err)


def prompt_check_client_materials():
    try:
        client_id = int(input("Enter client ID of client that you would like to check required materials status: "))
        client = Client.get(client_id)
        # check client material flag to determine status
        if not client.material_provided_flag:
            print(f"Client ({client.name}) with Client ID: ({client.id}) has not provided tax materials to the firm.")
        elif client.material_provided_flag:
            print(f"Client ({client.name}) with Client ID: ({client.id}) has provided tax materials to the firm.")
    except (ValueError, TypeError) as err:
        print(err)


def prompt_file_tax_return():
    try:
        client_id = int(input("What is the client's ID for the tax return that has been filed?: "))
        # check to see if tax return for client already exist in database
        try:
            check_for_tax_return = TaxReturn.get_by_client(client_id)
            print(f"Client with ID: ({check_for_tax_return.client_id}) already has a tax return on file"
                  f" with tax return ID: ({check_for_tax_return.id})")
        # TypeError means tax return for client id doesn't exist limiting one tax return per client.
        except TypeError:
            has_been_filed = True
            # data handling

            filed_timestamp = datetime.datetime.now(timezone.utc)
            # call function to deal with cpa or assistant
            checked_by_cpa = determine_cpa_or_assistant()
            tax_return = TaxReturn(has_been_filed, filed_timestamp, checked_by_cpa, client_id)
            result = tax_return.save()
            filed_datetime = tax_return.filed_timestamp.strftime("%Y-%m-%d")
            # inform user client does not exist in db if so
            if result is None:
                print("Client ID does not exist in the database")
            else:
                print(f"{tax_return}\nHas been filed on {filed_datetime}.")
    # catch value error if wrong input is entered
    except ValueError as err:
        print(err)


def determine_cpa_or_assistant():
    error_flag = True
    while error_flag:
        user_input = input("Are you a CPA? (y/n): ")
        if user_input == 'y':
            return True
        elif user_input == 'n':
            return False
        else:
            print("Invalid entry. 'y' or 'n' has to be entered to continue.")


def prompt_check_client_return():
    try:
        client_id = int(input("Enter client ID to check for tax return: "))
        tax_return = TaxReturn.get_by_client(client_id)
        print(f"id: {tax_return.id}, been filed: {tax_return.has_been_filed}, timestamp; {tax_return.filed_timestamp}"
              f"checked by CPA: {tax_return.checked_by_cpa}, client id: {tax_return.client_id}")
    except ValueError as err:
        print(err)
    except TypeError:
        print(f'No tax return has been filed for client with client ID: ({client_id})')
        # check to see if there is a client with the client input by the user
        try:
            client = Client.get(client_id)
            print(f"Client with name: ({client.name}) and ID: ({client.id}) has not filed a tax return.")
        except TypeError:
            print(f"Client with ID: ({client_id}) does not exist in database.")


def prompt_mark_cpa_checked():
    try:
        tax_return_id = int(input("Enter the Tax Return ID you would like marked that a CPA checked: "))
        TaxReturn.get(tax_return_id).mark()
        tax_return = TaxReturn.get(tax_return_id)
        print(f"Tax Return ID: ({tax_return.id}) has a checked by CPA status of ({tax_return.checked_by_cpa})\n"
              f"{tax_return}\nWas updated.")
    except (ValueError, TypeError) as err:
        print(err)


def prompt_check_cpa_checked():
    try:
        tax_return_id = int(input("Enter tax return ID for CPA checked status: "))
        tax_return = TaxReturn.get(tax_return_id)
        # check to see if cpa has checked tax return
        if not tax_return.checked_by_cpa:
            print(f"Tax return with ID: ({tax_return.id}) has not been checked by a CPA.")
        elif tax_return.checked_by_cpa:
            print(f"Tax return with ID: ({tax_return.id}) has been checked by a CPA.")
    except ValueError as err:
        print(err)
    except TypeError as te:
        print(f'No tax return with the ID: ({tax_return_id}) has been filed.')


# Dictionary mapped to functions


MENU_OPTIONS = {
    "1": prompt_create_cpa,
    "2": prompt_create_assistant,
    "3": prompt_create_client,
    "4": prompt_mark_client_materials,
    "5": prompt_check_client_materials,
    "6": prompt_file_tax_return,
    "7": prompt_check_client_return,
    "8": prompt_mark_cpa_checked,
    "9": prompt_check_cpa_checked
}


def menu():
    connection = create_connection()
    database.create_tables(connection)

    while (selection := input(MENU_PROMPT)) != '10':
        try:
            MENU_OPTIONS[selection]()
        except KeyError:
            print("Invalid input selected. Please try again.")


if __name__ == '__main__':
    menu()
