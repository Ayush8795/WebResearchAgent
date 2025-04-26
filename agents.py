import requests
import json
import os
import datetime
from utils import llmCaller as call
from utils import json_parser as jp
from bs4 import BeautifulSoup

from dotenv import load_dotenv
import hashlib

load_dotenv()

google_api_key = os.getenv('GOOGLE_API_KEY')
search_engine_id = os.getenv('SEARCH_ENGINE_ID')


class SearchAgent:
    '''
    This class is responsible for searching the web using Google Custom Search API.
    '''
    def __init__(self):
        self.api_key = google_api_key
        self.search_engine_id = search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, query):
        today_date = datetime.datetime.now()
        date_2_monthsAgo = today_date - datetime.timedelta(days = 60)
        today_date_str = today_date.strftime("%Y-%m-%d")
        date_2_monthsAgo_str = date_2_monthsAgo.strftime("%Y-%m-%d")

        self.params = {
            "q": query,
            "key": self.api_key,
            "cx": self.search_engine_id,
            # "searchType": "news",
            "dateRestrict": f"{today_date_str}:{date_2_monthsAgo_str}"
        }

        response = requests.get(self.base_url, params = self.params)

        if response.status_code == 200:
            results = response.json()
            items = results.get('items', [])

            search_results = []
            for item in items:
                search_result = {
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet")
                }
                search_results.append(search_result)
            
            return search_results
        
        else:
            return None


class SearchResultParser:
    '''
    This class is responsible for parsing the search results and extracting relevant links out of all gathered links.
    '''
    def __init__(self, search_results):
        self.search_results = search_results

    def extract_links(self, query):
        web_response = ""
        for i,result in enumerate(self.search_results):
            web_response += f"{i + 1} :-> " f"Title: {result['title']}\n"
            web_response += f"Link: {result['link']}\n"
            web_response += f"Snippet: {result['snippet']}\n\n"

        prompt = f"""
        Consider you are a person who is searching web about some topic.
        You have entered the following search query: {query}

        You got the following search results:
        {web_response}

        By carefully analysing the search results and search query provide the list of relevant links to find the required information.
        Give your output in the following JSON format:
        {{
            "links": [
                {{
                    "responseNum": <1, 2, 3 which ever is the relevant link from the provided search results>,
                    "link": "<link of the relevant search result>",
                    "title": "<title of the relevant search result>"
                }},
                ...
            ]
        }}

        """
        response = call.callLLama(prompt)
        resp = jp.parse_json_response(response)

        if not resp:
            return None
        
        return resp['links']


class WebCrawler:
    '''
    This class is responsible for crawling the web pages and extracting the content from them.'''
    def __init__(self, link_results):
        self.link_results = link_results
    
    def extract_webpage_content(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers = headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else "No title found"
            
            for script_or_style in soup(['script', 'style', 'head', 'header', 'footer', 'nav']):
                script_or_style.decompose()
            
            text = soup.get_text(separator = '\n', strip = True)
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            text_content = '\n'.join(lines)
            
            return {
                "success": True,
                "title": title,
                "text": text_content
            }
        
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "title": "Error",
                "text": f"An error occurred while fetching the webpage: {str(e)}"
            }
        
        except Exception as e:
            return {
                "success": False,
                "title": "Error",
                "text": f"An unexpected error occurred: {str(e)}"
            }
    

    def crawl_links(self):
        crawled_data = []
        for link in self.link_results:
            response = self.extract_webpage_content(link['link'])
            if response['success']:
                crawled_data.append({
                    "responseNum": link['responseNum'],
                    "link": link['link'],
                    "title": link['title'],
                    "webpage_title": response['title'],
                    "webpage_text": response['text']
                })
        
        return crawled_data


