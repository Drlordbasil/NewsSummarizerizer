import requests
from bs4 import BeautifulSoup
import nltk
import re
import heapq
import matplotlib.pyplot as plt


class NewsScraper:
    def __init__(self, source):
        self.source = source

    def scrape(self):
        response = requests.get(self.source)
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = soup.find_all('article')
        news_articles = []
        for article in articles:
            headline = article.find('h2').text
            content = article.find('div', class_='content').text
            news_articles.append((headline, content))
        return news_articles


class TextPreprocessor:
    def __init__(self, text):
        self.text = text

    def clean_text(self):
        cleaned_text = re.sub(r'\[[0-9]*\]', ' ', self.text)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text)
        return cleaned_text

    def tokenize_sentences(self):
        return nltk.sent_tokenize(self.text)

    def tokenize_words(self):
        return nltk.word_tokenize(self.text.lower())


class TextSummarizer:
    def __init__(self, sentences):
        self.sentences = sentences

    def calculate_sentence_scores(self, word_frequencies):
        sentence_scores = {}
        for sentence in self.sentences:
            for word in nltk.word_tokenize(sentence.lower()):
                if word in word_frequencies:
                    if len(sentence.split(' ')) < 30:
                        if sentence not in sentence_scores:
                            sentence_scores[sentence] = word_frequencies[word]
                        else:
                            sentence_scores[sentence] += word_frequencies[word]
        return sentence_scores

    def generate_summary(self, sentence_scores, num_sentences):
        summary_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
        return ' '.join(summary_sentences)


class NewsSummarizer:
    def __init__(self, source, num_sentences=3):
        self.source = source
        self.num_sentences = num_sentences

    def summarize_news(self):
        scraper = NewsScraper(self.source)
        articles = scraper.scrape()
        summarized_articles = []
        for article in articles:
            headline, content = article
            preprocessor = TextPreprocessor(content)
            cleaned_text = preprocessor.clean_text()
            sentences = preprocessor.tokenize_sentences()
            word_frequencies = {}
            for word in preprocessor.tokenize_words():
                if word not in nltk.corpus.stopwords.words('english'):
                    if word not in word_frequencies:
                        word_frequencies[word] = 1
                    else:
                        word_frequencies[word] += 1
            sentence_scores = TextSummarizer(sentences).calculate_sentence_scores(word_frequencies)
            summary = TextSummarizer(sentences).generate_summary(sentence_scores, self.num_sentences)
            summarized_articles.append((headline, summary))
        return summarized_articles


class Visualization:
    def __init__(self, summarized_articles):
        self.summarized_articles = summarized_articles

    def plot_summary_length_distribution(self):
        summary_lengths = [len(summary.split(' ')) for _, summary in self.summarized_articles]
        plt.hist(summary_lengths, bins=20, alpha=0.5)
        plt.xlabel('Summary Length')
        plt.ylabel('Frequency')
        plt.title('Summary Length Distribution')
        plt.show()

    def show_summaries(self):
        for headline, summary in self.summarized_articles:
            print('Headline:', headline)
            print('Summary:', summary)
            print('--------------------------')


def main():
    source = 'https://example.com/news'
    num_sentences = 3

    summarizer = NewsSummarizer(source, num_sentences)
    summarized_articles = summarizer.summarize_news()

    visualization = Visualization(summarized_articles)
    visualization.plot_summary_length_distribution()
    visualization.show_summaries()


if __name__ == '__main__':
    main()