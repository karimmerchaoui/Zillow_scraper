import re


def format_hist(info_list):
    result_str = ""  # Initialize an empty string to accumulate the result

    # Iterate over each entry in the list
    entry = info_list[0]
    if entry['price']:
        for key, value in entry.items():
            if key=="price":
                value=str(value)[:3] + ',' + str(value)[3:]
            if key =="attributeSource" or key=="time" or key=="showCountyLink" or key=="postingIsRental":
                continue
            if isinstance(value, dict):  # Check if the value is a nested dictionary
                result_str += f"{key}:\n"
                # If it's a dictionary, iterate over it
                for sub_key, sub_value in value.items():
                    result_str += f"  {sub_key}: {sub_value}\n"
            else:
                result_str += f"{key}: {value}\n"

    return result_str


def format_house_details(info_dict):
    # List of features to extract
    features = ["bathrooms", "bathroomsFloat", "bedrooms", "lotSize", "pricePerSquareFoot", "yearBuilt", "livingArea"]

    # Initialize a dictionary to store the features
    house_features = {feature: info_dict.get(feature, "Not Found") for feature in features}

    return house_features


def chunk_leads(leads, batch_size=5):
    """Splits the list of leads into smaller batches of 5."""
    return [leads[i:i + batch_size] for i in range(0, len(leads), batch_size)]


def generate_zillow_link(address):
    """Formats an address into a Zillow property search link."""
    if not address or not isinstance(address, str):
        return None  # Handle empty or invalid input

    formatted_address = address.strip()
    formatted_address = re.sub(r'\s+', '-', formatted_address)  # Replace spaces with hyphens
    formatted_address = re.sub(r'[^\w,\-]', '', formatted_address)  # Remove unwanted special characters
    formatted_address = re.sub(r'^-+|-+$', '', formatted_address)  # Remove leading/trailing hyphens

    return f"https://www.zillow.com/homes/{formatted_address}_rb/"