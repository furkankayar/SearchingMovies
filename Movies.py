"""
    Movies.py: Searches movies of actors and actors of movies. It reads data from csv file or it can get data from themoviedb. It can show results as graph.
"""

__author__ = "Furkan Kayar"


import csv
import json
from urllib.request import urlopen as get_data
from urllib.error import HTTPError, URLError
import re

isLibrariesOkey = False
try:  # Checking required libraries
    import networkx
    import matplotlib.pyplot as plt
    isLibrariesOkey = True
except ModuleNotFoundError:
    print("\nError : Please install \"networkx\" and \"matplotlib\" libraries to see graphs.")

actors = []  #Array keeps name and movies of actors and actresses as dictionaries.
movies = []  #Array keeps name and actors of movies as dictionaries.
APIKEY = "6b080614b119a4a88bc82be6b2eeca68" #Required key to get data from themoviedb. If it is invalid, new apikey is required.
FILENAME = "movies.csv" #Name of the input file.
results = [] #Will be written to output file.
column_names = ["Actor or Actress Name"] #Keeps the column names of csv file.
MAXFILMNUMBER = 200 #Expected maximum film number for one actor or actress.
NODECOLOR = 'r' # Colors of nodes.
EDGECOLOR = 'b' # Colors of edges.

for i in range(1, MAXFILMNUMBER):
    column_names.append("Film%d Name" % i) #Adds the film numbers to column name for the csv file

def find_movie(movie_name): #Function that searches the movie in movies array

    for movie in movies:
        if movie["movie_name"].lower().replace(" ","").replace("\t","") == movie_name.lower().replace(" ","").replace("\t",""):
            return movie #If founds returns the movie
    return None #Else returns None

def find_actor(actor_name):#Function that searches the actor in actors array

    for actor in actors:
        if actor["actor_name"].lower().replace(" ","").replace("\t","") == actor_name.lower().replace(" ","").replace("\t",""):
            return actor #If founds returns the actor
    return None #Else returns None

def read_file(file_name): #Function that reads the csv file and divides file to arrays, dictionaries and sets

    try:
        with open(file_name, "r") as file: #Opens file to read
            allDictionaries = csv.DictReader(file, fieldnames=column_names, delimiter=",", skipinitialspace=True) #Reads all rows wrt assigned column names and deletes empty spaces
            for dictionary in allDictionaries: # Turning row by row in all rows
                actor_name = str(dictionary["Actor or Actress Name"]).title().rstrip().replace("\t"," ") # Gets the name of the actor or actress
                actor_movies = set() # Creates an array to keep movies of actor that is in the current row
                for i in range(1, MAXFILMNUMBER): # Loop turns until it reaches to assigned maximum film number.
                    if dictionary["Film%d Name" % i] is not None: # Checks the movie name is None or not
                        movie_name = str(dictionary["Film%d Name" % i]).title().rstrip().replace("\t"," ") # Gets the movie name from (i+1). column
                        actor_movies.add(movie_name) # Adds the movie name to set
                        check_movie = find_movie(movie_name) # Checks the movie is created before or it is a new movie
                        if check_movie is None:
                            new_movie = { "movie_name" : movie_name, "movie_actors" : set([actor_name]) } # If it is a new movie, creates a dictionary for new movie and initializes and set to keep actors
                            movies.append(new_movie) # Adds the new dictionary to movies array
                        else:
                            check_movie["movie_actors"].add(actor_name) # If the movie is created before, adds the actor name to set of current movie
                check_actor = find_actor(actor_name)
                if check_actor is None: # Checks the actor is created or it is a new actor
                    new_actor = { "actor_name" : actor_name, "actor_movies" : actor_movies } # If it is a new actor, creates a dictionary and adds movies
                    actors.append(new_actor) # Adds new actor to actors array
                else:
                    check_actor["actor_movies"] = check_actor["actor_movies"].union(actor_movies) # If actor is crated before, adds movies to its set
    except FileNotFoundError:
        print(file_name, "is not found.\n") # If file is not found with given name, prints error


def update_file(file_name): #Function that updates the csv file with new entries

    with open(file_name, "w") as file: # Opens file to write
        for actor in actors: # Turns actor by actor in actors array
            file.write(actor["actor_name"]) # Writes the name of actor to file
            for movie in actor["actor_movies"]: # Turns movie by movie in current actors movies
                file.write(", " + movie) # Writes the movies to file
            file.write("\n") # Writes new line character to file, because current line is end


