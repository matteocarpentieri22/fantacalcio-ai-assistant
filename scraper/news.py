from base import FantacalcioScraperBase

class NewsScraper(FantacalcioScraperBase):
    def __init__(self):
        super().__init__()

    def get_ultime_notizie(self):
        """
        Scarica e analizza la pagina delle news.
        Ritorna una lista di dizionari con titolo, link e data.
        """
        soup = self.fetch_page("/news", delay=(1.0, 2.0))
        if not soup:
            return []

        news_list = []
        
        # Le notizie principali sono dentro tag <article class="article-card">
        articles = soup.find_all('article', class_='article-card')
        
        for article in articles:
            n = {}
            a_tag = article.find('a', class_='inner')
            if a_tag:
                link = a_tag.get('href', '')
                if link and not link.startswith('http'):
                    link = self.base_url + link
                n['link'] = link
                
                title_tag = a_tag.find('h2', class_='title')
                if title_tag:
                    n['title'] = title_tag.text.strip()
                    
                incipit_tag = a_tag.find('p', class_='incipit')
                if incipit_tag:
                    n['abstract'] = incipit_tag.text.strip()
                    
                date_tag = a_tag.find('span', class_='date')
                if date_tag:
                    n['date'] = date_tag.text.strip()
                    
                category_tag = a_tag.find('span', class_='category')
                if category_tag:
                    n['category'] = category_tag.text.strip()
                
                if 'title' in n and 'link' in n:
                    # Fetching the content
                    article_soup = self.fetch_page(n['link'], delay=(0.5, 1.5))
                    if article_soup:
                        body = article_soup.find('div', class_='html-content') or article_soup.find('div', class_='article-body') or article_soup.find('article')
                        n['content'] = body.text.strip() if body else ''
                    else:
                        n['content'] = ''
                        
                    news_list.append(n)
        return news_list

if __name__ == "__main__":
    scraper = NewsScraper()
    notizie = scraper.get_ultime_notizie()
    import json
    print(f"Trovate {len(notizie)} notizie principali.")
    print(json.dumps(notizie[:3], indent=2, ensure_ascii=False))
