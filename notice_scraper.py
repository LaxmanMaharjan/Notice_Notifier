# -*- coding: utf-8 -*-
import scrapy
import pandas as pd
from scrapy.crawler import CrawlerProcess
import datetime
import smtplib
import pickle
import os

from email.message import EmailMessage

data = pd.read_csv("Notice_Infos.csv")
date = str(datetime.date.today())


class NoticeScraperSpider(scrapy.Spider):
    name = 'notice_scraper'
    allowed_domains = ['khwopa.edu.np']
    start_urls = ['https://khwopa.edu.np/']
    
    '''
    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'Notice_Infos.csv',
        'FEED_EXPORT_ENCODING' : 'utf-8'
    }
'''
    def parse(self, response):
        """ This function first scrapes the link and Title of the Notice published in college website.
        """

        infos = response.xpath("//div[@class='col-md-4 wbod']/table[@class='table table-bordered table-hover']/tr/td/a")
        for info in infos:
            Link = info.xpath('.//@href').get()
            Title = info.xpath('.//text()').get()
            yield scrapy.Request(url= Link, callback=self.parse_info, meta={'Link':Link, 'Title':Title})

    def parse_info(self, response):
        """This function is called with link and tile of notice as meta data and This
        function now follows the link and scrape the image of notice and all together
        yields tile and image of the notice.
        """

        Title = response.request.meta['Title']
        Image = response.xpath("//div[@class='post-image']/a/img/@src").get()


        # if the title of the notice doesn't exist in previous csv file it is new notice.
        # Since it is new Notice notify it and add it to previous existing csv file.

        if (Title in data.Title.tolist()) == False:

            # appending new notice in existing csv file
            data1 = data.append({'Date':date,
            'Title':response.request.meta['Title'],
                'Image':response.xpath("//div[@class='post-image']/a/img/@src").get()},ignore_index=True).sort_values(by = 'Date', ascending = False)

            yield {'Date':date,
            'Title':response.request.meta['Title'],
                'Image':response.xpath("//div[@class='post-image']/a/img/@src").get()}
            # get email and password from environment variables
            EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
            EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')

            msg = EmailMessage()
            msg['Subject'] = Title
            msg['From'] = NoticeScraperSpider.gmail.get_username()
            msg['To'] = 'lxmnmrzn@gmail.com'

            msg.set_content(Image)


            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)


            data1.to_csv("Notice_Infos.csv",index=False)


if __name__=='__main__':
    #run spider
    process = CrawlerProcess()
    process.crawl(NoticeScraperSpider)
    process.start()
