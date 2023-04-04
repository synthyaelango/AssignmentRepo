import scrapy
import boto3
import logging

class MySpider(scrapy.Spider):
    name = "spider_scrap_web_page"

    def __init__(self, websiteUrl=None, pageUrl=None, **kwargs):
        super().__init__(**kwargs)
        self.websiteUrl = websiteUrl
        self.pageUrl = pageUrl

    def start_requests(self):
        url = self.websiteUrl+self.pageUrl
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        parseUrl = self.websiteUrl+self.pageUrl
        dynamodb = boto3.resource('dynamodb',region_name='ap-south-1',aws_access_key_id='AKIA6GQTHGHXEW2QDYND',aws_secret_access_key='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')
        table = dynamodb.Table('tab_scrap_web')
        resultMap = {}
        table_name = 'tab_scrap_web'
        key = {'web_pg_url': parseUrl}
        table.delete_item(TableName=table_name, Key=key)
        scrapedItem = table.get_item(Key={'web_pg_url': parseUrl})
        if 'Item' in scrapedItem:
            print("Item already in DB")
            item = scrapedItem['Item']
            yield item['scrap_cnt_map']
        else:
            print("Item not in DB")
            valueList = []
            if "/company/about-us" in self.pageUrl:
                resultMap = extract_data_aboutUs(self, response)
            elif "/company/our-culture" in self.pageUrl:
                resultMap = extract_data_culture(self, response)
            elif "/Why-Tachyon/similarities" in self.pageUrl:
                resultMap = extract_data_similarities(self, response)
            elif "/partners/partner-program-overview" in self.pageUrl:
                resultMap = extract_data_partner(self, response)
            elif "/solutions/overview" in self.pageUrl:
                resultMap = extract_data_overview(self, response)
            else:
                yield
            item = {
                'web_pg_url': parseUrl,
                'scrap_cnt_map': resultMap
            }
            table.put_item(Item=item)
            urlRes = [self.pageUrl]
            resultMap["pageUrl"]=urlRes
        yield resultMap


def extract_data_similarities(self, response):
    nextLine='\n'
    resultMap = {}
    valueList = []
    topic1 = response.css('h1::text').get()
    content1 = response.css('p::text').get().strip()
    valueList=[content1]
    for h4_selector in response.css('h4'):
        h4_selector_name = h4_selector.css('h4::text').extract()
        valueList.append(nextLine+h4_selector_name[0]);
        p_selector = h4_selector.css('h4 ~ ul li::text').extract()
        for p_selector_val in p_selector:
            valueList.append(p_selector_val.strip());
    resultMap[topic1] = valueList
    return resultMap

def extract_data_overview(self, response):
    nextLine='\n'
    resultMap = {}
    all_h3_selector = response.css('h3')
    h5_selectors = response.css('div.features-block3 h5')
    h4_selectors = response.css('div.about-service-detail h4')
    valueList_features = []
    valueList_service = []
    valueList_industry = []
    valueList_user = []
    cnt=1
    industryCnt = 1
    h5_industry_all = response.css('div.service-block1 h5')
    for h5_industry in h5_industry_all:
        p_industry = h5_industry.xpath('following-sibling::p[1]/text()').extract()
        a_industry = h5_industry.css("a:first-of-type::text").extract_first()
        if industryCnt>=9:
            valueList_industry.append(nextLine+a_industry)
            valueList_industry.append(p_industry)
        else:
            valueList_user.append(nextLine+a_industry)
            valueList_user.append(p_industry)
    for h5_selector in h5_selectors:
        h5_p_val = h5_selector.xpath('following-sibling::p[1]/text()').extract()
        h5_val = h5_selector.css('h5::text').get()
        valueList_features.append(nextLine+h5_val)
        valueList_features.append(h5_p_val)
    for h4_selector in h4_selectors:
        h4_p_val = h4_selector.xpath('following-sibling::p[1]/text()').extract()
        h4_val = h4_selector.css('h4::text').get()
        valueList_service.append(nextLine+h4_val)
        valueList_service.append(h4_p_val)
    for h3_selector in all_h3_selector:
        h3_text = h3_selector.css('h3::text').get().strip()
        h3_strong_text = h3_selector.css('strong::text').get()
        if h3_strong_text:
            h3_text=h3_text+' '+h3_strong_text
            h3_p_val = h3_selector.xpath('following-sibling::p[1]/text()').extract()
        if cnt==1:
            valueList_features.insert(0,h3_p_val)
            resultMap[h3_text] = valueList_features
        elif cnt==2:
            valueList_service.insert(0,h3_p_val)
            resultMap[h3_text] = valueList_service
        elif cnt==3:
            valueList_industry.insert(0,h3_p_val)
            resultMap[h3_text] = valueList_industry
        elif cnt==4:
            valueList_user.insert(0,h3_p_val)
            resultMap[h3_text] = valueList_user
        cnt=cnt+1
    return resultMap


