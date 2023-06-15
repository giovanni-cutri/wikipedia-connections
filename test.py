# Import the unittest library and the "shortest_path" function
import unittest
from wikipedia_connections import shortest_path

# A class containing all the tests
class Tests(unittest.TestCase):

    def test_sampson_carolina(self):
        """Check path for Sampson -> Noth Carolina."""
        self.assertEqual(shortest_path("it", "https://it.wikipedia.org/wiki/Contea_di_Sampson", "https://it.wikipedia.org/wiki/Carolina_del_Nord"),
                         [('Carolina del Nord', 'https://it.wikipedia.org/wiki/Carolina_del_Nord')])

    def test_sampson_atlantic(self):
        """Check path for Sampson -> Atlantic Ocean."""
        self.assertEqual(shortest_path("it", "https://it.wikipedia.org/wiki/Contea_di_Sampson", "https://it.wikipedia.org/wiki/Oceano_Atlantico"),
                         [("Stati Uniti d'America", 'https://it.wikipedia.org/wiki/Stati_Uniti_d%27America'), ('Oceano Atlantico', 'https://it.wikipedia.org/wiki/Oceano_Atlantico')])

    def test_steven_boccaccio(self):
        """Check path for Steven Universe -> Giovanni Boccaccio."""
        self.assertEqual(shortest_path("it", "https://it.wikipedia.org/wiki/Episodi_di_Steven_Universe_(seconda_stagione)", "https://it.wikipedia.org/wiki/Giovanni_Boccaccio"),
                         [('Italia', 'https://it.wikipedia.org/wiki/Italia'), ('Giovanni Boccaccio', 'https://it.wikipedia.org/wiki/Giovanni_Boccaccio')])   


# Run each of the testing functions
if __name__ == "__main__":
    unittest.main()