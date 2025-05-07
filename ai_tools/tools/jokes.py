import random

class JokesTool:
    def __init__(self):
        pass

    @staticmethod
    def get_random_joke():
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "Why don't programmers like nature? It has too many bugs.",
            "Why do we never tell secrets on a farm? Because the potatoes have eyes and the corn has ears!",
            "What do you call fake spaghetti? An impasta!",
        ]
        random_joke = random.choice(jokes)
        return {"random_joke": random_joke, "status": "success"}