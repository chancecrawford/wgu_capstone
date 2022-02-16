
# converts numbers to more readable format
def round_number_millions(number):
    return round(number / 1000000, 2)


# converts numbers to more readable format
def round_number_billions(number):
    return round(number / 1000000000, 2)


# converts number to more readable format and outputs as string
def round_number_as_string(number):
    if number > 1000000000:
        return str(round(number / 1000000000, 2)) + ' Billion'
    else:
        return str(round(number / 1000000, 2)) + ' Million'
