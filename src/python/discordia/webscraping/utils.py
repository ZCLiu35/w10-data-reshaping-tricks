from bs4 import BeautifulSoup

from IPython.display import display, HTML

def show_HTML(web_element):
    if isinstance(web_element, str):
        return display(HTML(web_element))
    else:
        return display(HTML(web_element.get_attribute('outerHTML')))

def get_pretty_HTML(web_element):
    if isinstance(web_element, str):
        return BeautifulSoup(web_element, 'html.parser').prettify()
    else:
        return BeautifulSoup(web_element.get_attribute('outerHTML'), 'html.parser').prettify()

def print_HTML(web_element):
    return print(get_pretty_HTML(web_element))