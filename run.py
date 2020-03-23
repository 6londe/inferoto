import json
import requests
import time
import numpy as np
import keras
from keras import models, layers
from sklearn.model_selection import train_test_split


try:
    BASE_URL = "http://www.nlotto.co.kr/common.do?method=getLottoNumber&drwNo="
    DATA_PATH = "./data/data.json"

    with open(DATA_PATH) as json_file:
        data = json.load(json_file)

    drwNo = 1
    while True:
        if not str(drwNo) in data:
            res = requests.get(BASE_URL + str(drwNo)).json()
            if res["returnValue"] == "fail":
                print("Next drwNo: " + str(drwNo))
                break

            print("Save drwNo=" + str(drwNo) + " data..")
            data[str(drwNo)] = res
            with open(DATA_PATH, 'w') as json_file:
                json.dump(data, json_file)
            
            time.sleep(1)    
        drwNo = drwNo + 1

finally:
    print("Train with last " + str(len(data)) + " data..")

    x = []
    y = []
    for i in range(1, drwNo):
        x.append(i)
        refined = np.zeros(45)
        for drwt in range(1, 7):
            refined[int(data[str(i)]["drwtNo" + str(drwt)])-1] = 1
        refined[int(data[str(i)]["bnusNo"])-1] = 1
        y.append(refined)

    x = np.array(x)
    y = np.array(y)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size = 0.1)

    model = models.Sequential([
        layers.Dense(45, input_shape=(1,), activation='softmax'),
    ])
    model.compile(optimizer='rmsprop', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(x_train, y_train, epochs=10000, verbose=1, validation_split=0.1)
    result = model.predict([drwNo])
    print(result)
    result = result[0].tolist()

    numbers = []
    for n in range(1, 7):
        idx = result.index(max(result))
        result[idx] = -1
        numbers.append(idx+1)

    print("=== " + str(drwNo) + "st Numbers Prediction ===")
    print(numbers)