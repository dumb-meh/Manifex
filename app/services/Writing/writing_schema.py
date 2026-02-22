from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class TopicEnum(str, Enum):
    SPORTS = "Sports"
    DANCE = "Dance"
    COOKING = "Cooking"
    FOOD = "Food"
    NATURE = "Nature"
    ART = "Art"
    MUSIC = "Music"
    TRAVEL = "Travel"
    SCIENCE = "Science"
    MOVIES = "Movies"
    MEDITATION = "Meditation"
    GAMING = "Gaming"
    ANIMALS = "Animals"
    # Additional child-friendly topics (ages 2-10)
    FAMILY = "Family"
    FRIENDS = "Friends"
    TOYS = "Toys"
    PLAYGROUND = "Playground"
    SCHOOL = "School"
    COLORS = "Colors"
    SHAPES = "Shapes"
    NUMBERS = "Numbers"
    LETTERS = "Letters"
    BIRTHDAY = "Birthday"
    HOLIDAYS = "Holidays"
    SEASONS = "Seasons"
    WEATHER = "Weather"
    FLOWERS = "Flowers"
    TREES = "Trees"
    BIRDS = "Birds"
    INSECTS = "Insects"
    OCEAN = "Ocean"
    SPACE = "Space"
    DINOSAURS = "Dinosaurs"
    FAIRY_TALES = "Fairy Tales"
    BOOKS = "Books"
    STORIES = "Stories"
    SUPERHEROS = "Superheroes"
    PIRATES = "Pirates"
    PRINCESSES = "Princesses"
    ROBOTS = "Robots"
    CARS = "Cars"
    TRAINS = "Trains"
    AIRPLANES = "Airplanes"
    BOATS = "Boats"
    BIKES = "Bikes"
    PETS = "Pets"
    FARM = "Farm"
    ZOO = "Zoo"
    JUNGLE = "Jungle"
    FOREST = "Forest"
    BEACH = "Beach"
    PARK = "Park"
    HOME = "Home"
    BEDROOM = "Bedroom"
    KITCHEN = "Kitchen"
    GARDEN = "Garden"
    CLOTHES = "Clothes"
    SHOES = "Shoes"
    HATS = "Hats"
    FRUITS = "Fruits"
    VEGETABLES = "Vegetables"
    SNACKS = "Snacks"
    DRINKS = "Drinks"
    ICE_CREAM = "Ice Cream"
    CANDY = "Candy"
    CAKE = "Cake"
    COOKIES = "Cookies"
    GAMES = "Games"
    PUZZLES = "Puzzles"
    DRAWING = "Drawing"
    PAINTING = "Painting"
    SINGING = "Singing"
    DANCING = "Dancing"
    RUNNING = "Running"
    JUMPING = "Jumping"
    SWIMMING = "Swimming"
    CLIMBING = "Climbing"
    MAGIC = "Magic"
    CIRCUS = "Circus"
    CLOWNS = "Clowns"
    BALLOONS = "Balloons"
    BUBBLES = "Bubbles"
    RAINBOWS = "Rainbows"
    STARS = "Stars"
    MOON = "Moon"
    SUN = "Sun"

class TopicRequest(BaseModel):
    topic: Optional[TopicEnum] = None  # If None, a random topic will be selected
    age:str

class InitialTopicResponse(BaseModel):
    topic: str
    related_words: List[str]


class FinalScoreRequest(BaseModel):
    topic: str
    related_words: List[str]
    user_paragraph: str

class FinalScoreResponse(BaseModel):
    sentence_score: int  # Score out of 10 for overall writing quality
    motivation: str  # Motivational message and feedback

class CategoryResponse(BaseModel):
    categories: List[str]  # List of 5 available topic categories