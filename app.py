import json
import os
import random
import pandas as pd
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import pickle
from flask import Flask, request, render_template, jsonify, make_response, send_file
from werkzeug.utils import secure_filename

from face_landmarks1 import make_face_df_save, find_face_shape
from recommender import process_rec_pics, run_recommender_face_shape
from flask_cors import CORS
import sqlalchemy as sa

application = Flask(__name__, static_url_path="")

# ssl_args = {'ssl': {'ca': 'YOUR_SSL_CERT_PATH'}}
# server = "localhost"
# database = "salondb"
# db_url = 'mysql://{}@{}/{}'.format("root", server, database)
# print(db_url)
#
# engine = sa.create_engine(db_url, echo=False)
# cnx = engine.connect()


CORS(application, resources={r"/api/*": {"origins": "http://localhost"}})
df = pd.DataFrame(
    columns=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17',
             '18', '19', '20', '21', '22', '23', '24', '25', '26', '27', '28', '29',
             '30', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41',
             '42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53',
             '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64', '65',
             '66', '67', '68', '69', '70', '71', '72', '73', '74', '75', '76', '77',
             '78', '79', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89',
             '90', '91', '92', '93', '94', '95', '96', '97', '98', '99', '100', '101',
             '102', '103', '104', '105', '106', '107', '108', '109', '110', '111', '112', '113',
             '114', '115', '116', '117', '118', '119', '120', '121', '122', '123', '124', '125',
             '126', '127', '128', '129', '130', '131', '132', '133', '134', '135', '136', '137',
             '138', '139', '140', '141', '142', '143', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7', 'A8', 'A9',
             'A10', 'A11', 'A12', 'A13', 'A14', 'A15', 'A16', 'Width', 'Height', 'H_W_Ratio', 'Jaw_width', 'J_F_Ratio',
             'MJ_width', 'MJ_J_width'])


@application.route('/')
def index():
    """Return the main page."""
    return render_template('theme.html')


@application.route('/predict', methods=['GET', 'POST'])
def predict():
    """Return a random prediction."""


    person_see_up_dos = request.form.get("person_see_up_dos")
    person_hair_length = request.form.get('person_hair_length')
    image = request.files['image']

    filename = secure_filename(image.filename)
    image.save(os.path.join('data/pics/recommendation_pics/', filename))



    data = {'file_name': filename, 'person_see_up_dos': person_see_up_dos, 'person_hair_length': person_hair_length}


    # data = request.json
    test_photo = 'data/pics/recommendation_pics/' + data['file_name']
    print(data)
    file_num = 2035
    style_df = pd.DataFrame()
    style_df = pd.DataFrame(columns=['face_shape', 'hair_length', 'location', 'filename', 'score'])
    hair_length_input = 'Updo'
    updo_input = data['person_see_up_dos']
    if updo_input in ['n', 'no', 'N', 'No', 'NO']:
        hair_length_input = data['person_hair_length']
        if hair_length_input in ['short', 'Short', 's', 'S']:
            hair_length_input = 'Short'
        if hair_length_input in ['long', 'longer', 'l', 'L']:
            hair_length_input = 'Long'

    # filename = secure_filename(data['file_name'].filename)
    # data['file_name'].save(os.path.join('data/pics/recommendation_pics/', filename))

    make_face_df_save(test_photo, file_num, df)
    face_shape = find_face_shape(df, file_num)
    process_rec_pics(style_df)
    img_filename = run_recommender_face_shape(face_shape[0], style_df, hair_length_input)

    # with open(f"{img_filename}", 'rb') as f:
    #     img_data = f.read()
    #     print(type(img_data))
    #     files = [
    #         ('document', (img_filename, open(img_filename, 'rb'), 'application/octet'))
    #
    #     ]
    #     headers = {'Content-type': 'multipart/form-data'}
    #     res = requests.post("http://127.0.0.1:5001/test", files=files, headers=headers)
    #     print(res)
    files = [
        ('document', (img_filename, open(img_filename, 'rb'), 'application/octet'))

    ]
    print(files)
    headers = {'Content-type': 'multipart/form-data'}
    res = requests.post("http://salonserver-env.eba-g3vpimmh.us-east-1.elasticbeanstalk.com/test", files=files)

    d = json.loads(res.text)
    print(d['test'])

    return jsonify({'Face Shape': face_shape[0], 'img_filename': d['test']})


@application.route('/predict_user_face_shape', methods=['GET', 'POST'])
def predict_user_face_shape():
    """Return a user face shape."""
    data = request.json
    test_photo = 'data/pics/recommendation_pics/' + data['file_name']
    file_num = 2035

    make_face_df_save(test_photo, file_num, df)
    face_shape = find_face_shape(df, file_num)
    return jsonify({'face_shape': face_shape[0]})


@application.route('/output/<img_filename>')
def output_image(img_filename):
    """Send the output image."""
    with open(f"output/{img_filename}", 'rb') as f:
        img_data = f.read()
        res = requests.post("http://127.0.0.1:5000/determine_escalation", data=img_data)
    response = make_response(img_data)
    response.headers['Content-Type'] = 'image/png'
    return response

@application.route("/api/downloadfile/")
def download_file():
    path = request.args.get('path')
    print(path)
    return send_file(path, as_attachment=True)



@application.after_request
def after_request_func(response):
    origin = ''
    if request.headers.get('Origin'):
        origin = request.headers.get('Origin')

    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Headers', 'x-csrf-token')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
    else:
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Origin', origin)

    return response

if __name__ == '__main__':
    application.run(debug=True)
    # socketio.run(applicationlication, debug=True)