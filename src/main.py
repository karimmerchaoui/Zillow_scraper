import requests
from bs4 import BeautifulSoup
import time
from requests.exceptions import ConnectTimeout, ConnectionError,ReadTimeout
from urllib3.exceptions import ProtocolError
import pandas as pd
import datetime
import customtkinter as ctk
from tkinter import filedialog
import threading
import json
import tkinter as tk
from tkinter import ttk
import os
from concurrent.futures import ThreadPoolExecutor,as_completed
from foratting import format_hist,format_house_details,chunk_leads,generate_zillow_link


request_counter = 0


def update_request_count_label():
    root.after(0, lambda: request_count_label.configure(text=f"API Requests: {request_counter}"))


def disable_all_buttons():
    input_browse_button.configure(state='disabled')  # Disable input button
    output_browse_button.configure(state='disabled')  # Disable output button
    process_button.configure(state='disabled')  # Disable process button
    lead_checkbox.configure(state='disabled')
    zillow_checkbox.configure(state='disabled')
    zestimate_checkbox.configure(state='disabled')
    price_history_checkbox.configure(state='disabled')
    seller_checkbox.configure(state='disabled')
    house_features_checkbox.configure(state='disabled')
    status_checkbox.configure(state='disabled')
    auction_link_checkbox.configure(state='disabled')


def enable_all_buttons():
    input_browse_button.configure(state='enable')  # Disable input button
    output_browse_button.configure(state='enable')  # Disable output button
    process_button.configure(state='enable')  # Disable process button
    lead_checkbox.configure(state='normal')
    zillow_checkbox.configure(state='normal')
    zestimate_checkbox.configure(state='normal')
    price_history_checkbox.configure(state='normal')
    seller_checkbox.configure(state='normal')
    house_features_checkbox.configure(state='normal')
    status_checkbox.configure(state='normal')
    auction_link_checkbox.configure(state='normal')

def read_leads_from_excel():
    # Read the Excel file into a DataFrame
    df = pd.read_excel(input_path.get(), header=None)

    # Drop NaN values and remove duplicates
    leads = list(set(df.iloc[:, 0].dropna()))

    return leads

def extract_info(zillow_link):
    def load_and_parse():
        payload = {'api_key': 'API_KEY', 'url': zillow_link, 'ultra_premium': "true"}
        code = 500
        while code == 500:
            try:
                global request_counter
                r = requests.get('https://api.scraperapi.com/', params=payload)
                request_counter += 1
                update_request_count_label()
                code = r.status_code
                time.sleep(1)
                if code == 500:
                    log_message("Connection issue (500). Retrying...")
            except (ConnectTimeout, ConnectionError, ProtocolError, ReadTimeout):
                log_message("Connection issue. Retrying...")
                time.sleep(1)
        return r.text

    def parse_data(soup):
        script_tag = soup.find('script', id="__NEXT_DATA__")
        json_obj = json.loads(script_tag.text)
        d = json_obj['props']['pageProps']['componentProps']['gdpClientCache']
        json_obj2 = json.loads(d)
        first_key = next(iter(json_obj2))
        return json_obj2, first_key

    def get_ev(soup):
        # Try multiple status class names in order
        status_classes = [
            'Text-c11n-8-99-3__sc-aiai24-0 sc-ZqGJI dFxMdJ cRfcfD',
            'StyledGalleryStatusPillContainer-fshdp-8-111-1__sc-1o1xnlr-0 dsIuEJ',
            'Text-c11n-8-99-3__sc-aiai24-0 sc-gUJyNl dFxMdJ eRIbOD',
            'Text-c11n-8-111-1__sc-aiai24-0 sc-ikHGee hZAvJt ckhRfp',
        ]
        status = next((soup.find(class_=cls) for cls in status_classes if soup.find(class_=cls)), None)

        # Try multiple Zestimate class names
        price_elements = [
            soup.find('span', attrs={'data-testid': 'price'}),
            soup.find(class_='Text-c11n-8-99-3__sc-aiai24-0 sc-hbWBzy iDpxGV dtpECA')
        ]
        ev_element = next((el for el in price_elements if el), None)

        if not (ev_element and status):
            return None

        ev = ev_element.text
        status_text = status.text

        if status_text == "Est.":
            alt = soup.find('div', class_='StyledGalleryStatusContainer-fshdp-8-106-0__sc-1ix1xn8-0 kxXvIE')
            if alt:
                status_text = alt.text

        return ev.replace("Est. ", ""), status_text

    def get_seller(soup):
        seller = soup.find('div', "SellerAttributionStyles__StyledListedBy-fshdp-8-106-0__sc-5b3vve-0 dPomoX")
        return seller.text.replace("Listed by:", "") if seller else "Not Found"

    def get_hist(json_obj2, first_key):
        try:
            hist = json_obj2[first_key]['property']['priceHistory']
            return format_hist(hist) if hist else "Not Found"
        except Exception:
            return None  # Trigger retry

    def get_house_details(json_obj2, first_key):
        details = json_obj2[first_key]['property']['resoFacts']
        return format_house_details(details)

    def get_auction_link(json_obj2, first_key):
        return json_obj2[first_key]['property'].get('postingUrl', None)

    # --- Initial load
    html = load_and_parse()
    soup = BeautifulSoup(html, 'html.parser')
    try:
        json_obj2, first_key = parse_data(soup)
        ev_st = get_ev(soup)
        if not ev_st:
            return None
        seller = get_seller(soup)
        price_history = get_hist(json_obj2, first_key)

        # --- If priceHistory failed, reload once
        if price_history is None:
            html = load_and_parse()
            soup = BeautifulSoup(html, 'html.parser')
            json_obj2, first_key = parse_data(soup)
            price_history = get_hist(json_obj2, first_key)
            if price_history is None:
                price_history = "ERROR"

        house_details = get_house_details(json_obj2, first_key)
        auction_link = get_auction_link(json_obj2, first_key)

        return ev_st[0], ev_st[1], seller, price_history, house_details, auction_link
    except Exception as e:
        log_message(f"Fatal error on {zillow_link}: {e}")
        return None



