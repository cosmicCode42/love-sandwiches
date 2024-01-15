import gspread
from google.oauth2.service_account import Credentials
from pprint import pprint

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('love_sandwiches')


def get_sales_data():
    """
    Get sales figures input from the user.
    Run a while loop to collect a valid string of data from the user
    via the terminal, which must be a string of 6 numbers separated
    by commas. The loop will repeatedly request data, until it is valid.
    """
    while True:
        print("Please enter sales data from the last market.")
        print("Sales should be six numbers, separated by commas.")
        print("Example: 10,20,30,40,50,60\n")

        data_str = input("Enter your data here: ")

        sales_data = data_str.split(",")

        if validate_data(sales_data):
            print("Data is valid!")
            break

    return [int(data) for data in sales_data]


def validate_data(values):
    """
    Inside the try, converts all string values into integers.
    Raises ValueError if strings cannot be converted into int,
    or if there are not exactly 6 values.
    """
    try:
        [int(value) for value in values]
        if len(values) != 6:
            raise ValueError(
                f'Exactly 6 values required. You provided {len(values)}'
            )
    except ValueError as e:
        print(f'Invalid data: {e}, please try again.')
        return False

    return True


def update_worksheet(data, sheet_name):
    """
    Update worksheets, add new row with list data provided
    """
    print(f"Updating {sheet_name} worksheet...\n")
    worksheet = SHEET.worksheet(sheet_name)
    worksheet.append_row(data)
    print(f"{sheet_name.capitalize()} worksheet updated successfully.\n")


def calculate_surplus_data(sales_row):
    """
    Compare sales with stock and calculate the surplus for each item type.

    The surplus is defined as the sales figure subtracted from the stock:
    - Positive surplus indicates waste
    - Negative surplus indicates extra made when stock was sold out.
    """
    print("Calculating surplus data...\n")
    stock = SHEET.worksheet("stock").get_all_values()
    stock_row = [int(data) for data in stock[-1]]

    surplus_data = [stock - sales for stock,
                    sales in zip(stock_row, sales_row)]

    return surplus_data


def get_last_5_entries_sales():
    """
    Collects columns of data from sales worksheet, collecting
    the last 5 entries for each sandwich and returns the data
    as a list of lists.
    """
    sales = SHEET.worksheet("sales")
    column_list = [sales.col_values(i)[-5:] for i in range(1, 7)]

    return column_list


def calculate_stock_data(data):
    """
    Calculate the average stock for each item type, adding 10%.

    Iterates through each list in the list of lists, converting
    them to number lists. Finds the average using sum() / 5,
    then increases by a factor of 1.1 and rounds the result.
    Puts each result in a new list and returns the list.
    """
    print("Calculating stock data...\n")
    projected_stock_row_list = [round((sum([int(num) for 
                                num in list]) / 5) * 1.1) for list in data]
    return projected_stock_row_list


def get_stock_values(data):
    headings = [SHEET.worksheet("stock").col_values(i)[0] for i in range (1, 7)]
    stock_values = data
    stock_dict = {heading:stock for heading, stock in zip(headings, stock_values)}
    print(f"Make the following numbers of sandwiches for next market:\n\n{stock_dict}")


def main():
    """
    Run all program functions
    """
    sales_data = get_sales_data()
    update_worksheet(sales_data, "sales")
    new_surplus_data = calculate_surplus_data(sales_data)
    update_worksheet(new_surplus_data, "surplus")
    projected_stock_data = calculate_stock_data(get_last_5_entries_sales())
    update_worksheet(projected_stock_data, "stock")
    get_stock_values(projected_stock_data)


print("Welcome to Love Sandwiches data automation!\n")
main()
