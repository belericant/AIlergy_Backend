from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import base64
from PIL import Image
import numpy as np
import mysql.connector
import keras
import os
from django.conf import settings

mydb = mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='makerecipesgreatagain',
)

mycursor = mydb.cursor()

mycursor.execute('USE RECIPE')
mydb.commit()


def classify(model_path, img):
    def get_key(dictionary, value):
        for key, val in dictionary.items():
            if val == value:
                return key
        return -1

    label_dict = {'apple_pie': 0, 'baby_back_ribs': 1, 'baklava': 2, 'beef_carpaccio': 3, 'beef_tartare': 4,
                  'beet_salad': 5, 'beignets': 6, 'bibimbap': 7, 'bread_pudding': 8, 'breakfast_burrito': 9,
                  'bruschetta': 10, 'caesar_salad': 11, 'cannoli': 12, 'caprese_salad': 13, 'carrot_cake': 14,
                  'ceviche': 15, 'cheese_plate': 16, 'cheesecake': 17, 'chicken_curry': 18, 'chicken_quesadilla': 19,
                  'chicken_wings': 20, 'chocolate_cake': 21, 'chocolate_mousse': 22, 'churros': 23, 'clam_chowder': 24,
                  'club_sandwich': 25, 'crab_cakes': 26, 'creme_brulee': 27, 'croque_madame': 28, 'cup_cakes': 29,
                  'deviled_eggs': 30, 'donuts': 31, 'dumplings': 32, 'edamame': 33, 'eggs_benedict': 34,
                  'escargots': 35, 'falafel': 36, 'filet_mignon': 37, 'fish_and_chips': 38, 'foie_gras': 39,
                  'french_fries': 40, 'french_onion_soup': 41, 'french_toast': 42, 'fried_calamari': 43,
                  'fried_rice': 44, 'frozen_yogurt': 45, 'garlic_bread': 46, 'gnocchi': 47, 'greek_salad': 48,
                  'grilled_cheese_sandwich': 49, 'grilled_salmon': 50, 'guacamole': 51, 'gyoza': 52, 'hamburger': 53,
                  'hot_and_sour_soup': 54, 'hot_dog': 55, 'huevos_rancheros': 56, 'hummus': 57, 'ice_cream': 58,
                  'lasagna': 59, 'lobster_bisque': 60, 'lobster_roll_sandwich': 61, 'macaroni_and_cheese': 62,
                  'macarons': 63, 'miso_soup': 64, 'mussels': 65, 'nachos': 66, 'omelette': 67, 'onion_rings': 68,
                  'oysters': 69, 'pad_thai': 70, 'paella': 71, 'pancakes': 72, 'panna_cotta': 73, 'peking_duck': 74,
                  'pho': 75, 'pizza': 76, 'pork_chop': 77, 'poutine': 78, 'prime_rib': 79, 'pulled_pork_sandwich': 80,
                  'ramen': 81, 'ravioli': 82, 'red_velvet_cake': 83, 'risotto': 84, 'samosa': 85, 'sashimi': 86,
                  'scallops': 87, 'seaweed_salad': 88, 'shrimp_and_grits': 89, 'spaghetti_bolognese': 90,
                  'spaghetti_carbonara': 91, 'spring_rolls': 92, 'steak': 93, 'strawberry_shortcake': 94,
                  'sushi': 95, 'tacos': 96, 'takoyaki': 97, 'tiramisu': 98, 'tuna_tartare': 99, 'waffles': 100}
    label_dict_r = dict([(val, key) for key, val in label_dict.items()])

    model = keras.models.load_model(model_path)
    preds = list(model.predict(img))

    pred_dict = dict([(index, confidence) for index, confidence in enumerate(preds)])
    pred_dict = dict(sorted(pred_dict.items(), key=lambda kv: kv[1], reverse=True))

    new_list = []
    for key in pred_dict:
        new_list.append((label_dict_r[key], pred_dict[key]))  # inefficient but it's late and we gotta move!

    return dict(new_list)

import base64
import json
from django.views.decorators.csrf import csrf_exempt
import base64
import json
import io

@csrf_exempt
def requestResponse(request):
    #print >> sys.stderr, request.method
    imageData = request.POST.get('image')
    allergensData = request.POST.get('allergens')
    np_img = np.array(Image.open(base64.decodebytes(imageData))).astype(np.uint8)
    foodHits = classify('./foodnet_v2.h5', np_img)
    returnFoods = {image}
    for key, value in foodHits:
        tempDict = {}
        for allergen in allergensData:
            confidence = mycursor.fetchall('SELECT count(*) FROM ' + key + ' WHERE ingredients LIKE \"%' + allergen + '%\"')[0]/mycursor.fetchall('SELECT count(*) FROM ' + key)[0]*100
            if confidence >= 5:
                tempDict = {allergen: confidence}
        returnFoods = {key: [value*100, tempDict]}
    return JsonResponse(returnFoods)