def clear_log():
    log_textbox.configure(state='normal')  # Make the textbox editable
    log_textbox.delete('1.0', 'end')  # Clear content
    log_textbox.configure(state='disabled')  # Make the textbox read-only again


def browse_input_path():
    input_path.set(filedialog.askopenfilename(title="Select Input File", filetypes=[("Text Files", "*.xlsx")]))


def browse_output_path():
    output_path.set(filedialog.askdirectory(title="Select Output Directory"))


def log_message(message):
    # Use after() to ensure that the log is updated on the main thread
    root.after(0, append_log, "")
    root.after(0, append_log, message)


def append_log(message):
    # Update the log Textbox safely in the main thread
    log_textbox.configure(state='normal')  # Allow editing the textbox temporarily
    log_textbox.insert(ctk.END, f"{message}\n")
    log_textbox.yview(ctk.END)  # Auto-scroll to the latest log message
    log_textbox.configure(state='disabled')  # Make the textbox read-only again


def process_files():
    if not input_path.get() or not output_path.get():
        log_message("Error: Input file or Output directory not set.")
        return

    # Run the actual processing in a separate thread
    threading.Thread(target=process_in_background, daemon=True).start()


def process_single_lead(lead):
    """Processes a single lead."""
    try:
        log_message(f"Processing: {lead}")
        zillow_link = generate_zillow_link(lead)
        extracted_info=extract_info(zillow_link)
        if extracted_info:
            ev, status, seller, price_history, house_details,auction_link=extracted_info
        else:
            return {"Lead": lead, "Status": "Property Not Found"}

        # Dictionary storing only selected attributes
        result = {"Lead": lead}  # "Lead" is always included

        if status_var.get():
            result["Status"] = status

        if zillow_var.get():
            result["Zillow Link"] = zillow_link

        if zestimate_var.get():
            result["Zestimate"] = ev

        if seller_var.get():
            result["Seller"] = seller

        if price_history_var.get():
            result["Price History"] = price_history

        if auction_link_var.get():
            result["Auction Link"] = auction_link

        if house_features_var.get():
            # Add individual house features to the result dictionary
            result.update(house_details)

        return result

    except AttributeError:
        return {"Lead": lead, "Status": "Property Not Found"}

    except Exception as e:
        log_message(f"Error processing lead {lead}: {e}")
        return {"Lead": lead, "Status": "ERROR"}
def process_lead_batch(leads_batch):
    """Processes a batch of 5 leads in parallel."""
    results = []
    with ThreadPoolExecutor(max_workers=5) as batch_executor:  # Process 5 leads in parallel
        future_to_lead = {batch_executor.submit(process_single_lead, lead): lead for lead in leads_batch}

        for future in as_completed(future_to_lead):
            result = future.result()
            if result:
                results.append(result)

    return results  # Return all results from the batch



def process_in_background():
    clear_log()
    disable_all_buttons()
    progress_var.set(0)

    leads = read_leads_from_excel()
    ln = len(leads)
    progress_label.configure(text=f"0/{ln}")

    lead_batches = chunk_leads(leads, batch_size=5)  # Split into batches of 5
    total_batches = len(lead_batches)

    results = []
    processed_count = 0

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(output_path.get(), f"{timestamp}-output.xlsx")

    with ThreadPoolExecutor(max_workers=9) as executor:  # 9 threads handling batches
        future_to_batch = {executor.submit(process_lead_batch, batch): batch for batch in lead_batches}

        for future in as_completed(future_to_batch):
            batch_results = future.result()
            results.extend(batch_results)
            processed_count += len(batch_results)

            # Update progress
            progress_var.set((processed_count / ln) * 100)
            progress_label.configure(text=f"{processed_count}/{ln}")

            # Save intermediate results to avoid data loss
            df_result = pd.DataFrame(results)
            with pd.ExcelWriter(output_file, mode="w", engine="openpyxl") as writer:
                df_result.to_excel(writer, index=False)

    progress_var.set(100)
    progress_label.configure(text=f"{ln}/{ln}")
    log_message("Scraping Finished.")
    log_message(f"Results saved to: {output_file}")

    enable_all_buttons()

