import random


lowercase = [chr(i) for i in range(97, 123)]
uppercase = [chr(i) for i in range(65, 91)]
digits = [str(i) for i in range(10)]

def generate_random_string(length: int) -> str:
    characters = lowercase + uppercase + digits
    return "".join(random.choice(characters) for _ in range(length))