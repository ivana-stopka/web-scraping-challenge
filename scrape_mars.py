# Dependencies
from bs4 import BeautifulSoup as bs
import requests
import pymongo
from splinter import Browser
from flask import Flask, render_template, redirect
from flask_pymongo import PyMongo
import pandas as pd

# Initiate browser
def init_browser():
    executable_path = {"executable_path":"chromedriver.exe"}
    browser = Browser("chrome", **executable_path, headless=False)
    return browser

# Initiate function scrape that will run scraping code and return dictionary.
def scrape():
    browser=init_browser()
    mars_dict={}

    # ----------------------------------------------------------------------------
    # Mars News Site
    # ----------------------------------------------------------------------------
    # URL of page to be scraped
    mn_url = "https://redplanetscience.com/"
    browser.visit(mn_url)
    html=browser.html

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(html, "html.parser")

    # Retrieve the latest news title
    news_title=soup.find_all("div", class_="content_title")[0].text

    # Retrieve the latest news paragraph
    news_para=soup.find_all("div", class_="article_teaser_body")[0].text

    # ----------------------------------------------------------------------------
    # JPL Mars Space Images
    # ----------------------------------------------------------------------------
    # URL of page to be scraped
    jpl_url="https://spaceimages-mars.com"
    browser.visit(jpl_url)
    html=browser.html

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(html, "html.parser")

    # Find the featured image
    image_url=soup.find("img", class_="headerimage fade-in").attrs["src"]

    # Combine the jpl_url with the image_url
    featured_image_url=jpl_url+"/"+image_url

    # ----------------------------------------------------------------------------
    # Mars Facts
    # ----------------------------------------------------------------------------
    # URL of page to be scraped
    mf_url="https://galaxyfacts-mars.com/"

    # Read the tables on the page using Pandas. Viewed each table (element) and found table of interest
    # was element 1, therefore tables[1].
    tables=pd.read_html(mf_url)

    # Store mars facts in a table, rename the columns.
    mars_facts=tables[1]
    mars_facts_final=mars_facts.rename(columns={0:"Parameter",1:"Value"})
    mars_facts_final.set_index("Parameter",inplace=True)

    # Convert mars_facts_final table to html table string.
    mars_table_html=mars_facts_final.to_html()

    # ----------------------------------------------------------------------------
    # Mars Hemispheres
    # ----------------------------------------------------------------------------
    # URL of page to be scraped
    mh_url = "https://marshemispheres.com/"

    browser.visit(mh_url)
    html=browser.html

    # Create BeautifulSoup object; parse with 'html.parser'
    soup = bs(html, "html.parser")

    # Extract the item elements. Class = "collapsible results" contains the full list and class = "items"
    # contains the individual items in which the image and header are stored.
    mars_list=soup.find("div",class_="collapsible results")
    mars_item=mars_list.find_all("div",class_="item")

    # Create an empty list to store the images and url's.
    hems_image_urls=[]

    # Loop through each item in mars_items
    for item in mars_item:
        # Error handling
        try:
            # Extract title
            hem=item.find("div",class_="description")
            title=hem.h3.text
            # Extract image url
            hem_url=hem.a["href"]
            browser.visit(mh_url+hem_url)
            html=browser.html
            soup=bs(html,"html.parser")
            image_src=soup.find("li").a["href"]
            image_url=mh_url+image_src
            if (title and image_url):
                # Print results
                print("------------------------------------------")
                print(title)
                print(image_url)
            # Create dictionary for title and url
            hems_dict={
                "title":title,
                "image_url":image_url
            }
            hems_image_urls.append(hems_dict)
        except Exception as e:
            print(e)

    # ----------------------------------------------------------------------------
    # Final Dictionary
    # Create dictionary for all info scraped from sources above
    mars_dict={
        "news_title":news_title,
        "news_paragraph":news_para,
        "featured_image":featured_image_url,
        "fact_table":mars_table_html,
        "hemisphere_images":hems_image_urls
    }

    # ----------------------------------------------------------------------------
    # Close the browser after scraping
    browser.quit()
    return mars_dict

if __name__ == "__main__":
    scrape()