from os.path import dirname #class knows what files are in curr dir, access dialog and vocab

from adapt.intent import IntentBuilder #registers new intent 
from mycroft.skills.core import MycroftSkill
from mycroft.messagebus.message import Message
from mycroft.util.log import getLogger #wrapper to log errors
from mycroft.skills import context

import yummly
import numpy as np
import pandas as pd

from yummly import Client

__author__ = "aasta"
LOGGER = getLogger(__name__)

#initialize yummly
TIMEOUT = 5.0
RETRIES = 0

client = Client(api_id = "bc03093e" , api_key = "66163b61d9724213d0a76744e93d89db", 
                timeout = TIMEOUT, retries = RETRIES)

#max rating from list of recipes
def max_rating(matches):
    mat =  matches["Rating"].idxmax()
    return client.recipe(matches.ix[mat,"ID"])

#min cooking time from list of recipes
def min_time(matches):
    mat = matches["Total Time"].idxmin()
    return client.recipe(matches.ix[mat,"ID"])

#max serving size from list of recipes
def max_servings(matches):
    mat = matches["Servings"].idxmax()
    return client.recipe(matches.ix[mat,"ID"])

#min serving size from list of recipes
def min_servings(matches):
    mat = matches["Servings"].idxmin()
    return client.recipe(matches.ix[mat,"ID"])

def get_recipes(food = "", maxResults = 10):
    
    search = client.search(food)
    match = search.matches[0]
    #recipe = client.recipe(match.id)
    
    return match
    
#    results = []
#    
#    match = (client.search(food, maxRexults = maxResults)).matches
#    
#    for m in match:
#        results.append(client.recipe(m.id))
#    
#    recipes = pd.DataFrame(columns = ["Name", "Rating", "Total Time", "Servings",
#                                      "ID"])
#    for r in results:
#        recipes = recipes.append({"Name": r.name, "Rating": r.rating, "Total Time": r.totalTimeInSeconds, 
#                                               "Servings": r.numberOfServings, "ID": r.id}, ignore_index = True)
#    return client.recipe(r.ix[0,"ID"])
   
 #   return recipes
    
def top_search(food):
    r = get_recipes(food)
    return client.recipe(r.ix[0, "ID"])

class RecipeSkill(MycroftSkill):

    #constructor
    def __init__ (self):
        super(RecipeSkill, self).__init__(name="RecipeSkill") 
        rec_name = ""

    
    def initialize(self):
        #self.register_vocabulary("RecipeKeyword", "recipe")

        keyword_intent = IntentBuilder("RecipeKeywordIntent").require("RecipeKeyword").require("FoodNames").optionally("recipe").build()
        self.register_intent(keyword_intent, self.handle_recipeKeyword)
       
        needMore_intent = IntentBuilder("FoodTypeIntent").require("FoodTypes").optionally("food_descrip").build()
        self.register_intent(needMore_intent, self.handle_needMore)
       
        no_intent = IntentBuilder("NoIntent").require("NoKeyword").build()
        self.register_intent(no_intent, self.handle_no)

        print("initialized")
        
    def handle_recipeKeyword(self, message):
        #GET FIRST SEARCH
        print("handling recKey")
        
        self.rec_name = message.data.get("recipe", None)
        self.set_context("RecipeKeyword", self.rec_name)
        #self.adds_context("RecipeKeyword")
        print("context set")
        self.speak("Searching for recipe ingredients")
        rec = get_recipes(self.rec_name)
        #RESPOND, ASK SECOND SEARCH
        #self.adds_context("RecipeKeyword")

        self.speak("Rating is" + str(rec.rating) + "Anything else?", expect_response = True)        
        
#        self.speak(str(rec.name) + " has a rating of" + str(rec.rating) + 
#        " and it takes " + str(rec.totalTime) + "to make. Anything else?", 
#        expect_response = True)     
  
        
    def handle_needMore(self, message):
        print("handling more")
        
        self.rec_name = self.rec_name + message.data.get("food_descrip", None)
        self.set_context("RecipeKeyword", self.rec_name)
        rec = get_recipes(self.rec_name)
        self.speak("rating is" + self.rec_name +"is" + str(rec.rating) + "anything else?", expect_response = True)
        
    def handle_no(self, message):
        print("handling no")
        
        self.speak("Have a good meal")
        self.remove_context("RecipeKeyword")
 
            
    def stop(self):
        pass

def create_skill():
    return RecipeSkill()

