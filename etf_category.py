import requests
from bs4 import BeautifulSoup
import math
import re
import pandas as pd
from common.utility import logger, since_last_update
from common.parse_tables import parse_table, get_paginated_table



class ETFCategoryScraper():
    def __init__(self):
        self.baseline_url = "https://etfdb.com/etfs/"
        self._get_baseline_links()


    def _get_baseline_links(self):
        response = requests.get(self.baseline_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)

        urls = [link["href"] for link in links]

        urls = set([u for u in urls if re.match(r'^https?://', u)])

        channel = []
        themes = []
        commission_free = []

        for url in urls:

            if "themes" in url:
                themes.append(url)

            elif 'asset-class' in url:
                channel.append(url)

            elif "commission-free" in url:
                commission_free.append(url)

        self.category_url = {"channel": channel, "themes": themes, 
                             "commission free": commission_free}
    
    def list_etf_categories(self):

        # Send a GET request to the URL
        response = requests.get(self.baseline_url)

        # Parse HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all divs with class containing 'table'
        table_divs = soup.find_all('div', class_=lambda x: x and 'table' in x)
        etf_tables = {}
        if table_divs is None:
            logger.error(f"{url} does not contain any tables")
            return None
        logger.info(f"number of tables {len(table_divs)}")
        # Iterate over each div containing tables
        for table_id, div in enumerate(table_divs):
            if not div.find("h3"):
                continue
            table_name = div.find('h3').text

            cur_table = parse_table(div)
            if table_name is not None:
                etf_tables[table_name] = pd.DataFrame(cur_table)

        self.etf_tables = etf_tables
        self._get_all_category_links()
        return etf_tables.keys()

    def _get_all_category_links(self):
        link_list = {}
        for tbl_name, tbl_det in self.etf_tables.items():
            link_list.update({"_".join(cur_link.split("/")[-3:-1]).replace("-", "_"): cur_link
                              for cur_link in tbl_det["link"]})
        self.link_list = link_list

    def save_all_etf_category(self, save_path, ignore_list=None):
        if not hasattr(self, "link_list"):
            self.list_etf_categories()
        ignore_list = [] if ignore_list is None else ignore_list
        ignore_list += [file_name for file_name in self.link_list.keys() if since_last_update(f"{save_path}/{file_name}.parquet") > 3600]
        failed_list = []
        for file_name, file_path in self.link_list.items():
            save_file_name = f"{save_path}/{file_name}.parquet"

            if file_name in ignore_list:
                logger.info(f"ignored {file_name}")
                continue
            try:
                logger.info(f"working on {file_path}")
                cur_df = self.get_etf_by_category(file_path)
                logger.info(f"{file_name} has {len(cur_df.index)} rows")
                cur_df.to_parquet(save_file_name)
            except Exception:
                logger.error(f"Failed to retrieve data for {file_path}")
                failed_list.append(file_path)

        return failed_list


    def get_etf_by_category(self, category_url):
        url = category_url if "https:" in category_url else f"https:{category_url}"
        response = requests.get(url)

        if response.status_code != 200:
            logger.warning(f"invalid url {url}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        response.close()
        table = soup.find('table')
        rows_per_page = int(table.get("data-page-size"))
        table_rows = int(table.get("data-total-rows"))
        num_page = math.ceil(table_rows / rows_per_page) + 1
        logger.info(f"there are {table_rows} etfs for {category_url}")
        headers = [th.text.strip().split("\n")[0] for th in table.find_all("th")]

        rows = []
        for n in range(1, num_page):
            logger.info(f"working on {n} out of {num_page - 1}")
            suffix_url = f"#etfs&sort_name=assets_under_management&sort_order=desc&page={n}"
            response = requests.get(f"{url}{suffix_url}")
            if response.status_code != 200:
                logger.error(f"failed to retrieve page {n} using url {url}{suffix_url}")
                continue

            soup = BeautifulSoup(response.text, 'html.parser')
            response.close()
            rows += get_paginated_table(soup, headers)


        return pd.DataFrame(rows)


