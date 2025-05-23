import groq
import eventregistry
from transformers import pipeline, AutoTokenizer
import json
from datetime import datetime, timedelta
import os

class NewsAnalyzer:
    def __init__(self, groq_api_key, event_registry_api_key):
        self.groq_client = groq.Groq(api_key="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")
        self.er = eventregistry.EventRegistry(apiKey="c3892498-706c-443a-a9a7-b194c52887b7")
        self.tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-finetuned-sst-2-english")
        self.sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            tokenizer=self.tokenizer
        )

    def truncate_text(self, text, max_length=512):
        """Truncate text to fit within model's token limit"""
        tokens = self.tokenizer.encode(text, truncation=True, max_length=max_length)
        return self.tokenizer.decode(tokens, skip_special_tokens=True)

    def fetch_news(self):
        q = eventregistry.QueryArticlesIter(
            keywords=eventregistry.QueryItems.OR([
                "Lithium - Ion", "Batteries", "Electric Vehicles",
                "Lithium shortage", "Lithium", "Cobalt", "Mineral Mining"
            ]),
            dateStart=(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d'),
            dateEnd=datetime.now().strftime('%Y-%m-%d'),
            dataType=["news", "blog"],
            lang="eng"
        )
        
        articles = []
        for article in q.execQuery(self.er, sortBy="date", maxItems=20):  # Limit to 20 articles
            articles.append({
                "source": article.get("source", {}).get("title", ""),
                "title": article.get("title", ""),
                "body": article.get("body", ""),
                "dateTime": article.get("dateTime", "")
            })
        
        return articles

    def analyze_sentiment(self, text):
        truncated_text = self.truncate_text(text)
        result = self.sentiment_pipeline(truncated_text)[0]
        return {
            "label": result["label"],
            "score": float(result["score"])
        }

    def analyze_risk_with_llama(self, content):
        truncated_content = content[:4000]  # Limit content length for LLaMA
        prompt = f"""Analyze the following news article for lithium-ion battery supply chain risks.
        Article: {truncated_content}
        Provide a structured analysis of the identified risks and their potential impact."""

        completion = self.groq_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content

    def run_analysis(self):
        articles = self.fetch_news()
        results = []
        
        for article in articles:
            sentiment = self.analyze_sentiment(article["body"])
            risk_analysis = self.analyze_risk_with_llama(article["body"])
            
            results.append({
                "title": article["title"],
                "source": article["source"],
                "dateTime": article["dateTime"],
                "sentiment_analysis": sentiment,
                "risk_analysis": risk_analysis
            })
            
        # Save results to JSON
        os.makedirs("data", exist_ok=True)
        with open("data/analysis_results.json", "w") as f:
            json.dump(results, f, indent=4)
            
        return results 