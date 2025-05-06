class WeatherTools:
    def __init__(self):
        pass

    @staticmethod
    def get_weather(location):
        return {"location": location, "temperature": "25°C", "condition": "Sunny"}
