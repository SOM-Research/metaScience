__author__ = 'atlanmod'

from selenium import webdriver


GOOGLE = 'http://www.google.com'


def main():
    driver = webdriver.Chrome(executable_path='C:\Program Files (x86)\Google\Chrome\chromedriver.exe')
    driver.get(GOOGLE)
    driver.close()

if __name__ == "__main__":
    main()