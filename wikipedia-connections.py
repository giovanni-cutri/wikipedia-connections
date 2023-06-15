import bs4
import csv
import requests
import sys
import urllib.parse
import validators

from util import Node, StackFrontier, QueueFrontier


def main():

    language_code = get_language_code(input("Wikipedia Language: "))
    
    source = page_id_for_title(input("Title: "))
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
        if degrees == 1:
            print(f"\n{degrees} degree of separation.\n")
        else:
            print(f"\n{degrees} degrees of separation.\n")
        path = [(urllib.parse.unquote(source.split("/")[-1]).replace("_", " "), source)] + path
        for i in range(degrees + 1):
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


def get_language_code(language):
    """
    Gets the corresponding Wikipedia language code
    """

    editions = []

    with open ("data/list_of_wikipedias.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            edition = (row["Language"].lower(), row["Language (local)"].lower(), row["Wiki"])
            editions.append(edition)
    
    for edition in editions:
        if language.lower() in edition:
            language_code = edition[2]
            return language_code


def page_id_for_title(title):
    """
    Returns the page id for the title provided by the user
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


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    res = requests.get(person_id)
    soup = bs4.BeautifulSoup(res.text, "lxml")

    pages_ids = ["https://it.wikipedia.org" + page.attrs["href"] for page in soup.select("a[href^='/wiki/']") if ":" not in str(page)]  # ignore special namespaces
    pages_titles = [urllib.parse.unquote(page_id.split("/")[-1]).replace("_", " ") for page_id in pages_ids]

    neighbors = list(zip(pages_ids, pages_titles))

    return neighbors


if __name__ == "__main__":
    main()
