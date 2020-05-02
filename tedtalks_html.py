"""
This Flask app serves a collection of web pages that allows users to browse
a database of TED Talks in several ways.
"""


from flask import Flask, g, render_template, request
import os
from tedtalk_db import TedTalkDatabase


app = Flask(__name__)

app.config['DATABASE'] = os.path.join(app.root_path, 'tedtalks.sqlite')


def get_db():
    """
    Returns a TedTalkDatabase instance for accessing the database.
    If the database
    file does not yet exist, it creates a new database.
    """

    if not hasattr(g, 'tedtalks_db'):
        g.tedtalks_db = TedTalkDatabase(app.config['DATABASE'])

    return g.tedtalks_db


@app.route('/speeches')
def get_all_speeches():
    """
    Gets a list of all speeches and serves a page
    which shows all speeches and relevant information.
    """

    speeches = get_db().get_all_speeches()

    return render_template('speeches.html', speeches=speeches)


@app.route('/speeches/<speech_id>')
def get_speech_by_id(speech_id):
    """
    Gets a dict representation of a speech with the given id and
    serves a page which shows relevant information about the speech.
    :param speech_id: id of the speech
    """
    speech = get_db().get_speech_by_id(speech_id)
    if speech is not None:
        reviews = get_db().get_reviews_by_speech(speech_id)
        if reviews is not []:
            speech['reviews'] = reviews
        return render_template('speech_by_id.html', speech=speech)
    else:
        return render_template('404.html', title='404'), 404


@app.route('/speeches/<speech_id>/add_review', methods = ['GET', 'POST'])
def add_review(speech_id):
    """
    Add a review to a speech with a given speech_id and
    serves a page which displays whether the addition succeeds.
    :param speech_id: id of the speech
    """
    speech = get_db().get_speech_by_id(speech_id)

    display_notice = False
    successful_add = None
    notice_text = None

    # If names were submitted then 'first_name' and 'last_name' will be keys
    # in the request.form dictionary, because those are the "name" attributes
    # of the form fields
    if 'review_content' in request.form:
        display_notice = True

        # strip() removes whitespace from either side of a string
        review_content = request.form['review_content'].strip()

        max_length = 400

        if review_content == '':
            successful_add = False
            notice_text = 'You must enter the review content.'
        elif len(review_content) > max_length:
            successful_add = False
            notice_text = 'Reviews must not be longer than 400 characters'
        else:
            successful_add = True
            get_db().insert_review(review_content, speech_id)
            notice_text = 'Review added successfully!'

    return render_template('add_review.html', display_notice=display_notice,
                           successful_add=successful_add,
                           notice_text=notice_text,
                           speech=speech)


@app.route('/topics')
def get_all_topics():
    """
    Gets a list of all topics and serves a page
    which shows all topics and relevant information.
    """

    topics = get_db().get_all_topics()

    return render_template('topics.html', topics=topics)


@app.route('/topics/<topic_id>')
def get_topic_by_id(topic_id):
    """
    Gets a dict representation of a topic with the given id and
    serves a page which shows relevant information about the topic.

    :param topic_id: id of the topic
    """

    topic = get_db().get_topic_by_id(topic_id)
    if topic is not None:
        speeches = get_db().get_speeches_by_topic(topic_id)
        if speeches is not []:
            topic['speeches'] = speeches

        return render_template('topic_by_id.html', topic=topic)
    else:
        return render_template('404.html', title='404'), 404


@app.route('/speakers')
def get_all_speakers():
    """
    Gets a list of all speakers and serves a page
    which shows all speakers and relevant information.
    """

    speakers = get_db().get_all_speakers()

    return render_template('speakers.html', speakers=speakers)


@app.route('/speakers/<speaker_id>')
def get_speaker_by_id(speaker_id):
    """
    Gets a dict representation of a speaker with the given id and
    serves a page which shows relevant information about the speaker.

    :param speaker_id: id of the topic
    """

    speaker = get_db().get_speaker_by_id(speaker_id)
    if speaker is not None:
        speeches = get_db().get_speeches_by_speaker(speaker_id)
        if speeches is not []:
            speaker['speeches'] = speeches

        return render_template('speaker_by_id.html', speaker=speaker)
    else:
        return render_template('404.html', title='404'), 404


if __name__ == '__main__':
    app.run(debug=True)
