import bs4
import requests
import sys
import urllib.parse
import validators

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"\n{degrees} degrees of separation.\n")
        path = [(urllib.parse.unquote(source.split("/")[-1]).replace("_", " "), source)] + path
        for count, i in enumerate(range(degrees + 1)):
            if count !=0 and count != degrees:
                print("-> ", end="")
            print(f"{path[i][0]} - {path[i][1]}")
            # print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """

    # Keep track of number of states explored
    num_explored = 0

    # Initialize frontier to just the starting position
    start = Node(state=source, parent=None, action=urllib.parse.unquote(source.split("/")[-1]).replace("_", " "))
    frontier = QueueFrontier()
    frontier.add(start)

    # Initialize an empty explored set
    explored = set()

    # Keep looping until solution found
    while True:

        # If nothing left in frontier, then no path
        if frontier.empty():
            return None

        # Choose a node from the frontier
        node = frontier.remove()
        num_explored += 1

        # Mark node as explored
        explored.add(node.state)

        # Add neighbors to frontier
        for state, title in neighbors_for_person(node.state):

            if not frontier.contains_state(state) and state not in explored:

                child = Node(state=state, parent=node, action=title)
  
                # If node is the goal, then we have a solution
                if child.state == target:
                    movies = []
                    people = []
                    while child.parent is not None:
                        movies.append(child.action)
                        people.append(child.state)
                        child = child.parent
                    movies.reverse()
                    people.reverse()
                    solution = list(zip(movies, people))
                    return solution
                
                frontier.add(child)



def person_id_for_name(title):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """

    if not validators.url(title):
        url = "https://it.wikipedia.org/wiki/" + urllib.parse.quote(title, safe='/', encoding=None, errors=None)\
            .replace("%20", "_")  # Wikipedia encodes URLS normally in its wikilinks, except
                                  # for whitespaces, which are replaced by '_'
    else:
        url = title
    
    res = requests.get(url)
    if res.status_code == 200:
        return url
    
    return None

    print(res.status_code)
    input()
    if res.status_code == 200:
        return name

    url = "https://it.wikipedia.org/wiki/" + urllib.parse.quote(name, safe='/', encoding=None, errors=None)
    print(url)
    input()
    res = requests.get(url)
    if res.status_code == 200:
        return url
    
    return None

    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    res = requests.get(person_id)
    soup = bs4.BeautifulSoup(res.text, "lxml")
    pages_ids = ["https://it.wikipedia.org" + page.attrs["href"] for page in soup.select("a[href^='/wiki/']")]
    pages_titles = [urllib.parse.unquote(page_id.split("/")[-1]).replace("_", " ") for page_id in pages_ids]

    neighbors = list(zip(pages_ids, pages_titles))

    return neighbors


if __name__ == "__main__":
    main()
