#!/usr/bin/env python

__author__ = 'atlanmod'

from pyvirtualdisplay import Display
from selenium import webdriver


GOOGLE = 'http://www.google.com'


def main():
    display = Display(visible=0, size=(800, 600))
    display.start()

    browser = webdriver.Chrome()
    browser.get(GOOGLE)
    print browser.title
    browser.quit()

    display.stop()

if __name__ == "__main__":
    main()