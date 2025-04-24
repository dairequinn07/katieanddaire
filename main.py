import os
from datetime import timedelta
import requests
from flask import Flask, render_template, request, make_response, redirect, session, jsonify

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)


# Step 3: Add HTTPS redirection before any request is processed
@app.before_request
def https_redirect():
    if not request.is_secure and request.headers.get('x-forwarded-proto') != 'https':
        # Redirect HTTP requests to HTTPS
        return redirect(request.url.replace('http://', 'https://', 1), code=301)


@app.after_request
def add_response_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = "0"
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=['GET'])
def hello_world():
    session.permanent = True
    response = make_response(render_template('index.html'))
    return response


@app.route('/submit-form', methods=['POST'])
def submit_form():
    data = request.get_json() # Get JSON data from the request
    names = data['names']
    attending = data['attending']
    location = data['location']
    dietary = data['dietary']
    comments = data['comments']
    myEmail = os.environ.get('myEmail')
    ccEmail = os.environ.get('ccEmail')
    api_key = os.environ.get('api_key')

    send_mail = requests.post(
        "https://api.eu.mailgun.net/v3/katieanddaire.com/messages",
        auth=("api", api_key),
        data={
            "from": "RSVP <postmaster@katieanddaire.com>",
            "to": [myEmail],
            "cc": [ccEmail],
            "subject": "Wedding RSVP",
            "html": f'''\
        <html>
            <body>
                <p>New Wedding RSVP:</p>
                <p>Name: {names}</p>
                <p>Attending: {attending}</p>
                <p>Location: {location}</p>
                <p>Dietary: {dietary}</p>
                <p>Additional Info: {comments}</p>
            </body>
        </html>
        '''
        }
    )
    if send_mail.status_code == 200:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False})


if __name__ == "__main__":
    app.run(debug=False)