# Initialize the customtkinter window
ctk.set_appearance_mode("Dark")  # Choose 'Dark' or 'Light' mode for customtkinter
ctk.set_default_color_theme("blue")  # Set default color theme

root = ctk.CTk()
root.title("Zillow Extractor")
root.geometry("620x720")

# Define StringVars for input and output paths
input_path = ctk.StringVar()
output_path = ctk.StringVar()

# Create GUI components for input path
input_label = ctk.CTkLabel(root, text="Input File Path:")
input_label.pack(pady=10)
input_entry = ctk.CTkEntry(root, textvariable=input_path, width=300)
input_entry.pack(pady=5)
input_browse_button = ctk.CTkButton(root, text="Browse Input", command=lambda: browse_input_path())
input_browse_button.pack(pady=5)

# Create GUI components for output directory
output_label = ctk.CTkLabel(root, text="Output Directory:")
output_label.pack(pady=10)
output_entry = ctk.CTkEntry(root, textvariable=output_path, width=300)
output_entry.pack(pady=5)
output_browse_button = ctk.CTkButton(root, text="Browse Output", command=lambda: browse_output_path())
output_browse_button.pack(pady=5)

# Define BooleanVars for checkboxes
lead_var = ctk.BooleanVar(value=True)  # True by default, selected
zillow_var = ctk.BooleanVar(value=True)  # True by default, selected
zestimate_var = ctk.BooleanVar(value=True)  # True by default, selected
seller_var = ctk.BooleanVar(value=True)
price_history_var = ctk.BooleanVar(value=True)
house_features_var = ctk.BooleanVar(value=True)  # True by default
auction_link_var = ctk.BooleanVar(value=True)  # True by default

# Create a frame for the checkboxes
checkbox_frame = ctk.CTkFrame(root)

# Create two separate frames for each row of checkboxes
row1_frame = ctk.CTkFrame(checkbox_frame)
row2_frame = ctk.CTkFrame(checkbox_frame)

status_var = ctk.BooleanVar(value=True)  # Default to True (selected)

# Create and pack the first three checkboxes in the first row
lead_checkbox = ctk.CTkCheckBox(row1_frame, text="Lead", variable=lead_var, border_width=0, corner_radius=0)
lead_checkbox.pack(side="left", padx=10)

status_checkbox = ctk.CTkCheckBox(row1_frame, text="Status", variable=status_var, border_width=0, corner_radius=0)
status_checkbox.pack(side="left", padx=10)


zillow_checkbox = ctk.CTkCheckBox(row1_frame, text="Zillow Link", variable=zillow_var, border_width=0, corner_radius=0)
zillow_checkbox.pack(side="left", padx=10)

zestimate_checkbox = ctk.CTkCheckBox(row1_frame, text="Zestimate", variable=zestimate_var, border_width=0, corner_radius=0)
zestimate_checkbox.pack(side="left", padx=10)

# Create and pack the next three checkboxes in the second row
seller_checkbox = ctk.CTkCheckBox(row2_frame, text="Seller", variable=seller_var, border_width=0, corner_radius=0)
seller_checkbox.pack(side="left", padx=10)

price_history_checkbox = ctk.CTkCheckBox(row2_frame, text="Price History", variable=price_history_var, border_width=0, corner_radius=0)
price_history_checkbox.pack(side="left", padx=10)

auction_link_checkbox = ctk.CTkCheckBox(row2_frame, text="Auction link", variable=auction_link_var, border_width=0, corner_radius=0)
auction_link_checkbox.pack(side="left", padx=10)

house_features_checkbox = ctk.CTkCheckBox(
    row2_frame, text="House Features", variable=house_features_var, border_width=0, corner_radius=0
)
house_features_checkbox.pack(side="left", padx=10)

# Pack the rows into the main checkbox frame
row1_frame.pack(pady=(10, 0))  # Add some padding on top of the first row
row2_frame.pack(pady=(15, 0))   # Add some padding on top and bottom of the second row

# Pack the main checkbox frame into the root window
checkbox_frame.pack(pady=10)

# Progress bar and button setup (as in your original code)
progress_var = tk.DoubleVar()
progress_label = tk.Label(root, text="", fg="white", bg=root.cget("bg"), bd=0)  # Set bg to match root bg and remove border
progress_label.pack(pady=20)

request_count_label = ctk.CTkLabel(root, text="API Requests: 0")
request_count_label.pack(pady=5)

style = ttk.Style()
style.theme_use('alt')
style.configure("blue.Horizontal.TProgressbar", thickness=20,
                troughcolor="gray", background="#0078d4")  # System blue color


progress_bar = ttk.Progressbar(root, variable=progress_var, style='TProgressbar', maximum=100, length=450)
progress_bar.pack(pady=0)

process_button = ctk.CTkButton(root, text="Process Files", command=lambda: process_files())
process_button.pack(pady=20)

# Log textbox setup (as in your original code)
log_textbox = ctk.CTkTextbox(root, height=300, width=510)
log_textbox.pack(pady=(5))
log_textbox.configure(state='disabled')  # Make the textbox read-only

# Start the application loop
root.mainloop()

