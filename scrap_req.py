from flask import Flask, request, jsonify, render_template, Response
from scrapy.crawler import CrawlerProcess
from proj_scrap_web_page.proj_scrap_web_page.spiders.spider_scrap_web_page import MySpider
from twisted.internet import reactor
import json
import logging
from scrapy.utils.project import get_project_settings


app = Flask(__name__,template_folder='template')

@app.after_request
def add_cors_headers(response):
	# NEED TO ADD SPECIFIC ORGINS LATER 
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
	#response.headers['Access-Control-Allow-Methods'] = '*'
    return response

@app.route('/scrap', methods=['POST'])
def scrapWebpage():
	file_location = "proj_scrap_web_page/output.json"
	with open(file_location, "r") as f:
		json_data = json.load(f)
		response = jsonify(json_data) 
		return json_data

if __name__ == "__main__":
    app.run(debug=True)
       
