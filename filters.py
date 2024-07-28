from dataclasses import dataclass

import pick
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel


@dataclass
class RawOption(BaseModel):
    data_key: str
    label_text: str


@dataclass
class RawFilter(BaseModel):
    data_component: str
    button_text: str
    options: list[RawOption]


# Transform from list[RawFilter]
# to filters[27][1]=0&filters[27][2]=1&...&filters[28][achievement]=0&filters[29][1]=0
def ask_user_filters(filters: list[RawFilter]) -> str:
    filter_string = ""
    for f in filters:
        options = [option.label_text for option in f.options]
        selected = [
            label for (label, _) in pick.pick(options, f.button_text, multiselect=True)
        ]

        for option in f.options:
            if option.label_text in selected:
                filter_string += f"&filters[{f.data_component}][{option.data_key}]=1"
            else:
                filter_string += f"&filters[{f.data_component}][{option.data_key}]=0"

    return filter_string.strip("&")


def get_filters(url: str, cookies: dict[str, str]) -> list[RawFilter]:
    response = requests.get(url, cookies=cookies, timeout=5)
    response.raise_for_status()

    # Response text is html

    # Look for ul with class "filter-dropdown flex-list flex-wrap"
    #   Loop over li elements
    #       Note down "data-component" attribute
    #       Note down "button-text" attribute in sbx-pop-out node inside li
    #       Then inside the div with id "filter-component-<data-component>"
    #           Loop over li elements inside ul with class "option-list"
    #               Note down "data-key" in input node inside li
    #               Note down label text inside label inside li

    soup = BeautifulSoup(response.text, "html.parser")
    filters = []

    ul_element = soup.find("ul", class_="filter-dropdown flex-list flex-wrap")
    if not ul_element:
        return filters

    for li in ul_element.find_all(
        "li", class_="checklist item filter-component", recursive=False
    ):
        data_component = li.get("data-component")
        button_text = li.find("sbx-pop-out").get("button-text")

        div_id = f"filter-component-{data_component}"
        div_element = soup.find("div", id=div_id)
        if not div_element:
            print(f"Could not find div with id {div_id}")
            continue

        ul_option_list = div_element.find("ul", class_="option-list")
        if not ul_option_list:
            print("Could not find ul with class option-list")
            continue

        options = []
        for option_li in ul_option_list.find_all("li", recursive=False):
            data_key = option_li.find("input", type="checkbox").get("data-key")
            label_text = option_li.find("label").text.strip()
            options.append({"data_key": data_key, "label_text": label_text})

        filters.append(
            {
                "data_component": data_component,
                "button_text": button_text,
                "options": options,
            }
        )

    return [RawFilter.model_validate(f) for f in filters]
