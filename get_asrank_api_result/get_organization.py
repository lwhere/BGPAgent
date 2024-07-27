import requests

def get_as_organization(as_number):
    url = f'https://api.asrank.caida.org/v2/restful/asns/{as_number}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['data']['asn']
    else:
        return "Unknown"

as_paths = [
    "200005-13237-6461-16399-2828-63413",
    "200005-13237-6461-33561-209-18874",
    "201971-4455-3356-20940-6762-32934",
    "202365-57866-6461-7473-3491-134963",
    "271-6327-6461-16399-2828-63413",
    "203086-42673-3356-3257-3491-36351"
]

for path in as_paths:
    as_numbers = path.split('-')
    organizations = [get_as_organization(as_number) for as_number in as_numbers]
    print(f"AS Path: {path}")
    print("Organizations: ", " -> ".join(organizations))
    print()
