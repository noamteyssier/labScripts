#!/usr/bin/env python
# Author : Noam Teyssier

import selenium
import time
import argparse
import os
import getpass
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


def open_browser():
    browser = webdriver.Chrome()
    browser.get('http://www.quintarabio.com/user/myqb?id=15805')
    return browser

def login_to_MyQuintaraBio(browser, password):
    login = browser.find_element_by_name('login')
    login.send_keys('Anna.Chen@ucsf.edu')
    password = browser.find_element_by_name('password')
    password.send_keys(password + Keys.RETURN)

def new_excel_file_upload(browser):
    new_form = browser.find_element_by_link_text("Excel File Upload")
    new_form.send_keys(Keys.RETURN)

def click_fragment(browser):
    fr = browser.find_element_by_xpath('//*[@id="right-content"]/div/form/table/tbody/tr[1]/td[2]/input[2]')
    fr.click()

def upload_excel(browser, excel_name):
    ue = browser.find_element_by_name('datafile')
    ue.send_keys(excel_name)
    upload = browser.find_element_by_name('upload').click()

def pickup_date(browser, date):
    if date != None:
        pd = browser.find_element_by_xpath('//*[@id="ready_date"]')
        pd.clear()
        pd.send_keys(date)

def fill_nickname(browser, sample_name):
    nn = browser.find_element_by_name('seqorder_name')
    nn.send_keys(sample_name)

def finalize_order(browser):
    # browser.maximize_window()
    # browser.send_keys("")

    # first click
    first = browser.find_element_by_name('submit')
    first.send_keys("")
    first.click()

    # final click
    final = browser.find_element_by_name('confirm')
    browser.execute_script("arguments[0].scrollIntoView();", final)
    final.send_keys("")
    final.click()

def return_home(browser):
    home = browser.find_element_by_link_text("Back to Home Page")
    home.send_keys("")
    home.click()

def __main__():
    parser = argparse.ArgumentParser(description='Submit all 12 CE plate orders to QuintaraBio')
    parser.add_argument('-o','--output',help='Output file name (This will autofill the plate number)', required=False)
    parser.add_argument('-d', '--date' ,help='Date to Pick Up (Default is Today). Will require format MM/DD/YYYY', required=False)
    parser.add_argument('-n', '--numPlates', help = 'Number of plates to order (default is 12)', required=False)
    args = parser.parse_args()

    password = getpass.getpass()

    ## assign values ##
    sample_name = args.output
    date = args.date
    numPlates = 12
    path = os.getcwd()
    excel_name = os.path.abspath('/'.join([path ,'Quintara_Seq_OrderForm_row.xlsx']))

    if sample_name == None:
        sample_name = str(raw_input("Sample Name?\n>"))

    if args.numPlates:
        numPlates = int(args.numPlates)

    ## show values ##
    print ("Sample Name: %s (P1-P%s)" % (sample_name, str(numPlates)) )
    if args.date != None:
        print ("Date : %s" % args.date)


    ## Open Browser and Login to MyQuintara ##
    br = open_browser()
    login_to_MyQuintaraBio(br, password)

    ## Make the CE Plate Orders for Plates 1-12 ##
    for i in range(1, 1 + numPlates):
        plate_name = sample_name + '-P%i' %i
        new_excel_file_upload(br)
        click_fragment(br)
        upload_excel(br, excel_name)
        pickup_date(br, date)
        fill_nickname(br, plate_name)
        finalize_order(br)
        return_home(br)

    ## Close the Browser after completion ##
    br.close()

__main__()
