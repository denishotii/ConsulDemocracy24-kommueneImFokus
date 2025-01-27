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
    # Generate the report data for the selected city
    city_projects = projects_df[projects_df["City"] == city]
    city_proposals = proposals_df[proposals_df["City"] == city]
    city_comments = comments_df[comments_df["City"] == city]

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
def get_most_discussed_topics(comments_df):
    try:
        # Check if the DataFrame is empty or has no "Text" column
        if comments_df.empty or "Text" not in comments_df.columns:
            return "Not enough data available yet. Metrics will appear as more users become active."

        from collections import Counter
        import re

        words = " ".join(comments_df["Text"].dropna()).lower()
        words = re.findall(r'\b\w+\b', words)

        # Check if there are any words
        if not words:
            return "No topics available for analysis."

        word_counts = Counter(words).most_common(5)
        return ", ".join([word for word, count in word_counts])
    except Exception as e:
        return f"An error occurred while calculating most discussed topics: {str(e)}"

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
        # Check if the DataFrame is empty or has no "Date" column
        if comments_df.empty or "Date" not in comments_df.columns:
            return "Not enough data available yet. Metrics will appear as more users become active."

        # Parse dates with the correct format
        comments_df["Date"] = pd.to_datetime(comments_df["Date"], format="%d. %B %Y %H:%M:%S")
        comments_df["Hour"] = comments_df["Date"].dt.hour

        # Check if there are any valid hours
        if comments_df["Hour"].empty:
            return "No valid time data available."

        peak_hours = comments_df["Hour"].value_counts().idxmax()
        return f"Most comments were posted at {peak_hours}:00."
    except Exception as e:
        return f"An error occurred while calculating peak hours: {str(e)}"

def get_peak_days(comments_df):
    try:
        # Check if the DataFrame is empty or has no "Date" column
        if comments_df.empty or "Date" not in comments_df.columns:
            return "Not enough data available yet. Metrics will appear as more users become active."

        # Parse dates with the correct format
        comments_df["Date"] = pd.to_datetime(comments_df["Date"], format="%d. %B %Y %H:%M:%S")
        comments_df["Day"] = comments_df["Date"].dt.day_name()

        # Check if there are any valid days
        if comments_df["Day"].empty:
            return "No valid day data available."

        peak_day = comments_df["Day"].value_counts().idxmax()
        return f"Most comments were posted on {peak_day}."
    except Exception as e:
        return f"An error occurred while calculating peak days: {str(e)}"

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
        return [{"Title": f"An error occurred: {str(e)}", "Supporters": 0, "URL": "#"}]

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

if __name__ == "__main__":
    app.run(debug=True)