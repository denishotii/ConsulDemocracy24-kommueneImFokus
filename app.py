from flask import Flask, render_template, request, send_file, url_for
import os
import pandas as pd
from datetime import datetime
import locale
from jinja2 import Environment, FileSystemLoader
import pdfkit

# Set locale to German for month names
locale.setlocale(locale.LC_TIME, "de_DE")

app = Flask(__name__)

# Specify the path to wkhtmltopdf
wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'  # Update this path
pdfkit_config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

# List of cities (excluding Flensburg)
CITIES = [
    "Augsburg", "Bochum", "Detmold", "Siegburg", "Wuerzburg", "Muenchen", "Jena",
    "Unterschleissheim", "Bamberg", "Pforzheim", "Kempten", "Amberg", "Linz",
    "Trier", "Stutensee"
]

# Load data
comments_df = pd.read_csv("data/all_comments.csv")
projects_df = pd.read_csv("data/all_projects.csv")
proposals_df = pd.read_csv("data/all_proposals.csv")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Get the selected city from the form
        city = request.form.get("city")

        # Filter data for the selected city
        city_projects = projects_df[projects_df["City"] == city]
        city_proposals = proposals_df[proposals_df["City"] == city]
        city_comments = comments_df[comments_df["City"] == city].copy()

        # Generate charts
        wordcloud_path = generate_wordcloud(city_comments, city)
        active_users_plot_path = generate_active_users_plot(city_comments, city)
        sentiment_plot_path = generate_sentiment_plot(city_comments, city)

        # Generate the report data
        data = {
            "city": city,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "summary": f"This is a summary of civic engagement in {city}.",
            "ai_insights": f"Insights about civic engagement in {city}.",
            "most_discussed_topics": get_most_discussed_topics(city_comments),
            "most_liked_comments": get_most_liked_comments(city_comments),
            "peak_hours": get_peak_hours(city_comments),
            "peak_days": get_peak_days(city_comments),
            "most_supported_proposals": get_most_supported_proposals(city_proposals),
            "most_controversial_comments": get_most_controversial_comments(city_comments),
            "wordcloud_path": wordcloud_path or "static/placeholder.png",  # Fallback if no chart
            "active_users_plot_path": active_users_plot_path or "static/placeholder.png",  # Fallback if no chart
            "sentiment_plot_path": sentiment_plot_path or "static/placeholder.png",  # Fallback if no chart
        }

        # Render the report page with the data
        return render_template("report_template.html", data=data)

    # Render the city selection page
    return render_template("index.html", cities=CITIES)

@app.route("/download/<city>")
def download_report(city):
    # Filter data for the selected city
    city_projects = projects_df[projects_df["City"] == city]
    city_proposals = proposals_df[proposals_df["City"] == city]
    city_comments = comments_df[comments_df["City"] == city]

    # Generate charts
    wordcloud_path = generate_wordcloud(city_comments, city)
    active_users_plot_path = generate_active_users_plot(city_comments, city)
    sentiment_plot_path = generate_sentiment_plot(city_comments, city)

    # Generate the report data
    data = {
        "city": city,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "summary": f"This is a summary of civic engagement in {city}.",
        "ai_insights": f"Insights about civic engagement in {city}.",
        "most_discussed_topics": get_most_discussed_topics(city_comments),
        "most_liked_comments": get_most_liked_comments(city_comments),
        "total_comments": city_comments.shape[0],  # Get the number of rows (comments)
        "peak_hours": get_peak_hours(city_comments),
        "peak_days": get_peak_days(city_comments),
        "most_supported_proposals": get_most_supported_proposals(city_proposals),
        "most_controversial_comments": get_most_controversial_comments(city_comments),
        "wordcloud_path": wordcloud_path or "static/placeholder.png",  # Fallback if no chart
        "active_users_plot_path": active_users_plot_path or "static/placeholder.png",  # Fallback if no chart
        "sentiment_plot_path": sentiment_plot_path or "static/placeholder.png",  # Fallback if no chart
    }

    print("Total comments:", city_comments.shape[0])

    # Create a Jinja2 environment and pass the url_for function
    env = Environment(loader=FileSystemLoader('templates'))
    env.globals['url_for'] = url_for  # Make url_for available in the template

    # Render the HTML content
    template = env.get_template('report_template.html')
    html_out = template.render(data=data)

    # Convert HTML to PDF
    pdf_file_path = f"templates/{city}_report.pdf"
    pdfkit.from_string(html_out, pdf_file_path, configuration=pdfkit_config, options={
        'quiet': '',
        'enable-local-file-access': '',  # Allow access to local files
        'no-pdf-compression': '',  # Disable PDF compression
    })

    # Send the PDF file for download
    return send_file(pdf_file_path, as_attachment=True)

