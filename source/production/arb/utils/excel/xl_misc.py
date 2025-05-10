"""
Misc Excel utility functions for parsing and sorting Excel-style cell addresses.

These utilities are typically used to extract row and column references from Excel addresses
(e.g., "$A$1", "$BB$15") and to enable sorting structures based on those references.

Examples:
    >>> get_excel_row_column("$C$4")
    ('C', 4)

    >>> xl_address_sort(("$A$2", "some value"), address_location="key", sort_by="row")
    2

    >>> xl_address_sort(("row1", {"cell": "$D$15"}), address_location="value", sort_by="column", sub_keys="cell")
    'D'
"""

import pprint

from arb.__get_logger import get_logger
from arb.utils.misc import get_nested_value

logger, pp_log = get_logger()


def get_excel_row_column(xl_address):
    """
    Extract the Excel column letters and row number from an address string.

    Excel absolute references take the form "$A$1" or "$BB$12", where both the column and row
    are prefixed with dollar signs.

    Args:
        xl_address (str): The Excel address to parse (must be in absolute format like "$A$1").

    Returns:
        tuple:
            column (str): The column letters (e.g., "A", "BB").
            row (int): The row number (e.g., 1, 12).

    Raises:
        ValueError: If the format is invalid (e.g., not exactly two dollar signs, or row not an integer).

    Examples:
        >>> get_excel_row_column("$Z$9")
        ('Z', 9)

        >>> get_excel_row_column("$AA$105")
        ('AA', 105)
    """
    if xl_address.count('$') != 2:
        raise ValueError(f"Excel address must contain exactly two '$' characters: {xl_address}")

    first_dollar = xl_address.find('$')
    last_dollar = xl_address.rfind('$')

    column = xl_address[first_dollar + 1:last_dollar]
    try:
        row = int(xl_address[last_dollar + 1:])
    except ValueError as e:
        raise ValueError(f"Could not parse row number from Excel address: {xl_address}") from e

    return column, row


def xl_address_sort(xl_tuple, address_location="key", sort_by="row", sub_keys=None):
    """
    Extract the Excel row or column value from a tuple of key-value pairs for sorting.

    This is used when sorting collections of data where either the key or the value
    contains an Excel-style address string. Supports sorting by either row or column.

    Args:
        xl_tuple (tuple): A (key, value) tuple where one element is a string like "$A$1".
        address_location (str): Which element contains the Excel address ("key" or "value").
        sort_by (str): Whether to sort by "row" (int) or "column" (str).
        sub_keys (str|list[str], optional): If the address is nested in a dict (e.g., value["cell"]),
                                            specify the key or path to retrieve it.

    Returns:
        int | str: The row (int) or column (str) component of the address, depending on `sort_by`.

    Raises:
        ValueError: If `address_location` or `sort_by` has an invalid value.

    Examples:
        >>> xl_address_sort(("$B$3", "data"), address_location="key", sort_by="row")
        3

        >>> xl_address_sort(("item", {"pos": "$C$7"}), address_location="value", sort_by="column", sub_keys="pos")
        'C'

        >>> xl_address_sort(("row", {"nested": {"cell": "$D$12"}}), address_location="value", sort_by="row", sub_keys=["nested", "cell"])
        12
    """
    if address_location == "key":
        address = xl_tuple[0]
    elif address_location == "value":
        if sub_keys is None:
            address = xl_tuple[1]
        else:
            address = get_nested_value(xl_tuple[1], sub_keys)
    else:
        raise ValueError("address_location must be 'key' or 'value'")

    column, row = get_excel_row_column(address)

    if sort_by == "row":
        return_value = row
    elif sort_by == "column":
        return_value = column
    else:
        raise ValueError("sort_by must be 'row' or 'column'")

    return return_value


def run_diagnostics() -> None:
    """
    Run demonstration tests for get_excel_row_column() and xl_address_sort().
    This function is only called if this module is run directly.

    Examples:
        >>> run_diagnostics()
    """
    pp = pprint.PrettyPrinter(indent=4, sort_dicts=False)

    print("=== Testing get_excel_row_column ===")
    valid_addresses = ["$C$42", "$AA$99"]
    for addr in valid_addresses:
        try:
            result = get_excel_row_column(addr)
            print(f"  Address: {addr} => {result}")
        except Exception as e:
            print(f"  ERROR for {addr}: {e}")

    print("\n=== Testing get_excel_row_column (invalid formats) ===")
    invalid_addresses = ["A$1", "$A1", "$A$1$", "$AB$", "$AB$XYZ"]
    for addr in invalid_addresses:
        try:
            result = get_excel_row_column(addr)
            print(f"  UNEXPECTED SUCCESS: {addr} => {result}")
        except Exception as e:
            print(f"  Expected failure for {addr}: {e}")

    print("\n=== Testing xl_address_sort ===")
    test_tuple = ("$B$10", "Example")
    print(f"  Tuple: {test_tuple} => Row: {xl_address_sort(test_tuple, 'key', 'row')}")

    nested = ("key", {"nested": {"cell": "$D$20"}})
    print(f"  Tuple: {nested} => Row: {xl_address_sort(nested, 'value', 'row', sub_keys=['nested', 'cell'])}")


if __name__ == "__main__":
    run_diagnostics()