def extract_data_culture(self, response):
    nextLine='\n'
    resultMap = {}
    valueList = []
    topic1 = response.css('h1::text').get()
    content1 = response.css('p::text').get().strip()
    valueList=[content1]
    for h4_selector in response.css('h4'):
        h4_selector_name = h4_selector.css('h4::text').extract()
        valueList.append(nextLine+h4_selector_name[0]);
        p_selector = h4_selector.xpath('following-sibling::p[1]/text()').extract()
        valueList.append(p_selector[0]);
    resultMap[topic1] = valueList
    topic2 = response.css('h3::text').get()
    content2 = response.css('h3+p::text').get().strip()
    valueList=[nextLine+content2]
    for h5_selector in response.css('h5'):
        h5_selector_name  = h5_selector.css('a::text').extract()
        valueList.append(nextLine+h5_selector_name[0]);
        h5_p_selector = h5_selector.xpath('following-sibling::p[1]/text()').extract()
        valueList.append(h5_p_selector[0]);
        resultMap[topic2] = valueList
    return resultMap
    
def extract_data_aboutUs(self, response):
    nextLine='\n'
    resultMap = {}
    topic1 = response.css('h1::text').get()
    content1 = response.css('p::text').get().strip()
    valueList=[content1+nextLine]
    resultMap[topic1] = valueList
    valueList = []
    h5_selectors = []
    for h4_selector in response.css('h4'):
        h4_selector_name = h4_selector.css('h4::text').extract()
        if h4_selector_name[0] == 'Fast facts':
            for element in response.css(".card-columns"):
                content2 = element.css("::text").extract()
                h5_selectors = content2
                tempContent2=[]
                cnt=2
                for t in content2:
                    if t.strip():
                        if cnt%2==0:
                            tempContent2.append(nextLine+t.strip())
                            cnt=cnt+1
                        else:
                            tempContent2.append(t.strip())
                            cnt=cnt+1
            content2 = tempContent2
            valueList.append(content2)
            resultMap[h4_selector_name[0]] = content2
        else:
            p_selector = h4_selector.xpath('following-sibling::p[1]/strong/text()').extract()
            p_selector = [txt.strip() for txt in p_selector if txt.strip()]
            valueList = p_selector
            resultMap[h4_selector_name[0]] = valueList
        topic5 = response.css('h3::text').get()
        content5 = response.css('h3+p::text').get().strip()
        valueList = [content5]
        all_h5_selectors = response.css('h5')
        for h5_selector in all_h5_selectors:
            h5_selector_val = h5_selector.css('h5::text').extract()
            if len(h5_selector_val) > 0:
                h5_selector_val = h5_selector.css('h5::text').extract()[0]
                if h5_selector_val not in h5_selectors:
                    valueList.append(nextLine+h5_selector_val);
                    valueList.append(h5_selector.xpath('following-sibling::p[1]/text()').extract()[0].strip());
        resultMap[topic5] = valueList
    return resultMap

def extract_data_partner(self, response):
    nextLine='\n'
    resultMap = {}
    valueList = []
    valueListPara = []
    first_h4 = response.css("h4:first-of-type::text").extract_first()
    first_p = response.css("p:first-of-type::text").extract_first()
    all_h4 = response.css("h4")
    for h4 in all_h4:
        h4_text = h4.css('h4::text').get().strip()
        p_text = h4.xpath('following-sibling::p[1]/text()').extract()
        li_text_list = h4.xpath("following-sibling::ul[1]/li/text()").extract()
        if h4_text != first_h4:
            valueListPara.append(nextLine+h4_text)
        valueListPara.append(p_text)
        for li_text in li_text_list:
            valueListPara.append(li_text)
        resultMap[first_h4] = valueListPara
        h3_selectors = response.css('h3')
        for h3_selector in h3_selectors:
            valueList = []
            h3_key = h3_selector.css('::text').get()
            p = h3_selector.xpath('following-sibling::p[1]/text()').extract()
            if p:
                valueList.append(p)
            h5_selectors = response.css('div.service-block1 h5')
            if h3_key == 'Our Partner Benefits':
                for h5_selector in h5_selectors:
                    h5_first_p = h5_selector.xpath('following-sibling::p[1]/text()').extract()
                    h5_txt = h5_selector.css("a:first-of-type::text").extract_first()
                    valueList.append(nextLine+h5_txt)
                    valueList.append(h5_first_p)
                resultMap[h3_key] = valueList
            else:
                row_h5_selectors = response.css('div.row h5')
                for row_h5_selector in row_h5_selectors:
                    h5_text = row_h5_selector.css("h5::text").get()
                    h7_text = row_h5_selector.xpath('following-sibling::h7[1]/strong/text()').extract()
                    p_text = row_h5_selector.xpath('following-sibling::p[1]/text()').extract()
                    if h7_text:
                        valueList.append(nextLine+h5_text)
                        valueList.append(h7_text)
                        valueList.append(p_text)
                resultMap[h3_key] = valueList
    return resultMap
    
