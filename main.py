import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

movies = pd.read_csv("ml-latest-small/movies.csv")
ratings = pd.read_csv("ml-latest-small/ratings.csv")

# create user-movie rating matrix
user_movie_matrix = ratings.pivot_table(index='userId', columns='movieId', values='rating')

print("\nUser-Movie rating matrix:")
print(user_movie_matrix.head())
# جایگزینی NaN با 0 برای محاسبه شباهت
user_movie_matrix_filled = user_movie_matrix.fillna(0)

# محاسبه ماتریس شباهت کسینوسی بین کاربران
user_similarity = cosine_similarity(user_movie_matrix_filled)

# تبدیل به DataFrame با اندیس userId
user_similarity_df = pd.DataFrame(user_similarity, index=user_movie_matrix.index, columns=user_movie_matrix.index)

print("\nUser similarity matrix (Cosine Similarity):")
print(user_similarity_df.head())
def recommend_movies(user_id, user_similarity_df, user_movie_matrix, movies, top_n=5):
    # کاربران مشابه به user_id را پیدا کن (به جز خودش)
    similar_users = user_similarity_df[user_id].drop(labels=[user_id]).sort_values(ascending=False)
    
    # ۵ کاربر برتر شبیه را انتخاب کن
    top_users = similar_users.head(top_n).index
    
    # فیلم‌هایی که این کاربران دیده‌اند ولی user_id ندیده
    user_movies = user_movie_matrix.loc[user_id].dropna().index
    movies_to_recommend = user_movie_matrix.loc[top_users].drop(columns=user_movies, errors='ignore')
    
    # میانگین امتیاز فیلم‌ها توسط کاربران مشابه
    mean_ratings = movies_to_recommend.mean(axis=0)
    
    # فیلم‌ها را بر اساس میانگین امتیاز مرتب کن
    recommended_movies = mean_ratings.sort_values(ascending=False).head(top_n)
    
    # نام فیلم‌ها را بگیر
    recommended_titles = movies.set_index('movieId').loc[recommended_movies.index]['title']
    
    return recommended_titles

# امتحان تابع برای user_id = 1
recommendations = recommend_movies(1, user_similarity_df, user_movie_matrix, movies, top_n=5)
print("\nRecommended movies for user 1:")
print(recommendations)