def write_output_file(file_name): # Writes performed operations and their results to output file

    with open(file_name, "w") as file: # Opens file to write
        file.write("Results\n")
        for result in results: # Turns result by result in results
            file.write(result) # Writes result to file


def list_movies_of_actor(actor_name): # Gets an actor name and prints the movies of given actor

    found_actor = find_actor(actor_name) # Searches actor in actors array
    output = "\nMovies of " + re.sub(r' {2,}', ' ', actor_name.title().replace("\t"," ")) + " are"
    if found_actor is not None: # If it founds actor
        print(output, end="", flush=True)
        for movie in found_actor["actor_movies"]: # Turns movie by movie in actor's movies
            print(",",movie, end="", flush=True) # Prints each movie
            output += ", " + movie
        output += "\n"
        print()
    results.append(output) # Adds the output to results array


def find_actors_with_acted(actor_name): #Function that takes a actor name and prints all actors acted with

    found_actor = find_actor(actor_name) # Searches the given actor in actors array
    output = "\n" + re.sub(r' {2,}', ' ', actor_name.title().replace("\t"," ")) + " acted with"
    if found_actor is not None:
        all_actors_with_acted = set() # Creates a set to keep all actors acted with
        for movie in found_actor["actor_movies"]: # Turns movie by movie in movies of given actor
            all_actors_with_acted = all_actors_with_acted.union(find_movie(movie)["movie_actors"]) # Adds all actors of movies of given actor
    all_actors_with_acted = all_actors_with_acted.symmetric_difference(set([re.sub(r' {2,}', ' ', actor_name.title().replace("\t"," "))])) # Subtracts given actor from this set
    print(output, end="", flush=True)
    if all_actors_with_acted != set(): # If set is not empty prints actors
        for actor in all_actors_with_acted:
            print(",",actor, end="", flush=True)
            output += ", " + actor
    else:   # If set is empty prints message
        print(", NOBODY", end="", flush=True)
        output += ", NOBODY"
    output += "\n"
    print()
    results.append(output) # Adds the result of this operation to results array


def list_actors_of_movie(movie_name): # Function that takes a movie name and prints the all actors of movie

    found_movie = find_movie(movie_name) # Searches the movie in movies array
    output = "\nAll actors and actresses in " + re.sub(r' {2,}', ' ', movie_name.title().replace("\t"," ")) + " are"
    print(output, end="", flush=True)
    if found_movie is not None:
        for actor in found_movie["movie_actors"]: # Turns actor by actor in given movies actors
            print(",", actor, end="", flush=True) # Prints actors
            output += ", " + actor
    output +="\n"
    print()
    results.append(output) # Adds the result of this operation to results array


def list_all_actors_in_two_movies(movie1_name, movie2_name): # Function that takes two movie and prints the all actors by using set union

    found_movie1 = find_movie(movie1_name) # Searches the first movie in movies array
    found_movie2 = find_movie(movie2_name) # Searches the second movie in movies array
    output = "\nAll actors and actresses in " + re.sub(r' {2,}', ' ', movie1_name.title().replace("\t"," ")) + " and " + re.sub(r' {2,}', ' ', movie2_name.title().replace("\t"," ")) + " are"
    print(output, end="", flush=True)
    if found_movie1 is not None and found_movie2 is not None:
        all_actors = found_movie1["movie_actors"].union(found_movie2["movie_actors"]) # Adds the all actors of two movies
        for actor in all_actors: # Turns actor by actor in set of all actors
            print(",",actor, end="", flush=True) # Prints actors
            output += ", " + actor
    output += "\n"
    print()
    results.append(output) # Adds the result of this operation to results array


