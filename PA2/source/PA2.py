from asyncore import write
import csv
import math

class Movie:
    def __init__(self, ID=None, title=None, genre=None, imdbid=None, tmbdid=None):
        self.ID = ID
        self.title = title
        self.genre = genre # genre:list(genre)
        self.imdbid = imdbid
        self.tmbdid = tmbdid

class User:
    def __init__(self, ID=None):
        self.ID = ID
        self.movieratings = dict() # rating:dict(mID:MovieRating())

class MovieRating:
    def __init__(self, mID=None, rating=None, tags=None):
        self.mID = mID
        self.rating = rating # rating:list(rating,timestamp)
        self.tags = tags # tag:list(tag,timestamp)

# Reads movies into dict
def read_movies():
    movies = dict()
    with open("movies.csv", "r", encoding='utf-8') as moviescsv, open("links.csv", "r", encoding='utf-8') as linkscsv:
        movie_reader, link_reader = csv.reader(moviescsv), csv.reader(linkscsv)
        next(link_reader), next(movie_reader)
        for l1,l2 in zip(movie_reader,link_reader):
            movies[l1[0]] = Movie(l1[0], l1[1], l1[2].split(sep="|"), l2[1], l2[2]) # genre is split into list
        return movies

# Important distinguishment between class MovieRating and member rating - MovieRating contains the ID, actual rating, and tags
def read_movie_ratings():
    users = dict()
    with open("ratings.csv", "r", encoding='utf-8') as movieratingscsv, open("tags.csv", "r", encoding='utf-8') as tagscsv:
        rating_reader, tag_reader = csv.reader(movieratingscsv), csv.reader(tagscsv)
        next(rating_reader), next(tag_reader)
        for l1 in rating_reader: # Reads movieratings.csv where no tags exist
            if not l1[0] in users:
                users[l1[0]] = User(l1[0])
            users[l1[0]].movieratings[l1[1]] = MovieRating(l1[1], [l1[2], l1[3]], None)
        for l1 in tag_reader:
            if not l1[0] in users: # Reads tags.csv where no ratings exist
                users[l1[0]] = User(l1[0])
            if l1[1] in users[l1[0]].movieratings: # Check if mID already exists
                if users[l1[0]].movieratings[l1[1]].tags is None: # Check if tags is empty
                    users[l1[0]].movieratings[l1[1]].tags = [l1[2], l1[3]]
                else:
                    users[l1[0]].movieratings[l1[1]].tags.append([l1[2], l1[3]])
            else:
                users[l1[0]].movieratings[l1[1]] = MovieRating(l1[1], None, [l1[2],l1[3]])
        return users

# Part a) Calculates ratings matrix with users as keys
def create_user_matrix_(users, movies):
    ratings_matrix = dict()
    for user in users:
        temp = list()
        for movie in movies:
            if movie in users[user].movieratings and users[user].movieratings[movie].rating is not None:
                temp.append(users[user].movieratings[movie].rating[0])
            else:
                temp.append(str(0))
        ratings_matrix[user] = temp
    return ratings_matrix

# Part a) Calculates rating matrix with movies as keys
def create_ratings_matrix(movies, users):
    ratings_matrix = dict()
    for movie in movies:
        temp = list()
        for user in users:
            if movie in users[user].movieratings and users[user].movieratings[movie].rating is not None:
                temp.append(users[user].movieratings[movie].rating[0])
            else:
                temp.append(str(0))
        ratings_matrix[movie] = temp
    return ratings_matrix

# sos: sum of squares
def calculate_cos_sim(l1, l2):
    top, sos1, sos2 = 0.0,0.0,0.0
    for e1,e2 in zip(l1,l2):
        fe1, fe2 = float(e1), float(e2)
        if fe1 and fe2 != 0:
            top += fe1*fe2
        sos1 += math.pow(fe1, 2)
        sos2 += math.pow(fe2, 2)
    if not sos1 or not sos2:
        return 0
    return top / math.sqrt(sos1*sos2)

# Part b) Calculates cos sim for all existing movie pairs
def calculate_pairs_cos_sim(ratings_matrix):
    similarity_matrix = dict()
    for i in range(1, len(ratings_matrix)): # -1 Because we checking i+1 (shortened because full size takes too long)
        if str(i) in ratings_matrix: # Possibility movie doesn't exist
            temp = list()
            for j in range(1, len(ratings_matrix)):
                if str(j) in ratings_matrix:
                    temp.append([str(j), calculate_cos_sim(ratings_matrix[str(i)], ratings_matrix[str(j)])])
                    similarity_matrix[str(i)] = temp
    return similarity_matrix

# Part c) Gets 5 closest similarity scores
def find_neighborhood(similarity_matrix):
    nearest_neighbors = dict()
    for movie1 in similarity_matrix:
        maxs = [[0,0],[0,0],[0,0],[0,0],[0,0]]
        banned_indexs = []
        for movie2 in similarity_matrix[movie1]:
            for i in range(len(maxs)):
                if movie2[1] > maxs[i][1] and movie2[0] not in banned_indexs and movie2[1] != 1:
                    banned_indexs.append(movie2[0])
                    maxs[i] = movie2
        nearest_neighbors[movie1] = maxs
    return nearest_neighbors

# Part d) Uses the 5 nearest neighbors of a movie to predict users rating.
def estimate_ratings(users, similarity_matrix):
    estimated = dict()
    for user in users:
        list_of_movies = list()
        for rating in users[user].movieratings:
            temp = dict()
            adjusted = list()
            for movie in similarity_matrix[rating]:
                adjusted.append([movie[0], movie[1] * float(users[user].movieratings[rating].rating[0])])
            temp[rating] = adjusted
            list_of_movies.append(temp[rating])
        estimated[user] = list_of_movies
    return estimated

# Part e) gets recommend from estimated list
def get_recommended(estimated):
    recommended = dict()
    for user in estimated:
        if len(estimated[user][movie]) < 5:
            for movie in estimated[user]:
                recommended[user] = estimated[user][movie][0]
    return recommended

def write_file(output, estimated):
    with open(output, "w") as outfile:
        for user in estimated:
            outfile.write("User " + str(user) + ":  ")
            for movie_score in estimated[user]:
                outfile.write(str(movie_score[1]) + ",")
            outfile.write('\n')

def main():
    movies, users = read_movies(), read_movie_ratings()
    ratings_matrix = create_ratings_matrix(movies, users)
    similarity_matrix = calculate_pairs_cos_sim(ratings_matrix)
    neighborhood_set = find_neighborhood(similarity_matrix)
    estimated = estimate_ratings(users, similarity_matrix)
    write_file("output.txt", estimated)

if __name__ == "__main__":
    main()