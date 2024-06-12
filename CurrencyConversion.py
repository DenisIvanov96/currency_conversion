import argparse
import json
import sys
import requests

cached_base_currency = {}


def date_input(date_arg=None):
    date_format = date_arg
    date_format_split = date_format.split("-")

    if len(date_format_split) == 3 and len(date_format_split[0]) == 4 and 0 < int(
            date_format_split[1]) < 13 and 0 < int(date_format_split[2]) < 32:
        return date_format
    else:

        return date_input()


with open('config.json') as config_file:
    config_data = json.load(config_file)
    API_KEY = config_data['api_key']


def get_available_currencies():
    url = f"https://api.fastforex.io/currencies?api_key={API_KEY}"

    headers = {"accept": "application/json"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        currencies = data['currencies']
        return currencies
    else:
        print("Error:", response.text)
        return None


available_currencies = get_available_currencies()


def enter_amount():
    amount = input()

    if amount.upper() == 'END':
        sys.exit()

    if amount.isnumeric():
        entered_amount = float(amount)
        formatted_amount = f"{entered_amount:.2f}"
        return float(formatted_amount)
    else:
        print('Please enter a valid amount')
        return enter_amount()


def currency_code():
    entered_currency_code = input().upper()

    if entered_currency_code == 'END':
        sys.exit()

    if entered_currency_code in available_currencies:
        return entered_currency_code
    else:
        print('Please enter a valid currency code')
        return currency_code()


def convert_currency(base_currency, to_currency, amount):
    if [curr for curr in cached_base_currency if curr == base_currency]:
        target_currency = float(cached_base_currency[base_currency][to_currency])
        result = amount * target_currency
        return result
    else:
        url = f'https://api.fastforex.io/fetch-all?from={base_currency}&api_key={API_KEY}'
        headers = {"accept": "application/json"}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            results = data['results']
            cached_base_currency[base_currency] = results
            target_currency = float(cached_base_currency[base_currency][to_currency])
            result = amount * target_currency
            return result

        else:
            print("Error:", response.text)
            return None


def append_to_json(filename, data):
    with open(filename, 'r+') as file:
        try:
            file_data = json.load(file)
        except json.JSONDecodeError:
            file_data = []
        file_data.append(data)
        file.seek(0)
        json.dump(file_data, file)


def main():
    parser = argparse.ArgumentParser(description="Currency Conversion Script")
    parser.add_argument('date', nargs='?', type=str, help="The date in 'YYYY-MM-DD' format")
    args = parser.parse_args()

    date = date_input(args.date)
    while True:
        amount = enter_amount()
        base_currency = currency_code()
        target_currency = currency_code()
        converted_amount = convert_currency(base_currency, target_currency, amount)
        bold_start = "\033[1m"
        bold_end = "\033[0m"

        if converted_amount is not None:
            conversion_data = {
                "date": date,
                "amount": amount,
                "base_currency": base_currency,
                "target_currency": target_currency,
                "converted_amount": converted_amount,
            }
            append_to_json('conversions.json', conversion_data)

            print(
                f"{bold_start}{amount} {base_currency} is {converted_amount:.2f} {target_currency}{bold_end}")


if __name__ == "__main__":
    main()
