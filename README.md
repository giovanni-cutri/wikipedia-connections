# Wikipedia Connections
 
Find the shortest path between two [Wikipedia](https://en.wikipedia.org/) articles using the breadth-first search algorithm.

Inspired by [this](https://cs50.harvard.edu/ai/2020/projects/0/degrees/) CS50 Project.

# Usage

- Clone this repository to your local machine.
- Ensure that you have installed Python.
- Install the dependencies listed in *requirements.txt*.
  
  ````
  pip install -r requirements.txt
  ````
- Run *wikipedia_connections.py*.

You will be prompted to provide the language of the Wikipedia edition you want to use, the title of the initial article and the title of the final article.

Alternatively, you can provide the aforementioned information as three command-line arguments, like this:

````
python wikipedia_connections.py [language] [initial_article] [final_article]
````

# License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/giovanni-cutri/wikipedia-connections/blob/main/LICENSE) file for details.
