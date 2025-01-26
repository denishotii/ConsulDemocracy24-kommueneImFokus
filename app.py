from flask import Flask, render_template, request, send_file
import os
import pandas as pd
from datetime import datetime
import locale
from jinja2 import Environment, FileSystemLoader
from premailer import Premailer  # For inlining CSS


# Set locale to German for month names
locale.setlocale(locale.LC_TIME, "de_DE")

app = Flask(__name__)

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
        city_comments = comments_df[comments_df["City"] == city]

        # Generate the report data
        data = {
            "city": city,
            "date": datetime.now().strftime("%Y-%m-%d"),
            "summary": f"This is a summary of civic engagement in {city}.",
            "ai_insights": f"AI-generated insights about civic engagement in {city}.",
            "most_discussed_topics": get_most_discussed_topics(city_comments),
            "most_liked_comments": get_most_liked_comments(city_comments),
            "peak_hours": get_peak_hours(city_comments),
            "peak_days": get_peak_days(city_comments),
            "most_supported_proposals": get_most_supported_proposals(city_proposals),
            "most_controversial_comments": get_most_controversial_comments(city_comments),
            "wordcloud_path": f"static/{city}_wordcloud.png",  # Example path
            "active_users_plot_path": f"static/{city}_active_users.png",  # Example path
            "sentiment_plot_path": f"static/{city}_sentiment_distribution.png",  # Example path
        }

        # Render the report page with the data
        return render_template("report_template.html", data=data)

    # Render the city selection page
    return render_template("index.html", cities=CITIES)

@app.route("/download/<city>")
def download_report(city):
    # Ensure the file path includes the .html extension
    html_file_path = f"templates/{city}_report.html"
    return send_file(html_file_path, as_attachment=True)

# Helper functions to generate statistics
def get_most_discussed_topics(comments_df):
    # Example: Extract most frequent words from comments
    from collections import Counter
    import re

    words = " ".join(comments_df["Text"].dropna()).lower()
    words = re.findall(r'\b\w+\b', words)
    word_counts = Counter(words).most_common(5)
    return ", ".join([word for word, count in word_counts])

def get_most_liked_comments(comments_df):
    # Example: Find the most liked comments
    most_liked = comments_df.nlargest(3, "Total Votes")
    return most_liked[["Text", "Total Votes", "Username"]].to_dict("records")

def get_peak_hours(comments_df):
    # Parse dates with the correct format
    comments_df["Date"] = pd.to_datetime(comments_df["Date"], format="%d. %B %Y %H:%M:%S")
    comments_df["Hour"] = comments_df["Date"].dt.hour
    peak_hours = comments_df["Hour"].value_counts().idxmax()
    return f"Most comments were posted at {peak_hours}:00."

def get_peak_days(comments_df):
    # Parse dates with the correct format
    comments_df["Date"] = pd.to_datetime(comments_df["Date"], format="%d. %B %Y %H:%M:%S")
    comments_df["Day"] = comments_df["Date"].dt.day_name()
    peak_day = comments_df["Day"].value_counts().idxmax()
    return f"Most comments were posted on {peak_day}."

def get_most_supported_proposals(proposals_df):
    # Example: Find the most supported proposals
    most_supported = proposals_df.nlargest(3, "Supporters")
    return most_supported[["Title", "Supporters"]].to_dict("records")

def get_most_controversial_comments(comments_df):
    # Example: Find the most controversial comments (high dislikes)
    comments_df["Controversy"] = comments_df["Dislikes"] / comments_df["Total Votes"]
    most_controversial = comments_df.nlargest(3, "Controversy")
    return most_controversial[["Text", "Controversy", "Username", "Total Votes", "Dislikes"]].to_dict("records")

if __name__ == "__main__":
    app.run(debug=True)