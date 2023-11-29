"""
WEB SCRAPING: They Work For You website

We decided to scrape the data from the They Work For You website instead of Hansard because 
it was easier to scrape and contains the same information.

AUTHORS:

- Jon Cardoso-Silva (https://jonjoncardoso.github.io)
- Terry Zhou (https://github.com/tz1211)
- Nikolai Semikhatov (https://github.com/Sevnhutsjr)

DATE: 2023-11-29

"""

import re
import bs4
import requests
import warnings
import itertools

import pandas as pd

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException

BASE_URL = "https://www.theyworkforyou.com/debates/?d=YYYY-MM-DD"

def build_url(date_object, base_url=BASE_URL):
    """Builds a URL for a given date object.
    
    I decided to use a datetime object directly because it will be easier to navigate using pandas' datetime functions.
    
    Args:
        date_object (datetime): A datetime object.
        base_url (str): A base URL that will be used to build the URL.

    Returns:
        str: A URL for a given date object.

    """

    return (
        base_url.replace("YYYY", f"{date_object.year:04d}")
                .replace("MM", f"{date_object.month:02d}")
                .replace("DD", f"{date_object.day:02d}")
    )

#### DEBATE SECTIONS ####

def get_debate_item(a_element, section=None, section_excerpt=None):
    """
    Extracts the debate item from the <a> element. This element usually looks like:

    <a class="business-list__title" href="/debates/?id=2023-11-15b.633.6">
        <h3>
            Rural Connectivity
        </h3>
        <span class="business-list__meta">
            6 speeches
        </span>
    </a>

    and precedes a <p> element with the excerpt of the debate:

    <p class="business-list__excerpt">
       What steps her Department is taking to improve rural connectivity.
    </p>

    This <p> tag is a sibling of the <a> tag, and can be accessed with the XPath:

    ./following-sibling::p

    Args:
        a_element (Selenium WebElement): The <a> element containing the debate item.
        section (str): The section title, if any.
        section_excerpt (str): The section excerpt, if any.

    Returns:
        dict: A dictionary with the following keys:
            - debate_id (str): The debate ID, e.g. 2023-11-15b.633.6
            - debate_excerpt (str): The excerpt of the debate
            - url (str): The URL of the debate
            - title (str): The title of the debate
            - section (str): The section title, if any.
            - section_excerpt (str): The section excerpt, if any.
    """

    if not isinstance(a_element, WebElement):
        raise ValueError(f"Expected a Selenium WebElement but got {type(a_element)}")

    url = a_element.get_attribute('href')
    try:
        debate_excerpt = a_element.find_element(By.XPATH, "./following-sibling::p").text
    except NoSuchElementException:
        debate_excerpt = None

    return {
        "debate_id": re.search(r".*id=(.*)", url).group(1),
        "debate_excerpt": debate_excerpt,
        "url": url,
        "title": a_element.find_element(By.CSS_SELECTOR, "a > h3").text,
        "section": section,
        "section_excerpt": section_excerpt
    }

def get_debate_section(debate_section):
    """Extracts the debate items from a debate section.

    A debate section usually looks like the following if it has debate blocks inside:

    <div class="business-list__section">
        <h3>
            <a href="/debates/?id=2023-11-15b.633.6">
                Rural Connectivity
            </a>
        </h3>
        <p>
            What steps her Department is taking to improve rural connectivity.
        </p>
        <ul>
            <li>
                <a class="business-list__title" href="/debates/?id=2023-11-15b.633.6">
                    <h3>
                        Rural Connectivity
                    </h3>
                    <span class="business-list__meta">
                        6 speeches
                    </span>
                </a>
            </li>
            <a class="business-list__title" href="/debates/?id=2023-11-15b.634.6">
                <h3>
                    Rural Connectivity
                </h3>
                <span class="business-list__meta">
                    6 speeches
                </span>
            </a>
            ...
        </ul>
    </div>

    The code in this function handles both standalone debate items and debate sections with multiple debate items.

    Args:
        debate_section (Selenium WebElement): The debate section.

    Returns:
        list: A list of debate items.

    """

    if not isinstance(debate_section, WebElement):
        raise ValueError(f"Expected a Selenium WebElement but got {type(debate_section)}")

    first_child = debate_section.find_element(By.CSS_SELECTOR, ":first-child")
    debate_items = []
    if first_child.tag_name == "a":
        debate_items = [get_debate_item(first_child)]
    elif first_child.tag_name == "div":
        section_title = debate_section.find_element(By.CSS_SELECTOR, "div > h3").text
        section_title_excerpt = debate_section.find_element(By.CSS_SELECTOR, "p").text
        debate_items = [get_debate_item(a_element, section=section_title, section_excerpt=section_title_excerpt) 
                        for a_element in debate_section.find_elements(By.XPATH, "./ul//a")]
    else:
        msg = (
            "Unexpected tag name. Expected one of: ['a', 'div'] "
            f"but got {first_child.tag_name}. "
            f"Context:{debate_section.get_attribute('outerHTML')}"
        )
        warnings.warn(msg)
        
    return debate_items