# Helper functions to generate statistics
import spacy
from collections import Counter
import itertools

# Global variable, but lazy-loaded
_spacy_model = None

def get_nlp():
    """Load spaCy model only once and reuse it."""
    global _spacy_model
    if _spacy_model is None:
        _spacy_model = spacy.load("de_core_news_sm")
    return _spacy_model

def extract_keywords(text):
    """Extract keywords while reusing a single spaCy instance."""
    if not isinstance(text, str):
        return []
    
    nlp = get_nlp()
    doc = nlp(text)
    keywords = [
        token.lemma_ for token in doc
        if token.is_alpha and not token.is_stop and token.pos_ in {"NOUN", "PROPN", "ADJ", "VERB"}
    ]
    return keywords



def extract_ngrams(keywords, n=2):
    """Generate bigrams or trigrams from extracted keywords."""
    return [" ".join(ngram) for ngram in zip(*[keywords[i:] for i in range(n)])]

def get_most_discussed_topics(comments_df, top_n=5):
    """Extract the most discussed topics from the comments."""
    try:
        if comments_df.empty or "Text" not in comments_df.columns:
            return "Not enough data available yet."

        # Ensure all values in the "Text" column are strings, replacing NaN with empty strings
        comments_df["Text"] = comments_df["Text"].fillna("").astype(str)

        # Extract keywords from all comments
        comments_df["Keywords"] = comments_df["Text"].apply(extract_keywords)

        # Flatten keyword lists
        all_keywords = list(itertools.chain.from_iterable(comments_df["Keywords"]))

        # Extract bigrams and trigrams for better topics
        bigrams = list(itertools.chain.from_iterable(comments_df["Keywords"].apply(lambda x: extract_ngrams(x, n=2))))
        trigrams = list(itertools.chain.from_iterable(comments_df["Keywords"].apply(lambda x: extract_ngrams(x, n=3))))

        # Count occurrences
        keyword_counts = Counter(all_keywords).most_common(top_n)
        bigram_counts = Counter(bigrams).most_common(top_n)
        trigram_counts = Counter(trigrams).most_common(top_n)

        # Combine single keywords, bigrams, and trigrams for diversity
        topics = [word for word, _ in keyword_counts] + [phrase for phrase, _ in bigram_counts] + [phrase for phrase, _ in trigram_counts]

        return ", ".join(topics[:top_n]) if topics else "No significant topics found."

    except Exception as e:
        return f"Error extracting discussed topics: {str(e)}"


    except Exception as e:
        return f"Error extracting discussed topics: {str(e)}"


def get_most_liked_comments(comments_df):
    try:
        # Check if the DataFrame is empty or has no "Total Votes" column
        if comments_df.empty or "Total Votes" not in comments_df.columns:
            return [{"Text": "Not enough data available yet.", "Total Votes": 0, "Username": "N/A", "URL": "#"}]

        most_liked = comments_df.nlargest(5, "Total Votes")
        return most_liked[["Text", "Total Votes", "Username", "URL"]].to_dict("records")
    except Exception as e:
        return [{"Text": f"An error occurred: {str(e)}", "Total Votes": 0, "Username": "N/A", "URL": "#"}]

def get_peak_hours(comments_df):
    try:
        if comments_df.empty or "Date" not in comments_df.columns:
            return "Not enough data available yet."

        # Try parsing with day-first and automatic format detection
        comments_df["Date"] = pd.to_datetime(comments_df["Date"], dayfirst=True, errors="coerce")

        # Drop rows where parsing failed
        comments_df = comments_df.dropna(subset=["Date"])

        comments_df["Hour"] = comments_df["Date"].dt.hour

        if comments_df["Hour"].empty:
            return "No valid time data available."

        peak_hours = comments_df["Hour"].value_counts().idxmax()
        return f"Most comments were posted at {peak_hours}:00."
    except Exception as e:
        return f"Error while calculating peak hours: {str(e)}"


def get_peak_days(comments_df):
    try:
        if comments_df.empty or "Date" not in comments_df.columns:
            return "Not enough data available yet."

        # Try parsing with day-first and automatic format detection
        comments_df["Date"] = pd.to_datetime(comments_df["Date"], dayfirst=True, errors="coerce")

        # Drop rows where parsing failed
        comments_df = comments_df.dropna(subset=["Date"])

        comments_df["Day"] = comments_df["Date"].dt.day_name()

        if comments_df["Day"].empty:
            return "No valid day data available."

        peak_day = comments_df["Day"].value_counts().idxmax()
        return f"Most comments were posted on {peak_day}."
    except Exception as e:
        return f"Error while calculating peak days: {str(e)}"