def list_common_actors_in_two_movies(movie1_name, movie2_name): # Function that takes two movie and prints the common actors by using set intersection

    found_movie1 = find_movie(movie1_name) # Searches the first movie in movies array
    found_movie2 = find_movie(movie2_name) # Searches the second movie in movies array
    output = "\nCommon actors and actresses in " + re.sub(r' {2,}', ' ', movie1_name.title().replace("\t"," ")) + " and " + re.sub(r' {2,}', ' ', movie2_name.title().replace("\t"," ")) + " are"
    print(output, end="", flush=True)
    if found_movie1 is not None and found_movie2 is not None:
        all_actors = found_movie1["movie_actors"].intersection(found_movie2["movie_actors"]) # Intersects the two sets and assigns the result to another set
        if all_actors != set(): # If intersection is not empty
            for actor in all_actors: # Turns actor by actor in intersection set
                print(",",actor, end="", flush=True) # Prints actors
                output += ", " + actor
        else: # If intersection is empty
            print("\nThere is not any common actor or actress.") # Gives an message
            output += "\nThere is not any common actor or actress."
    print()
    output += "\n"
    results.append(output) # Adds the result of this operation to results array


def list_difference_actors_in_two_movies(movie1_name, movie2_name): # Function that takes two movies and prints the symmetric difference

    found_movie1 = find_movie(movie1_name) # Searches the first movie in movies array
    found_movie2 = find_movie(movie2_name) # Searches the second movie in movies array
    output = "\nAll actors and actresses in either of the movies " + re.sub(r' {2,}', ' ', movie1_name.title().replace("\t"," ")) + " and " + re.sub(r' {2,}', ' ', movie2_name.title().replace("\t"," ")) + " are"
    print(output, end="", flush=True)
    if found_movie1 is not None and found_movie2 is not None:
        all_actors = found_movie1["movie_actors"].symmetric_difference(found_movie2["movie_actors"]) # Takes the symmetric difference of two movies
        for actor in all_actors: # Turns actor by actor in set
            print(",", actor, end="", flush=True) # Prints actors
            output += ", " + actor
    print()
    output += "\n"
    results.append(output) # Adds the result of this operation to results array


def get_actors_of_movie(search_movie): # Function that takes movie and gets the actors from web, it adds the results to arrays

    try:
        search_movie = search_movie.replace(" ", "+") # Deletes empty spaces and adds plus sign
        with get_data("https://api.themoviedb.org/3/search/movie?api_key=" + APIKEY + "&query=" + search_movie) as response:
            data = json.loads(response.read()) # Loads the json file (which is like dictionary)
            movie_id = str(data["results"][0]["id"]) # Gets the id of movie
            with get_data("https://api.themoviedb.org/3/movie/" + movie_id + "/credits?api_key=" + APIKEY) as response2: # Finds the actors of the movie by using this id
                movie_data = json.loads(response2.read()) # Loads the json file
                for actor in movie_data["cast"]: # Turns in cast section of json file
                    found_actor = find_actor(actor["name"]) # Searches the actor in actors array
                    if found_actor is not None: # If finds the actor
                        found_actor["actor_movies"].add(re.sub(r' {2,}', ' ', search_movie.replace("+", " ").title())) # Adds the movie to found actor
                    else: # If it is not found
                        new_actor = { "actor_name" : actor["name"], "actor_movies" : set([re.sub(r' {2,}', ' ', search_movie.replace("+", " ").title())]) } # Creates a new actor
                        actors.append(new_actor) # Adds the new actor to actors array
                    found_movie = find_movie(search_movie.replace("+", " ").title()) # Searches the given movie in movies array
                    if found_movie is not None:
                        found_movie["movie_actors"].add(actor["name"]) # If it finds the movie, adds the actor to set of movie
                    else:
                        new_movie = { "movie_name" : search_movie.replace("+", " ").title(), "movie_actors" : set([actor["name"]]) } # If does not find the movie, creates new movie with current actor
                        movies.append(new_movie) # Adds the new movie to movies array
            update_file(FILENAME) # Updates the csv file
    except IndexError:
        print("Movie is not found in database.\n")
    except HTTPError as err:
        print("An error occurred while connecting to server:", err.code, err.msg,"\n")
    except URLError:
        print("Check your internet connection.\n")
    except UnicodeEncodeError:
        print("Unexpected characters entered.\n")


