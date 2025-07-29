from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Load data once
movies = pd.read_csv('movies.csv')
ratings = pd.read_csv('ratings.csv')

# Extract year from title (e.g. "Movie Title (1995)")
movies['year'] = movies['title'].str.extract(r'\((\d{4})\)').astype(float)

# Merge ratings with movies to get genre and year info
ratings_movies = pd.merge(ratings, movies, on='movieId')

def recommend_movies(user_id, genre, min_rating, year_from, year_to):
    # Filter movies by genre and year range
    filtered_movies = movies[
        (movies['genres'].str.contains(genre, case=False, na=False)) &
        (movies['year'] >= year_from) &
        (movies['year'] <= year_to)
    ]

    # Filter ratings for those movies only with rating >= min_rating
    filtered_ratings = ratings_movies[
        (ratings_movies['movieId'].isin(filtered_movies['movieId'])) &
        (ratings_movies['rating'] >= min_rating)
    ]

    # Filter ratings by user_id
    user_ratings = filtered_ratings[filtered_ratings['userId'] == user_id]

    if user_ratings.empty:
        # If user has no ratings with these filters, recommend top rated movies overall in this filter
        top_movies = filtered_ratings.groupby(['movieId', 'title', 'year'])['rating'].mean().reset_index()
        top_movies = top_movies.sort_values(by='rating', ascending=False).head(10)
    else:
        # Recommend movies user rated highest within this filter
        top_movies = user_ratings.sort_values(by='rating', ascending=False).head(10)

    return top_movies

@app.route('/', methods=['GET', 'POST'])
def home():
    recommendations = None
    plot_path = None

    if request.method == 'POST':
        user_id = int(request.form['user_id'])
        genre = request.form['genre']
        min_rating = float(request.form['min_rating'])
        year_from = int(request.form['year_from'])
        year_to = int(request.form['year_to'])

        recommendations = recommend_movies(user_id, genre, min_rating, year_from, year_to)

        # Plot ratings bar chart
        plt.figure(figsize=(10,5))
        plt.bar(recommendations['title'], recommendations['rating'], color='skyblue')
        plt.xticks(rotation=45, ha='right')
        plt.xlabel('Movie Title')
        plt.ylabel('Rating')
        plt.title('Recommended Movies Ratings')
        plt.tight_layout()

        # Save plot to static folder
        if not os.path.exists('static'):
            os.makedirs('static')
        plot_path = 'static/plot.png'
        plt.savefig(plot_path)
        plt.close()

    return render_template('index.html', recommendations=recommendations, plot_path=plot_path)

if __name__ == '__main__':
    app.run(debug=True)
