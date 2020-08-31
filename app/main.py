#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from flask import render_template
from flask import Flask, request
import json
import io
import os
import tensorflow as tf
import numpy as np
from PIL import Image
import base64
import tensorflow as tf
import tensorflow_hub as hub
from scipy.stats import truncnorm

from labels import category_labels




def img_to_base64_str( img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    buffered.seek(0)
    return "data:image/png;base64,{}".format(base64.b64encode(buffered.getvalue()).decode())



class Model():
    def __init__(self):
        self.rand_seed = 321
        self.truncation = 0.5
        module_path = 'https://tfhub.dev/deepmind/biggan-256/2'
        tf.reset_default_graph()
        module = hub.Module(module_path)
        inputs = {k: tf.placeholder(v.dtype, v.get_shape().as_list(), k) for k, v in module.get_input_info_dict().items()}
        self.output = module(inputs)

        self.input_z = inputs['z']
        self.input_y = inputs['y']

        self.input_trunc = inputs['truncation']

        self.random_state = np.random.RandomState(self.rand_seed)
        self.dim_z = self.input_z.shape.as_list()[1]
        self.vocab_size = self.input_y.shape.as_list()[1]

        initializer = tf.global_variables_initializer()
        self.sess = tf.Session()
        self.sess.run(initializer)


def truncated_z_sample():
    values = truncnorm.rvs(-2, 2, size=(1, model.dim_z), random_state=model.random_state)
    return model.truncation * values


def create_labels(genes):
    label = np.zeros((1,model.vocab_size))
    for key in genes:
        val = genes[key]
        ind = category_labels.index(key)
        label[0,ind] = val
    return label


def sample(vector, labels):
    feed_dict = {model.input_z: vector , model.input_y: labels, model.input_trunc: model.truncation}
    res = model.sess.run(model.output, feed_dict=feed_dict)
    res = np.clip(((res + 1) / 2.0) * 256, 0, 255)
    res = np.uint8(res)
    return res[0,...]


def normalize_genes(genes):
    sum_ = 0
    new_genes = {}
    sum_ = sum(genes.values())

    for key in genes:
        new_genes[key] = genes[key] / sum_

    return new_genes


def create_image(genes):
    genes = normalize_genes(genes)
    vector = truncated_z_sample()
    labels = create_labels(genes)
    im = sample(vector, labels)
    return im


app = Flask(__name__,static_url_path='/static')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html',category_labels = category_labels)


@app.route('/generate_image', methods=['POST'])
def generate_image():
    img = create_image(request.json["genes"])
    response = app.response_class(
        response=json.dumps({"encoded":img_to_base64_str(Image.fromarray(np.uint8(np.clip(img , 0, 255) )))}),
        status=201,
        mimetype='application/json'
    )
    return response


model = Model()

if __name__ == '__main__':
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'O$%7kQgXKVOhT@refsbY;mQmt9lMWg')
    port = os.getenv('PORT', 9000)
    print('port=', port)
    app.run(host='0.0.0.0', debug=True, port=port)