def get_movies_of_actor(search_actor): # Function that takes an actors and gets the movies of given actor from web, it adds the results to arrays

    try:
        search_actor = search_actor.replace(" ", "+") # Replaces empty spaces with plus signs
        with get_data("https://api.themoviedb.org/3/search/person?api_key=" + APIKEY + "&query=" + search_actor) as response:
            data = json.loads(response.read()) # Takes the json file for sent response
            person_id = str(data["results"][0]["id"]) # Gets the id of actor from json file
            with get_data("https://api.themoviedb.org/3/person/" + person_id + "/movie_credits?api_key=" + APIKEY) as response2: # New response to find movies with found actor id
                actor_data = json.loads(response2.read()) # Takes the new json file
                for movie in actor_data["cast"]: # Turns in movie by movie in cast section of json file
                    found_movie = find_movie(movie["title"]) # Checks the movie in movies array
                    if found_movie is not None: # If it finds the movie, it adds the new actor
                        found_movie["movie_actors"].add(re.sub(r' {2,}', ' ', search_actor.replace("+", " ").title()))
                    else: # If it is does not finds the movie, it creates new movie
                        new_movie = { "movie_name" : movie["title"], "movie_actors" : set([re.sub(r' {2,}', ' ', search_actor.replace("+", " ").title())]) }
                        movies.append(new_movie)
                    found_actor = find_actor(search_actor.replace("+", " ").title()) # Checks the given actor in actors array
                    if found_actor is not None: # If it finds the actor, adds the movie
                        found_actor["actor_movies"].add(movie["title"])
                    else: # If it does not find the actor, creates new actor
                        new_actor = { "actor_name" : search_actor.replace("+", " ").title(), "actor_movies" : set([movie["title"]]) }
                        actors.append(new_actor)
            update_file(FILENAME) # Updates csv file
    except IndexError:
        print("Actor/Actress is not found in database.\n")
    except HTTPError as err:
        print("An error occurred while connecting to server:", err.code, err.msg,"\n")
    except URLError:
        print("Check your internet connection.\n")
    except UnicodeEncodeError:
        print("Unexpected characters entered.\n")