class InformationExtractor:
    '''
    This class is responsible for extracting information from the crawled data.
    Merge different sources information into a single logical information.
    '''
    def __init__(self, query, crawled_data):
        self.crawled_data = crawled_data
        self.query = query
    
    def extract_information(self, article):
        prompt = f"""
        Consider you are reviewing an article to fulfill a search query.
        You will be provided with the article content and the search query.
        You have to extract the relevant information in points from the article 
        content to fulfill the requirements of search query.

        Search for:
        - important information.
        - important dates.
        - important people.
        - important events.
        - metrics
        - impact
        - statistics
        - trends

        The search query is:
        {self.query}

        Now review and extract information from the following article content:
        {article}

        Give your output in the following JSON format:
        {{
            "information": [<list of extracted important information>]
        }}
        """
        response = call.callLLama(prompt)
        resp = jp.parse_json_response(response)

        if not resp:
            return None
        
        return resp['information']
    
    def compare_and_merge_informations(self, info_list1, info_list2):
        if not info_list1:
            return info_list2
        
        if type(info_list1) != list or type(info_list2) != list:
            list1_str = str(info_list1)
            list2_str = str(info_list2)
        
        list1_str = " \n".join(info_list1)
        list2_str = " \n".join(info_list2)

        prompt = f"""
        You are provided with two lists of information and a search query.
        You have to compare the two lists and merge them into a single list.

        - Merge the list incorporating the useful information relevant to the search query from both lists.
        - Remove any duplicates and irrelevant information.
        - Ensure the merged list is concise and relevant to the search query.

        The search query is:
        {self.query}

        The first list of information is:
        {list1_str}

        The second list of information is:
        {list2_str}
        
        Give your output in the following JSON format:
        {{
            "information": [<list of merged information>]
        }}
        """
        response = call.callLLama(prompt)
        resp = jp.parse_json_response(response)
        
        if not resp:
            return None
        
        return resp['information']
    
    def extract_and_summarize(self):
        all_extracted_info = []

        for data in self.crawled_data:
            extracted_info = self.extract_information(data['webpage_text'])
            dic = self.compare_and_merge_informations(all_extracted_info, extracted_info)
            if dic:
                all_extracted_info += dic
        
        return all_extracted_info
    
def _store_in_cache(query, crawled_data, extracted_info):
    os.makedirs("cache", exist_ok = True)
    query_hash = hashlib.sha256(query.lower().encode()).hexdigest()
    cache_entry = {
        "query": query,
        "query_hash": query_hash,
        "crawled_data": crawled_data,
        "extracted_info": extracted_info
    }
    with open(f"cache/{query_hash}.json", "w") as f:
        json.dump(cache_entry, f, indent = 4)


def _check_cache(query):
    os.makedirs("cache", exist_ok = True)
    query_hash = hashlib.sha256(query.lower().encode()).hexdigest()
    cache_file_path = f"cache/{query_hash}.json"
    
    if os.path.exists(cache_file_path):
        with open(cache_file_path, "r") as f:
            cache_entry = json.load(f)
            return cache_entry
    
    return None


def run_agents(query):
    '''
    function to initiate and run the agents.
    It will first check the cache for the query and if not found, it will search the web for the query.
    It will then parse the search results and crawl the relevant links.
    '''
    
    resp = _check_cache(query)
    if resp:
        return resp['extracted_info']
    
    #search web for query
    print("Searching web for query...")
    search_agent = SearchAgent()
    search_results = search_agent.search(query)

    if not search_results:
        return None

    #Parsing the search results
    print("Parsing the results...")
    search_result_parser = SearchResultParser(search_results)
    parsed_links = search_result_parser.extract_links(query)

    if not parsed_links:
        parsed_links = search_results

    ## Crawling the parsed links
    print("Scraping the web...")
    web_crawler = WebCrawler(parsed_links)
    crawled_data = web_crawler.crawl_links()

    if not crawled_data:
        return None

    ## Extracting information from the crawled data
    print("Extracting information...")
    information_extractor = InformationExtractor(query, crawled_data)
    extracted_info = information_extractor.extract_and_summarize()

    _store_in_cache(query, crawled_data, extracted_info)

    return extracted_info


