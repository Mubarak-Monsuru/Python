from playwright.sync_api import sync_playwright
from pykml import parser
import pandas as pd
import json

links = {
    "recognized_identification_areas": "https://udds-faa.opendata.arcgis.com/datasets/c7ad6f733cce47b9a653e12010742361_0/explore"
}

def retrieve_file_name(link):
    path = None

    with sync_playwright() as playwright_instance:
        chromium = playwright_instance.chromium  # or "firefox" or "webkit".
        browser = chromium.launch(headless=False)
        page = browser.new_page()

        with page.expect_download(timeout=0) as download_info:
            page.goto(link)
            page.wait_for_load_state("networkidle", timeout=0)

            page.locator(".btn.btn-default.btn-block").click()
            page.wait_for_load_state("networkidle", timeout=0)

            sub_group = page.locator("hub-download-card").nth(1)
            button = sub_group.locator("calcite-button")

            if button.inner_text() == "Download":
                # pre-generated data
                button.click()
            else:
                button.click()
                sub_group.locator("calcite-dropdown-item").nth(0).click()
                attr_to_track = sub_group.locator("hub-download-notice[file-status='ready']")

                # Takes About 5-10 mins to generate new data
                attr_to_track.wait_for(timeout=0)

            download = download_info.value

            path = "./" + download.suggested_filename
            download.save_as(path)

            page.wait_for_load_state("networkidle", timeout=0)

        browser.close()

    return path

def extract_fria_data(file_path):
    root = None

    with open(file_path, 'r') as file:
        root = parser.parse(file).getroot()

    dataset = []

    for placemark in root.Document.findall('.//{http://www.opengis.net/kml/2.2}Placemark'):
        obj_id = placemark.find('.//{http://www.opengis.net/kml/2.2}SimpleData[@name="ObjectId"]')
        coordinates = placemark.find('.//{http://www.opengis.net/kml/2.2}coordinates')
        address = placemark.find('.//{http://www.opengis.net/kml/2.2}SimpleData[@name="address1"]')
        city = placemark.find('.//{http://www.opengis.net/kml/2.2}SimpleData[@name="city"]')
        state = placemark.find('.//{http://www.opengis.net/kml/2.2}SimpleData[@name="state"]')

        dataset.append({
            'object_id': obj_id.text if obj_id is not None else 'N/A',
            'coordinates': coordinates.text if coordinates is not None else 'N/A',
            'address': address.text if address is not None else 'N/A',
            'city': city.text if city is not None else 'N/A',
            'state': state.text if state is not None else 'N/A',
        })

    return dataset

for k, v in links.items():
    file_path = retrieve_file_name(v)

    dataset = None

    match k:
        case "recognized_identification_areas":
            dataset = extract_fria_data(file_path)

        case _:
            pass

    if dataset:
        df = pd.DataFrame(dataset)
        print(df.head().to_json(orient="records", lines=True))