def consoleUI(): # Function that interacts with user. It checks the inputs and calls required functions.

    while True:
        print("\no--o--o--o--o--o--o--o--o    Searching Movies   o--o--o--o--o--o--o--o--o",
              "|                                                                       |",
              "o    1. Find all movies of an actor or actress.                         o",
              "|    2. Find all actors or actresses with whom he/she has acted.        |",
              "o    3. Find all actors and actresses in a movie.                       o",
              "|    4. Find all actors and actresses in two movies.                    |",
              "o    5. Find common actors and actresses in two movies.                 o",
              "o    6. Find all actors in either of the movies but not both.           o",
              "|    7. Save results to a file.                                         |",
              "o    8. Add/Update an actor or actress from web.                        o",
              "|    9. Add/Update a movie from web.                                    |",
              "o   10. Draw graph of actors and actresses.(It may take time.)          o",
              "|   11. Draw graph of movies.(It may take time.)                        |",
              "o    0. Exit                                                            o",
              "|                                                                       |",
              "o--o--o--o--o--o--o--o--o--o--o--o--o--o--o--o--o--o--o--o--o--o--o--o--o", sep="\n")

        choice = str(input("\nEnter the choice : ")).rstrip().lstrip()

        if choice == "0":
            exit(0)
        elif choice == "1":
            actor_name = input("\nEnter the actor or actress name(-1 to exit) : ").rstrip().lstrip()
            while find_actor(actor_name) is None and actor_name != "-1":
                print(actor_name, "is not found in csv file.")
                decision = input("Do you want to see web result? Csv file will be updated.(Y/n) : ").rstrip().lstrip()
                if decision.lower() == "y":
                    get_movies_of_actor(actor_name)
                if find_actor(actor_name) is None:
                    actor_name = input("Enter the actor or actress name(-1 to exit) : ").rstrip().lstrip()
            if actor_name != "-1":
                list_movies_of_actor(actor_name)
            print()

        elif choice == "2":
            actor_name = input("\nEnter the actor or actress name(-1 to exit) : ").rstrip().lstrip()
            while find_actor(actor_name) is None and actor_name != "-1":
                print(actor_name, "is not found in csv file.")
                decision = input("Do you want to see web result? Csv file will be updated.(Y/n) : ").rstrip().lstrip()
                if decision.lower() == "y":
                    get_movies_of_actor(actor_name)
                if find_actor(actor_name) is None:
                    actor_name = input("Enter the actor or actress name(-1 to exit) : ").rstrip().lstrip()
            if actor_name != "-1":
                find_actors_with_acted(actor_name)
            print()

        elif choice == "3":
            movie_name = input("\nEnter the movie name(-1 to exit) : ").rstrip().lstrip()
            while find_movie(movie_name) is None and movie_name != "-1":
                print(movie_name, "is not found in csv file.")
                decision = input("Do you want to see web result? Csv file will be updated.(Y/n) : ").rstrip().lstrip()
                if decision.lower() == "y":
                    get_actors_of_movie(movie_name)
                if find_movie(movie_name) is None:
                    movie_name = input("Enter the movie name : ").rstrip().lstrip()
            if movie_name != "-1":
                list_actors_of_movie(movie_name)
            print()

        elif choice == "4":
            movie_name_1 = input("\nEnter the first movie name(-1 to exit) : ").rstrip().lstrip()
            while find_movie(movie_name_1) is None and movie_name_1 != "-1":
                print(movie_name_1, "is not found in csv file.")
                decision = input("Do you want to see web result? Csv file will be updated.(Y/n) : ").rstrip().lstrip()
                if decision.lower() == "y":
                    get_actors_of_movie(movie_name_1)
                if find_movie(movie_name_1) is None:
                    movie_name_1 = input("Enter the first movie name(-1 to exit) : ").rstrip().lstrip()

            if movie_name_1 != "-1":
                movie_name_2 = input("\nEnter the second movie name(-1 to exit) : ").rstrip().lstrip()
                while find_movie(movie_name_2) is None and movie_name_2 != "-1":
                    print(movie_name_2, "is not found in csv file.")
                    decision = input("Do you want to see web result? Csv file will be updated.(Y/n) : ").rstrip().lstrip()
                    if decision.lower() == "y":
                        get_actors_of_movie(movie_name_2)
                    if find_movie(movie_name_2) is None:
                        movie_name_2 = input("Enter the second movie name(-1 to exit) : ").rstrip().lstrip()

            if movie_name_1 != "-1" and movie_name_2 != "-1":
                list_all_actors_in_two_movies(movie_name_1, movie_name_2)
            print()

        elif choice == "5":
            movie_name_1 = input("\nEnter the first movie name(-1 to exit) : ").rstrip().lstrip()
            while find_movie(movie_name_1) is None and movie_name_1 != "-1":
                print(movie_name_1, "is not found in csv file.")
                decision = input("Do you want to get movie from web? Csv file will be updated.(Y/n) : ").rstrip().lstrip()
                if decision.lower() == "y":
                    get_actors_of_movie(movie_name_1)
                if find_movie(movie_name_1) is None:
                    movie_name_1 = input("Enter the first movie name(-1 to exit) : ").rstrip().lstrip()

            if movie_name_1 != "-1":
                movie_name_2 = input("\nEnter the second movie name(-1 to exit) : ").rstrip().lstrip()
                while find_movie(movie_name_2) is None and movie_name_2 != "-1":
                    print(movie_name_2, "is not found in csv file.")
                    decision = input("Do you want to get movie from web? Csv file will be updated.(Y/n) : ").rstrip().lstrip()
                    if decision.lower() == "y":
                        get_actors_of_movie(movie_name_2)
                    if find_movie(movie_name_2) is None:
                        movie_name_2 = input("Enter the second movie name(-1 to exit) : ").rstrip().lstrip()

            if movie_name_1 != "-1" and movie_name_2 != "-1":
                list_common_actors_in_two_movies(movie_name_1, movie_name_2)
            print()

        elif choice == "6":
            movie_name_1 = input("\nEnter the first movie name(-1 to exit) : ").rstrip().lstrip()
            while find_movie(movie_name_1) is None and movie_name_1 != "-1":
                print(movie_name_1, "is not found in csv file.")
                decision = input("Do you want to get movie from web? Csv file will be updated.(Y/n) : ").rstrip().lstrip()
                if decision.lower() == "y":
                    get_actors_of_movie(movie_name_1)
                if find_movie(movie_name_1) is None:
                    movie_name_1 = input("Enter the first movie name(-1 to exit) : ").rstrip().lstrip()

            if movie_name_1 != "-1":
                movie_name_2 = input("\nEnter the second movie name(-1 to exit) : ").rstrip().lstrip()
                while find_movie(movie_name_2) is None and movie_name_2 != "-1":
                    print(movie_name_2, "is not found in csv file.")
                    decision = input("Do you want to get movie from web? Csv file will be updated.(Y/n) : ").rstrip().lstrip()
                    if decision.lower() == "y":
                        get_actors_of_movie(movie_name_2)
                    if find_movie(movie_name_2) is None:
                        movie_name_2 = input("Enter the second movie name(-1 to exit) : ").rstrip().lstrip()

            if movie_name_1 != "-1" and movie_name_2 != "-1":
                list_difference_actors_in_two_movies(movie_name_1, movie_name_2)
            print()

        elif choice == "7":
            file_name = input("Enter the file name(-1 to exit) : ").lstrip().rstrip().replace("/","")
            if file_name != "-1":
                write_output_file(file_name)
                print("Results are saved to file.\n")
            else:
                print()
        elif choice == "8":
            actor_name = input("\nEnter the actor or actress name(-1 to exit) : ").rstrip().lstrip()
            if find_actor(actor_name) is not None and actor_name != "-1":
                get_movies_of_actor(actor_name)
                print("\nMovies of actor/actress are updated.\n")
            elif actor_name != "-1":
                get_movies_of_actor(actor_name)
                if find_actor(actor_name) is not None:
                    print("\nNew actor/actress is added.\n")
            else:
                print()
        elif choice == "9":
            movie_name = input("\nEnter the movie name(-1 to exit) : ").rstrip().lstrip()
            if find_movie(movie_name) is not None and movie_name != "-1":
                get_actors_of_movie(movie_name)
                print("\nActors and actresses of movie are updated.\n")
            elif movie_name != "-1":
                get_actors_of_movie(movie_name)
                if find_movie(movie_name) is not None:
                    print("\nNew movie is added.\n")
            else:
                print()
        elif choice == "10":
            print("Wait a minute...")
            draw_graph_of_actors()
        elif choice == "11":
            print("Wait a minute...")
            draw_graph_of_movies()
        else:
            print("Wrong choice.\n")

        input("Press Enter to continue...\n")