def get_most_supported_proposals(proposals_df):
    try:
        # Check if the DataFrame is empty or has no "Supporters" column
        if proposals_df.empty or "Supporters" not in proposals_df.columns:
            return [{"Title": "Not enough data available yet.", "Supporters": 0, "URL": "#"}]

        most_supported = proposals_df.nlargest(5, "Supporters")
        # Convert supporters to integers
        most_supported["Supporters"] = most_supported["Supporters"].astype(int)
        return most_supported[["Title", "Supporters", "URL"]].to_dict("records")
    except Exception as e:
        return [{"Title": "Not enough data available yet.", "Supporters": 0, "URL": "#"}]

def get_most_controversial_comments(comments_df):
    try:
        # Check if the DataFrame is empty or has no "Dislikes" or "Total Votes" columns
        if comments_df.empty or "Dislikes" not in comments_df.columns or "Total Votes" not in comments_df.columns:
            return [{"Text": "Not enough data available yet.", "Total Votes": 0, "Dislikes": 0, "Username": "N/A", "Controversy": 0, "URL": "#"}]

        comments_df["Controversy"] = comments_df["Dislikes"] / comments_df["Total Votes"]
        most_controversial = comments_df.nlargest(5, "Controversy")
        return most_controversial[["Text", "Controversy", "Username", "Total Votes", "Dislikes", "URL"]].to_dict("records")
    except Exception as e:
        return [{"Text": f"An error occurred: {str(e)}", "Total Votes": 0, "Dislikes": 0, "Username": "N/A", "Controversy": 0, "URL": "#"}]

import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for plotting (no UI)
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import numpy as np

from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

def generate_wordcloud(comments_df, city):
    """Generate a WordCloud image from meaningful keywords extracted with spaCy."""
    try:
        if comments_df.empty or "Text" not in comments_df.columns:
            return None  # No data, return None

        # Ensure all values in the "Text" column are strings, replacing NaN with empty strings
        comments_df["Text"] = comments_df["Text"].fillna("").astype(str)

        # Extract keywords from all comments
        comments_df["Keywords"] = comments_df["Text"].apply(extract_keywords)

        # Flatten keyword lists into a single text
        all_keywords_text = " ".join(itertools.chain.from_iterable(comments_df["Keywords"]))

        if not all_keywords_text.strip():  # If no meaningful words, return None
            return None

        # Generate WordCloud
        wordcloud = WordCloud(
            width=800, height=400, background_color='white', colormap="viridis"
        ).generate(all_keywords_text)

        # Save WordCloud as an image
        wordcloud_path = f"static/{city}_wordcloud.png"
        wordcloud.to_file(wordcloud_path)
        return wordcloud_path

    except Exception as e:
        print(f"Error generating word cloud: {e}")
        return None



def generate_active_users_plot(comments_df, city):
    try:
        if comments_df.empty or "Date" not in comments_df.columns:
            return None  # No data, return None

        # Try parsing with automatic format detection
        comments_df["Date"] = pd.to_datetime(comments_df["Date"], dayfirst=True, errors="coerce")

        # Drop rows where parsing failed
        comments_df = comments_df.dropna(subset=["Date"])

        if comments_df.empty:
            return None  # No valid data to plot

        comments_df["Hour"] = comments_df["Date"].dt.hour
        active_users = comments_df["Hour"].value_counts().sort_index()

        if active_users.empty:
            return None  # No valid data to plot

        plt.figure(figsize=(10, 6))
        sns.lineplot(x=active_users.index, y=active_users.values)
        plt.title("Active Users Over Time")
        plt.xlabel("Hour of the Day")
        plt.ylabel("Number of Comments")
        plt.xticks(np.arange(0, 24, 1))

        active_users_plot_path = f"static/{city}_active_users.png"
        plt.savefig(active_users_plot_path)
        plt.close()
        return active_users_plot_path
    except Exception as e:
        print(f"Error generating active users plot: {e}")
        return None


def generate_sentiment_plot(comments_df, city):
    try:
        if comments_df.empty:
            return None  # No data, return None

        sentiment_scores = np.random.normal(0, 1, len(comments_df))  # Placeholder for actual sentiment data
        if len(sentiment_scores) == 0:
            return None  # No data, return None

        plt.figure(figsize=(6, 4))
        sns.histplot(sentiment_scores, bins=20, kde=True)
        plt.title("Sentiment Distribution")
        plt.xlabel("Sentiment Score")
        plt.ylabel("Frequency")

        sentiment_plot_path = f"static/{city}_sentiment_distribution.png"
        plt.savefig(sentiment_plot_path)
        plt.close()
        return sentiment_plot_path
    except Exception as e:
        print(f"Error generating sentiment plot: {e}")
        return None




if __name__ == "__main__":
    app.run(debug=True)