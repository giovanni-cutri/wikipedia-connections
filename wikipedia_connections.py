import argparse
import bs4
import csv
import lxml
import requests
import sys
import urllib.parse
import validators

from util import Node, StackFrontier, QueueFrontier


def main():

    if len(sys.argv) == 4:
        (language, initial_article, final_article) = parse_arguments()

    elif len(sys.argv) == 1:
        language = input("Wikipedia Language: ")
        initial_article = input("Title of the initial article: ")
        final_article = input("Title of the final article: ")

    else:
        sys.exit("Invalid usage.")

    language_code = get_language_code(language)
    if language_code is None:
        sys.exit("Invalid language.")
    
    base_url = f"https://{language_code}.wikipedia.org"

    source = get_page_id_for_title(initial_article, base_url)
    if source is None:
        sys.exit("Initial article not found.")
    target = get_page_id_for_title(final_article, base_url)
    if target is None:
        sys.exit("Final article not found.")

    path = shortest_path(base_url, source, target)
    
    print_result(path, source)


def shortest_path(base_url, source, target):
    """
    Returns the shortest list of articles
    that connect the source to the target.

    If no possible path, returns None.
    """

    # If source and target coincide, return empty path
    if source == target:
        return ""

    # Keep track of number of states explored
    num_explored = 0

    # Initialize frontier to just the starting position
    start = Node(state=source, parent=None, action=get_title_for_page_id(source))
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
        for state, title in neighbors_for_article(base_url, node.state):

            if not frontier.contains_state(state) and state not in explored:

                child = Node(state=state, parent=node, action=title)
  
                # If node is the goal, then we have a solution
                if child.state == target:
                    titles = []
                    ids = []
                    while child.parent is not None:
                        titles.append(child.action)
                        ids.append(child.state)
                        child = child.parent
                    titles.reverse()
                    ids.reverse()
                    solution = list(zip(titles, ids))
                    return solution
                
                frontier.add(child)


def parse_arguments():
    """
    Parses command-line arguments
    """
    
    parser = argparse.ArgumentParser()
    parser.add_argument("language", help="the language of the Wikipedia edition you want to use for the search")
    parser.add_argument("initial_article", help="the title of the article from which you want to start the search")
    parser.add_argument("final_article", help="the title of the article which must be reached")
    args = parser.parse_args()
    return (args.language, args.initial_article, args.final_article)


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
    
    return None


def get_page_id_for_title(title, base_url):
    """
    Returns the page id for the title provided by the user
    """

    if not validators.url(title):
        url = base_url + "/wiki/" + urllib.parse.quote(title, safe='/', encoding=None, errors=None)\
            .replace("%20", "_")  # Wikipedia encodes URLS normally in its wikilinks, except
                                  # for whitespaces, which are replaced by '_'
    elif ".wikipedia.org/wiki" not in title:
        sys.exit("Not a valid Wikipedia URL.")
    else:
        url = title

    res = requests.get(url)
    if res.status_code == 200:
        return url
    
    return None


def get_title_for_page_id(page_id):
    """
    Returns the title for the page id provided as a parameter
    """

    return urllib.parse.unquote(page_id.split("/")[-1]).replace("_", " ")


def neighbors_for_article(base_url, page_id):
    """
    Returns (page_id, page_title) pairs for pages
    which are connected with the article provided as a parameter.
    """
    res = requests.get(page_id)
    soup = bs4.BeautifulSoup(res.text, "lxml")
  
    pages_ids = [base_url + page.attrs["href"] for page in soup.select("a[href^='/wiki/']") if ":" not in str(page)]  # ignore special namespaces
    pages_titles = [get_title_for_page_id(page_id) for page_id in pages_ids]

    neighbors = list(zip(pages_ids, pages_titles))

    return neighbors


def print_result(path, source):
    """
    Prints the resulting path
    """

    if path is None:
        print("\nArticles are not connected.")
    elif path == "":
        print("\nThe two articles coincide.")
    else:
        degrees = len(path)
        if degrees == 1:
            print(f"\n{degrees} degree of separation.\n")
        else:
            print(f"\n{degrees} degrees of separation.\n")

        path = [(get_title_for_page_id(source), source)] + path

        for i in range(degrees + 1):
            print("-> ", end="")
            print(f"{path[i][0]} - {path[i][1]}")


if __name__ == "__main__":
    main()
