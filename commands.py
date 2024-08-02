from weather import fetch_weather

def get_weather(city: str) -> tuple:
    return fetch_weather(city)

def count_numbers(number: int) -> str:
    return ' '.join(str(i) for i in range(1, number + 1))