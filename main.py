import requests
from bs4 import BeautifulSoup
import json
import random

def scrape_HTML(url):
    response = requests.get(url)
    html = response.content
    return BeautifulSoup(html, 'html.parser')

def extract_conversation(soup, conversation_id):
    conversations = []

    # Get the text content of the first <a> element with class "topic-title"
    soru_div = soup.find('div', {'class': 'post', 'itemprop': 'articleBody'})
    if soru_div is not None:
        soru_content = soru_div.get_text(strip=True)
        # Add the soru content to the conversations list as a "soru" message
        conversations.append({
            "from": "soru",
            "value": soru_content
        })

        # Get the text content of the first <div> element with class "post"
        cevap_div = soup.find('div', {'class': 'post', 'itemprop': 'text'})
        if cevap_div is not None:
            cevap_content = cevap_div.get_text(strip=True)
            # Add the cevap content to the conversations list as a "cevap" message
            conversations.append({
                "from": "cevap",
                "value": cevap_content
            })

    # Create a conversation JSON object with the given ID and the extracted messages
    conversation = {
        "id": conversation_id,
        "conversations": conversations
    }

    return conversation

def scrape_qa_page(page_number, page_outputs):
    print(f'scraping page number {page_number}...')
    # we are adding the random bit at the end to prevent cached response from the website
    url = f'https://sorucevap.com/?page={page_number}&random={random.randint(0, 100000)}'
    page_soup = scrape_HTML(url)
    # Find all <tr> elements with class "topic-list-item"
    trs = page_soup.find_all('tr', class_='topic-list-item')

    # Loop through the <tr> elements and call the extract_conversation method with the desired URL
    for tr in trs:
        # Find the <a> tag with class "title raw-link raw-topic-link"
        a_tag = tr.find('a', class_='title raw-link raw-topic-link')
        if a_tag:
            # Check if the span with title "gönderiler" has a number greater than 0
            span_tag = tr.find('span', title='gönderiler')
            if span_tag and int(span_tag.text) > 0:
                question_url = a_tag['href']
                print(question_url)
                conversation_id = question_url.split('/')[-1]
                conversation = extract_conversation(scrape_HTML(question_url), conversation_id)
                page_outputs.append(conversation)

def scrape_all_until(last_page):
    all_outputs = []
    for page_number in range(last_page):
        scrape_qa_page(page_number + 1, all_outputs)
    return all_outputs

while True:
    try:
        number_of_pages = int(input("Kaç sayfalık soru-cevap çekmek istersiniz: "))
        if number_of_pages <= 0 or number_of_pages > 19:
            raise ValueError
        break
    except ValueError:
        print("Lütfen geçerli bir sayı girin (0 < sayfa sayısı < 20)")

outputs = scrape_all_until(number_of_pages)

# Write the output conversations to a JSON file
with open('output.json', 'w', encoding='utf-8') as f:
    json.dump(outputs, f, ensure_ascii=False, indent=4)