def check_common_movie(actor1_name, actor2_name): # Function that checks common movie between two actors, it will be used to create edges of nodes

    actor1_movies = find_actor(actor1_name)["actor_movies"]
    actor2_movies = find_actor(actor2_name)["actor_movies"]

    if actor1_movies.intersection(actor2_movies) != set():
        return True
    return False


def check_common_actor(movie1_name, movie2_name): # Function that checks common actor between two movies, it will be used to create edges of nodes
    movie1_actors = find_movie(movie1_name)["movie_actors"]
    movie2_actors = find_movie(movie2_name)["movie_actors"]

    if movie1_actors.intersection(movie2_actors) != set():
        return True
    return False

def draw_graph_of_actors(): # Draws the graph of actors, it adds edges if there is a common movie between two actors

    if isLibrariesOkey:
        graph = networkx.Graph()

        for actor in actors:
            graph.add_node(actor["actor_name"])
            for compare in actors:
                if actor["actor_name"] != compare["actor_name"]:
                    if check_common_movie(actor["actor_name"], compare["actor_name"]):
                        graph.add_edge(actor["actor_name"], compare["actor_name"]) # Adds an edge
        networkx.draw(graph, with_labels=True, node_color=NODECOLOR, edge_color=EDGECOLOR) # Draws the graph
        plt.show() # Shows the graph
    else:
        print("\nError : Please install \"networkx\" and \"matplotlib\" libraries to see graphs.")


def draw_graph_of_movies(): # Draws the graph of movies, it adds edges if there is a common actor betwwen two movies

    if isLibrariesOkey:
        graph = networkx.Graph()

        for movie in movies:
            graph.add_node(movie["movie_name"])
            for compare in movies:
                if movie["movie_name"] != compare["movie_name"]:
                    if check_common_actor(movie["movie_name"], compare["movie_name"]):
                        graph.add_edge(movie["movie_name"], compare["movie_name"]) # Adds an edge
        networkx.draw(graph, with_labels=True, node_color=NODECOLOR, edge_color=EDGECOLOR) # Draws the graph
        plt.show() # Shows the graph
    else:
        print("\nError : Please install \"networkx\" and \"matplotlib\" libraries to see graphs.")


def main():

    read_file(FILENAME)
    consoleUI()


main()
