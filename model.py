import csv
import numpy as np
from sklearn.model_selection import train_test_split
from keras.models import Sequential, load_model
from keras.layers import Flatten, Dense, Conv2D, Dropout, Lambda, Cropping2D
from keras.callbacks import EarlyStopping
import os
from PIL import Image

# Set which parts of code to run
runModel = False
runTest = False

# Steering correction for the left and right camera angles, so they are perceived as center angles
steerCorrect = 0.2

# Mute output of tensorflow GPU info (makes output cleaner)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# The amount of epochs allowed without any improvement to val_loss
validationStop = 2

lines = []

# Read in csv data
with open('Training Data/driving_log.csv') as csvfile:
    read = csv.reader(csvfile)
    for line in read:
        lines.append(line)

images = []
steeringAng = []

for line in lines:
    # Read in center steering angles
    center = float(line[3])

    # Create left and right steering angles based on the center and steering correction value set above
    steerLeft = center + steerCorrect
    steerRight = center - steerCorrect

    # Read in images as arrays
    direct = 'Training Data/'
    imgCenter = np.asarray(Image.open(direct + line[0]))
    imgLeft = np.asarray(Image.open(direct + line[1].strip(" ")))
    imgRight = np.asarray(Image.open(direct + line[2].strip(" ")))

    # Append images and steering angles to two master lists
    images.append(imgCenter)
    images.append(imgLeft)
    images.append(imgRight)
    steeringAng.append(center)
    steeringAng.append(steerLeft)
    steeringAng.append(steerRight)


# Convert lists into arrays and assign them to training labels
X_train = np.array(images)
Y_train = np.array(steeringAng)


# Create test set with 20% of the data
X_train, X_test, Y_train, Y_test = train_test_split(X_train, Y_train, test_size=0.2, random_state=1)


# Print off data set characteristics:
xtrSize = len(X_train)
xteSize = len(X_test)

print("Number of training examples: ", round(xtrSize * 0.8))
print("Number of validation examples: ", round(xtrSize * 0.2))
print("Number of testing examples: ", xteSize)


# Define early stopping procedure when validation loss is not improving
early_stop = EarlyStopping(monitor='val_loss', patience=validationStop)

# Original image shape (160,320,3)
if runModel:
    # Model Arc - NVIDIA with dropout to reduce overfitting
    model = Sequential()
    model.add(Lambda(lambda x: x/255.0 - 0.5, input_shape=(160, 320, 3)))
    model.add(Cropping2D(cropping=((70, 25), (0, 0))))
    model.add(Conv2D(24, 5, 5, subsample=(2, 2), activation="relu"))
    model.add(Conv2D(36, 5, 5, subsample=(2, 2), activation="relu"))
    model.add(Conv2D(48, 5, 5, subsample=(2, 2), activation="relu"))
    model.add(Conv2D(64, 3, 3, activation="relu"))
    model.add(Conv2D(64, 3, 3, activation="relu"))
    model.add(Flatten())
    model.add(Dense(100))
    model.add(Dropout(0.25))
    model.add(Dense(50))
    model.add(Dropout(0.25))
    model.add(Dense(10))
    model.add(Dropout(0.25))
    model.add(Dense(1))

    # Select compiler paramaters
    model.compile(loss='mse', optimizer='adam')

    # Train model
    model.fit(X_train, Y_train, validation_split=0.2, shuffle=True, nb_epoch=10, verbose=2, callbacks=[early_stop])

    # Save model
    model.save('model.h5')
    print("Saved Model")

# Curiosity
if runTest:
    model = load_model('model.h5')
    evaluate = model.evaluate(X_test, Y_test)
    print(evaluate*100)



