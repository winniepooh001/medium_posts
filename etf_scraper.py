import requests
from bs4 import BeautifulSoup
from common.utility import logger, flatten_dic
from common.parse_lists import parse_paired_list


class ETFScraper():
    def __init__(self, ticker):
        self.ticker = ticker
        self.base_url = "https://etfdb.com/etf"


    def get_flatten(self):
        soup = self.generate_soup()
        nested_dic = self.get_detail(soup)
        return flatten_dic(nested_dic)

    def generate_soup(self):
        self.url = f"{self.base_url}/{self.ticker}/#etf-ticker-profile"
        response = requests.get(self.url)

        # Parse HTML content
        if response.status_code != 200:
            logger.error(f"fail to retrieve the link {self.url}")
            return self.url
        soup = BeautifulSoup(response.text, 'html.parser')
        response.close()
        return soup

    def get_detail(self, soup):
        return_dict = self._get_holdings(soup)
        return_dict.update(self._get_technical(soup))
        return_dict.update(self._get_profile(soup))
        return return_dict

    def _get_profile(self, soup):
        profile_tables = soup.find_all("div", class_="col-sm-6 col-xs-12")

        profile_dicts = parse_paired_list(profile_tables[0:3], "div", "row")
        del profile_dicts['Analyst Report']

        profile_dicts.update(parse_paired_list([soup.find("div", id="factset-classification")], "tr"))
        profile_tables = [profile_tables[-1], soup.find("div", class_="data-trading bar-charts-table")]
        profile_dicts.update(parse_paired_list(profile_tables, "li"))

        return profile_dicts

    def _get_technical(self, soup):

        volatility = soup.find('table', class_=lambda x: x and 'volatility' in x)
        table_row = volatility.find_all("tr")
        volatility = {}
        for cur_row in table_row:
            cells = cur_row.find_all("td")
            volatility[cells[0].text.strip()] = cells[1].text.strip()

        other_technicals = soup.find_all("div", class_="col-md-6 col-xs-12")
        technical_dict = parse_paired_list(other_technicals, "li")

        return technical_dict


    def _get_holdings(self, soup):

        # limited by top 15 ignore
        # table = soup.find('table', id="etf-holdings")

        aux_holding_dict = {}
        for cur_table in ["holdings-table", "size-table"]:
            try:
                table = soup.find("table", id=cur_table)
            except AttributeError:
                continue
            table_rows = table.find("tbody").find_all("tr")
            cur_dict = {}
            for cur_row in table_rows:
                tds = cur_row.find_all("td")
                cur_dict[tds[0].text.strip()] = tds[1].text.strip()

            aux_holding_dict[cur_table] = cur_dict
        return aux_holding_dict
