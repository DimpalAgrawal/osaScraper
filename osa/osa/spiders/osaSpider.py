#from scrapy.spider import BaseSpider
from scrapy.http import FormRequest, Request, Response, HtmlResponse, XmlResponse
from scrapy.selector import Selector
from scrapy.item import Item, Field
from scrapy.exceptions import CloseSpider
import os
import scrapy
import re
# import dropbox;
	

class osaSpider(scrapy.Spider):
	name = "osa"
	start_urls= ['http://wholesale.osaaustralia.com.au/']

	def __init__(self, **kwargs):
		print("Tasco started")
		self.username = "sales@safarifirearms.com.au"
		self.password = "Safari2016"
		self.output_file = ""
		self.isImageScrapper = "0"
		# self.client = dropbox.client.DropboxClient('-mWLE355VDAAAAAAAAAAWyC7WyBYPuwu2SdC038mivpGSPjUEhHIwc2hFfMjOPtd')
	
	def parse(self, response):
		print("inside parse")
		try:
			yield Request(url="http://wholesale.osaaustralia.com.au/login", callback=self.before_login)
		except CloseSpider as e:
    			print("Error: 500 Internal Server Error occurred")
	
	def before_login(self, response):
		print("inside  before login")
		token = response.xpath("//input[@class='authenticity_token']/@value").extract()
		print(token)
		formdata ={}
		formdata['user[email_address]'] = self.username
		formdata['user[password]'] =  self.password
		formdata['authenticity_token'] = token
		formdata['on_failure']= 'render:/login'
		formdata["login"] = ""
		formdata['on_success']= 'redirect:/'
		req = FormRequest(url="http://wholesale.osaaustralia.com.au/login", formdata=formdata, callback= self.afterLogin)
		yield req
		
		
	def cleanhtml(self, raw_html):
		cleanr = re.compile('<.*?>')
		cleantext = re.sub(cleanr, '', raw_html)
		cleantext = re.sub(r'[^\x00-\x7f]', r' ', cleantext)
		cleantext = cleantext.replace("\n", " ").replace("\r", " ").strip()
		return cleantext

	def afterLogin(self, response):
		print("after Login")
		req = Request("https://wholesale.osaaustralia.com.au/categories/", callback= self.categories)
		yield req

	def categories(self, response):
		print("inside categories")
		link = response.xpath("//div[@class='row d-flex flex-wrap']/div/div/div/a/@href").extract()
		for links in link:
			# yield{"links": links}
		    req = Request(url="http://wholesale.osaaustralia.com.au/" + links, callback = self.fetchSubCategories)
		    yield req
	
	def fetchSubCategories(self, response):
		# hxs = HtmlXPathSelector(response);
		subcat_list = response.xpath("//div[@class='category-wrap']/div/div/div/div/a/@href").extract()
		for subcat_link in subcat_list:
			# print(subcat_link)
			# yield{"subcat_link": subcat_link}
			req = Request(url="http://wholesale.osaaustralia.com.au/" + subcat_link, callback=self.getProductLinks, dont_filter=True);
			#req = Request(url="http://wholesale.osaaustralia.com.au/categories/ACCESSORIES/CLAY_TARGET_THROWERS", callback=self.getProductLinks, dont_filter=True);
			
			yield req;
			# break;

	def getProductLinks(self, response):
		product_links = response.xpath("//div[@class='result-row d-flex align-center flex-wrap']/div/a/@href").extract()
		for links in product_links:
			# yield{"products Links" : links}

			req = Request(url = "http://wholesale.osaaustralia.com.au/" + links , callback = self.getFetchdata)
			yield req

	def getFetchdata(self, response):
		print("Inside Fetch_Data")
		# if response.status == 500:
        #             	raise CloseSpider("Received 500 Internal Server Error")
		hxs = Selector(response)
		rows = hxs.xpath("//table[@class='product_table']")
		# sku = response.url.split("/")[-1]
		title = self.cleanhtml(hxs.xpath("//div[@class='av-product-title-wrap']/h2/text()")[0].extract())
		price = self.cleanhtml(hxs.xpath("//div[@class='av-product-details w-100']/div[4]/div/div/div/text()")[0].extract())
		img = hxs.xpath("//div[@class='av-img-placeholder-wrap']/img/@src")[0].extract()

		for row in rows:
			product_code = row.xpath(".//tr[2]/td[2]/text()").extract()
			uom = row.xpath(".//tr[3]/td[2]/text()")[0].extract()
			case_qty = row.xpath(".//tr[4]/td[2]/text()")[0].extract()
			brand = row.xpath(".//tr[1]/td[2]/text()")[0].extract()
			stock = row.xpath(".//tr[5]/td[2]/span/text()")[0].extract()
			in_transit = row.xpath(".//tr[6]/td[2]/span/text()")[0].extract()
			description = row.xpath(".//tr[8]/td[2]/text()")[0].extract()
			
		yield {"product_title": title, "product_price": price,"product_code": product_code,
				   "uom": uom, "case_qty": case_qty, "brand": brand, "stock_level": stock, "in_transit": in_transit, "descrption": description, 
				   "product_img": "https://wholesale.osaaustralia.com.au" + img, "scraper_name": "osa"}
		







		
	# def after_login(self, response):
	# 	self.logger.info('Login successful')
        # Check if login is successful (you might want to implement some checks here)
       
	# formdata = {'authenticity_token': 'lCeZWsCMJvWnm6Hr7YYKputajXWx1ALOWuqhyvTNmilSdht9eAT39mbQ3vcf+gM+2OwNJpJSe6zW3s5RKlx5bw==', 'redirect_uri': '/login?orig_req_url=%2F','on_failure': 'render:/login','on_success': 'redirect:/', 'user[email_address]': 'sales@safarifirearms.com.au','user[password]': 'Safari2016'}
	

	# def __init__(self, **kwargs):
	# 	print("Tasco started")
	# 	self.username = "sales@safarifirearms.com.au";
	# 	self.password = "Safari2016";
	# 	self.output_file = "";
	# 	self.isImageScrapper = "0";
	# 	#self.client = dropbox.client.DropboxClient('-mWLE355VDAAAAAAAAAAWyC7WyBYPuwu2SdC038mivpGSPjUEhHIwc2hFfMjOPtd')
			
	# 	if 'isImageScrapper' in kwargs:
	# 		self.isImageScrapper = "1";


	# def parse(self,response):
	# 	formdata = {};
	# 	formdata["user[email_address]"] = self.username;
	# 	formdata["user[password]"] = self.password;
	# 	formdata["on_success"] = "redirect:/account";
	# 	formdata["action_results.x"] = "22";
	# 	formdata["action_results.y"] = "6";
	# 	formdata["action_results"] = "Submit";
	# 	req = FormRequest(url="http://wholesale.osaaustralia.com.au/login", formdata=formdata,callback=self.afterLogin);
	# 	yield req;


	# def afterLogin(self, response):
	# 	f = open("afterLogin.html", "wb");
	# 	f.write(response.body);
	# 	f.close();
		
	# 	print ("HEllo");
	# 	hxs = Selector(response);
	# 	category_list = response.xpath("//div[@class='categoryrow']/a/@href").extract();
	# 	for category_link in category_list:
	# 		print (category_link);
			
	# 		yield{"category_link" : category_link}
	# 		req = Request(url="http://wholesale.osaaustralia.com.au/" + category_link, callback=self.fetchSubCategories, dont_filter=True);
	# 		yield req;
	# 		#break;
		
	# def fetchSubCategories(self, response):
	# 	hxs = HtmlXPathSelector(response);
	# 	subcat_list = hxs.select("//div[@class='category_box']/div[@class='category_title']/a/@href").extract();
	# 	for subcat_link in subcat_list:
	# 		print (subcat_link);
	# 		req = Request(url="http://wholesale.osaaustralia.com.au/" + subcat_link, callback=self.getProductLinks, dont_filter=True);
	# 		#req = Request(url="http://wholesale.osaaustralia.com.au/categories/ACCESSORIES/CLAY_TARGET_THROWERS", callback=self.getProductLinks, dont_filter=True);
			
	# 		yield req;
	# 		#break;
			
	# def getProductLinks(self, response):
	# 	hxs = HtmlXPathSelector(response);
	# 	product_list = hxs.select("//table[@id='list-result']//tr/td[1]/a/@href").extract();
	# 	rows = hxs.select("//table[@id='list-result']//tr");
	# 	for row in rows:
	# 		if len(row.select("td")) == 0:
	# 			continue
	# 		product_link = row.select("td[1]/a/@href")[0].extract()
	# 		try:
	# 			original_price = row.select("td[4]/strike/text()")[0].extract()
	# 		except:
	# 			original_price = row.select("td[4]/text()")[0].extract()
	# 		req = Request(url="http://wholesale.osaaustralia.com.au/" + product_link, callback=self.getProductDetail, dont_filter=True);
	# 		req.meta["original_price"] = original_price
	# 		print(product_link, original_price)
	# 		yield req;
	# 	'''	
	# 	for product_link in product_list:
	# 		req = Request(url="http://wholesale.osaaustralia.com.au/" + product_link, callback=self.getProductDetail, dont_filter=True);
	# 		yield req;
	# 		#break;
	# 	'''	
	# def getProductDetail(self, response):
		
	# 	hxs = HtmlXPathSelector(response);
	# 	original_price = response.request.meta["original_price"]
	# 	rows = hxs.select("//table[@id='product_table']//tr")
	# 	category_list = hxs.select("//p[@class='product_breadcrumb']/a/text()");
	# 	print (category_list);
	# 	product_title = self.normalizeValue(hxs.select("//div[@class='product_title']/text()")[0].extract());
	# 	product_price = self.normalizeValue(hxs.select("//div[@class='product_price']/span/text()")[0].extract());
	# 	product_img = "";
	# 	try:
	# 		product_img = "http://wholesale.osaaustralia.com.au" + hxs.select("//div[@id='product_img']//img/@data-zoomsrc")[0].extract();
	# 	except:
	# 		pass;
	# 	brand = "";
	# 	product_code = "";
	# 	uom = "";
	# 	case_qty = "";
	# 	sku = "";
	# 	stock_level = "";
	# 	in_transit = "";
	# 	description = "";
	# 	#print "Title " + self.normalizeValue(product_title);
	# 	#print "Price " + self.normalizeValue(product_price);
	# 	sku = response.url.split("/")[-1];
	# 	for row in rows:
	# 		try:
	# 			col_name = row.select("td/strong/text()")[0].extract();
	# 			col_value = self.normalizeValue(row.select("td/text()")[0].extract());
	# 		except:
	# 			try:
	# 				col_value = self.normalizeValue(row.select("td/span/text()")[0].extract());
	# 			except:
	# 				pass;
	# 			pass;
	# 			continue;
	# 		if "Brand" in col_name:
	# 			brand = col_value;
	# 		elif "Product Code" in col_name:
	# 			product_code = col_value;
	# 		elif "UOM" in col_name:
	# 			uom = col_value
	# 		elif "Case Qty" in col_name:
	# 			case_qty = col_value;
	# 		elif "Stock Level" in col_name:
	# 			stock_level = self.normalizeValue(row.select("td/span/text()")[0].extract());
	# 			if(stock_level=="Out"):
	# 				stock_level=0
	# 		elif "In Transit" in col_name:
	# 			in_transit = col_value;
	# 		elif "escription" in col_name:
	# 			description = col_value;
	# 	'''		
	# 	print product_title;
	# 	print product_price;
	# 	print brand;
	# 	print product_code;
	# 	print uom;
	# 	print case_qty;
	# 	print stock_level;
	# 	print in_transit;
	# 	print description;
	# 	print product_img;
	# 	'''
	# 	if self.isImageScrapper == "1":
	# 		if product_img == "":
	# 			return;
	# 		wget.download(product_img , sku + ".jpg");
	# 		f = open(sku+".jpg", 'rb')
	# 		response = self.client.put_file('/OSA_Scraped_Pictures/' + sku+".jpg", f, overwrite=True)
	# 		print ("uploaded:", response)
	# 		os.remove(sku+".jpg");
	# 		return;
	# 	item = OsaItem();
	# 	item["sku"] = sku;
	# 	item["title"] = product_title;
	# 	item["price"] = product_price;
	# 	item["original_price"] = original_price
	# 	item["product_code"] = product_code;
	# 	item["uom"] = uom;
	# 	item["case_qty"] = case_qty;
	# 	item["brand"] = brand;
	# 	item["stock"] = stock_level;
	# 	item["in_transit"] = in_transit;
	# 	item["description"] = description;
	# 	item["img"] = product_img;
	# 	item["scraper_name"] = "osa";
		
	# 	return item;
				
	# def normalizeValue(self, value):
	# 	value = value.replace("\r", " ");
	# 	value = value.replace("\n", " ");
	# 	value = value.replace("'", "\\'");
	# 	return value.strip();


	# def start_requests(self):
	# 	yield scrapy.FormRequest(url=self.starting_page,callback= self.parse, method="POST", formdata= self.formdata, headers= self.headers)

	# def parse(self, response):
	# 	link = response.xpath("https://wholesale.osaaustralia.com.au/categories/")

	# 	for links in link:
	# 		yield{"links":links}
	
	# def parse(self, response):
	# 	print("inside parse")
	# 	req = Request(url="https://wholesale.osaaustralia.com.au/categories", callback=self.categories)
	# 	yield req

	# def categories(self, response):
	# 	print("Inside Categories")
	# 	hxs = Selector(response)
	# 	category_list = hxs.xpath("//div[@class='row']/div/div/div/div/div/div/a/@href").extract()
	# 	print(category_list)
		# for category_link in category_list:
		# 	print(category_link)
			# req = Request(url="http://wholesale.osaaustralia.com.au/" + category_link, callback=self.fetchSubCategories)
			# yield req
			# break;