def scrape_debate_sections(driver):
    """Scrapes the debate sections from the page.

    Args:
        driver (Selenium WebDriver): The driver.

    Returns:
        list: A list of debate sections.

    """

    if not isinstance(driver, webdriver.Firefox):
        raise ValueError(f"Expected a Selenium Firefox WebDriver but got {type(driver)}")

    debate_sections = driver.find_elements(By.CSS_SELECTOR, "ul.business-list > li")
    all_debate_sections = [get_debate_section(debate_section) for debate_section in debate_sections]
    df = pd.DataFrame(itertools.chain.from_iterable(all_debate_sections))
    return df

#### DEBATE SPEECHES ####

def scrape_one_speech(speech_block, url): 
    """
    Extracts information about speaker and speech content from one <div> block for speeches. 
    
    Args: 
        speech_block (bs4.element.Tag): <div> block for speech 
    
    Returns: 
        dict: A dictionary with the following keys: 
            - debate_id (str): The debate ID, e.g. b.633.6 
            - speech_id (str): The Speech ID, e.g. g631.2 
            - speaker_id (str): The Speaker ID, e.g. 26020 
            - speaker_position (str): Information about the position of the speaker 
            - speech_html (str): speech content in html (containing embedded links) 
            - speech_raw_text (str): speech content as raw text 
    """

    if not isinstance(speech_block, bs4.element.Tag):
        raise ValueError(f"Expected a BeautifulSoup object but got {type(speech_block)}")

    speaker_block = speech_block.find("h2", attrs={"class": "debate-speech__speaker"})
    if speaker_block: 
        unparsed_speaker_id = speaker_block.find("a").get("href")
    else: # this is to account for the "Several hon. Members rose––" situation
        return None 

    content_block = speech_block.find("div", attrs={"debate-speech__content"})
    content = content_block.find_all("p")
    speech_html, speech_raw_text = "", ""
    for paragraph in content: 
        speech_html += paragraph.prettify()
        speech_raw_text += paragraph.text + "\n\n"

    return {
        "debate_id": re.search(r".*id=(.*)", url).group(1), 
        "speech_id": speech_block.get("id"), 
        "speaker_id": re.search(r".*p=(.*)", unparsed_speaker_id).group(1), 
        "speaker_position": speaker_block.find("small").text,
        "speech_html": speech_html, 
        "speech_raw_text": speech_raw_text[:-2]
    }

def get_all_speech_blocks(url): 
    """
    Extracts all the <div> blocks for speeches within a debate containing information about the speakers and the speech content. Example: 
    
    <div class="debate-speech" id="g631.2">
    <div class="full-page__row">
    <div class="full-page__unit">
    <a name="g631.2">
    </a>
    <div class="debate-speech__speaker-and-content">
        <h2 class="debate-speech__speaker">
        <a href="/mp/?p=26020">
        <img alt="Photo of Anum Qaisar" src="/people-images/mps/26020.jpg"/>
        <strong class="debate-speech__speaker__name">
        Anum Qaisar
        </strong>
        <small class="debate-speech__speaker__position">
        Shadow SNP Spokesperson (Levelling Up)
        </small>
        </a>
        </h2>
        <div class="debate-speech__content">
        <p pid="b631.2/1" qnum="900099">
        What steps her Department is taking to tackle harmful
        <a href="https://en.wikipedia.org/wiki/AI-generated_content" rel="nofollow">
        AI-generated content
        </a>
        on social media.
        </p>
    ...
    </div>
    </div>
    </div>

    
    Args: 
        url (str): url of the debate webpage 
    
    Returns: 
        speech_blocks (list of bs4.element.Tag): list of all <div> blocks for speeches
    """
    
    response = requests.get(url) 
    if response.status_code == 200: 
        soup = BeautifulSoup(response.content, "html.parser")
        speech_blocks = soup.find_all("div", attrs={"class": "debate-speech"})
        return speech_blocks
    return None 

def get_speeches(url): 
    """
    Wrapper function for `get_all_speech_blocks` and `scrape_one_speech`. Takes the url of a debate page and returns a pd.DataFrame of corresponding information. 
    
    Args: 
        url (str): url of the debate web page 
    
    Returns: 
        pd.DataFrame: A Pandas df with following columns:  
            - debate_id (str): The debate ID, e.g. b.633.6  
            - speech_id (str): The Speech ID, e.g. g631.2  
            - speaker_id (str): The Speaker ID, e.g. 26020  
            - speaker_position (str): Information about the position of the speaker  
            - speech_html (str): speech content in html (containing embedded links)  
            - speech_raw_text (str): speech content as raw text  
    """
    speech_blocks = get_all_speech_blocks(url) 
    
    speech_info = [scrape_one_speech(speech, url) for speech in speech_blocks]
    # Remove None values from the list
    speech_info = [speech for speech in speech_info if speech is not None]
    df_speeches = pd.DataFrame(speech_info)

    return df_speeches

#### HOUSE DIVISIONS (VOTES) ####

