from PIL import Image
from io import BytesIO
import base64
import numpy as np
import tensorflow as tf
from tensorflow import keras

class_names = ['nd', 'nuvoloso']
model = tf.keras.models.load_model("./demo/model_image")

def evaluate_image(image_string):
    image = Image.open(BytesIO(base64.b64decode(image_string)))
    image_array = tf.keras.utils.img_to_array(image)
    image_array = tf.expand_dims(image_array, axis=0)
    image_array = image_array[...,:3] # remove alpha channel
    if(image_array.shape != (390, 720, 3)):
           image_array = tf.image.resize(image_array, (390, 720))
    image_array = image_array / 255.0
    prediction = model.predict(image_array)
    score = tf.nn.softmax(prediction[0])
    print(
      "This image most likely belongs to {} with a {:.2f} percent confidence."
      .format(class_names[np.argmax(score)], 100 * np.max(score))
    )
    return class_names[np.argmax(score)]
