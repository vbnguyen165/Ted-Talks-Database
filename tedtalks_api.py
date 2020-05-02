"""
This Flask app implements a REST API for TedTalkDatabase.
"""


from flask import Flask, g, jsonify, request
from flask.views import MethodView
import os
from tedtalk_db import TedTalkDatabase

app = Flask(__name__)

app.config['DATABASE'] = os.path.join(app.root_path, 'tedtalks.sqlite')


def get_db():
    """
    Returns a TedTalk instance for accessing the database. If the database
    file does not yet exist, it creates a new database.
    """

    if not hasattr(g, 'tedtalks_db'):
        g.tedtalks_db = TedTalkDatabase(app.config['DATABASE'])

    return g.tedtalks_db


class RequestError(Exception):
    """
    This custom exception class is for easily handling errors in requests,
    such as when the user provides an ID that does not exist or omits a
    required field.

    We inherit from the Exception class, which is the base Python class that
    provides basic exception functionality. Our custom exception class takes
    a status code and error message in its initializer, and then has a
    to_response() method which creates a JSON response. When an exception of
    this type is raised, the error handler will take care of sending the
    response to the client.
    """

    def __init__(self, status_code, error_message):
        super().__init__(self)

        self.status_code = str(status_code)
        self.error_message = error_message

    def to_response(self):
        """
        Create a Response object containing the error message as JSON.

        :return: the response
        """

        response = jsonify({'error': self.error_message})
        response.status = self.status_code
        return response


@app.errorhandler(RequestError)
def handle_invalid_usage(error):
    """
    Returns a JSON response built from a RequestError.

    :param error: the RequestError
    :return: a response containing the error message
    """
    return error.to_response()


class SpeechesView(MethodView):
    """
    This view handles all the /dogs requests.
    """

    def get(self, speech_id):
        """
        Handle GET requests.

        Returns JSON representing all of the speeches if speech_id is None, or a
        single speech if speech_id is not None.

        :param speech_id: id of a speech, or None for all speeches
        :return: JSON response
        """
        if speech_id is None:
            speeches = get_db().get_all_speeches()
            return jsonify(speeches)
        else:
            speech = get_db().get_speech_by_id(speech_id)

            if speech is not None:
                reviews = get_db().get_reviews_by_speech(speech_id)
                if reviews:
                    speech['reviews'] = reviews
                response = jsonify(speech)
            else:
                raise RequestError(404, 'speech not found')

            return response

    def post(self):
        """
        Implements POST /speeches

        Requires the form parameters 'title', 'duration',
        'views', 'date', 'topic', 'speaker'

        :return: JSON response representing the new speech
        """

        for parameter in ('title', 'duration', 'views',
                          'date', 'topic', 'speaker'):
            if parameter not in request.form:
                error = 'parameter {} required'.format(parameter)
                raise RequestError(422, error)

        speech = get_db().insert_speech(request.form['title'],
                                        request.form['duration'],
                                        request.form['views'],
                                        request.form['date'],
                                        request.form['topic'],
                                        request.form['speaker'])
        return jsonify(speech)

    def delete(self, speech_id):
        """
        Handle DELETE requests. The speech_id must be provided.

        :param speech_id: id of a speech
        :return: JSON response containing a message
        """
        if get_db().get_speech_by_id(speech_id) is None:
            raise RequestError(404, 'speech not found')

        get_db().delete_speech(speech_id)

        return jsonify({'message': 'speech deleted successfully'})


class TopicsView(MethodView):
    """
    This view handles all the /topics requests.
    """

    def get(self, topic_id):
        """
        Handle GET requests.

        Returns JSON representing all of the topics if topic_id is None, or a
        single topic if topic_id is not None.

        :param topic_id: id of a topic, or None for all topics
        :return: JSON response
        """
        if topic_id is None:
            return jsonify(get_db().get_all_topics())
        else:
            topic = get_db().get_topic_by_id(topic_id)

            if topic is not None:
                speeches = get_db().get_speeches_by_topic(topic_id)
                if speeches:
                    topic['speeches'] = speeches
                response = jsonify(topic)
            else:
                raise RequestError(404, 'topic not found')

            return response

    def post(self):
        """
        Handles a POST request to insert a new topic. Returns a JSON
        response representing the new topic.

        Requires the form parameter 'topic'

        :return: a response containing the JSON representation of the topic
        """
        if 'topic' not in request.form:
            raise RequestError(422, 'name of topic required')
        else:
            response = jsonify(get_db().insert_topic(request.form['topic']))

        return response

    def delete(self, topic_id):
        """
        Handle DELETE requests. The topic_id must be provided.

        :param topic_id: id of a breed
        :return: JSON response containing a message
        """
        if get_db().get_topic_by_id(topic_id) is None:
            raise RequestError(404, 'topic not found')

        get_db().delete_topic(topic_id)

        return jsonify({'message': 'topic deleted successfully'})


class SpeakersView(MethodView):
    """
    This view handles all the /speakers requests.
    """

    def get(self, speaker_id):
        """
        Handle GET requests.

        Returns JSON representing all of the speakers if speaker_id is None,
        or a single speaker if speaker_id is not None.

        :param speaker_id: id of an speaker, or None for all speakers
        :return: JSON response
        """
        if speaker_id is None:
            return jsonify(get_db().get_all_speakers())
        else:
            speaker = get_db().get_speaker_by_id(speaker_id)

            if speaker is not None:
                speeches = get_db().get_speeches_by_speaker(speaker_id)
                if speeches:
                    speaker['speeches'] = speeches
                response = jsonify(speaker)
            else:
                raise RequestError(404, 'speaker not found')

            return response

    def post(self):
        """
        Handles a POST request to insert a new speaker. Returns a JSON
        response representing the new speaker.

        Requires the form parameter 'speaker'

        :return: a response containing the JSON representation of the speaker
        """
        if 'speaker' not in request.form:
            raise RequestError(422, 'speaker name required')
        else:
            response = jsonify(get_db().insert_speaker(request.form['speaker']))

        return response

    def delete(self, speaker_id):
        """
        Handle DELETE requests. The speaker_id must be provided.

        :param speaker_id: id of an speaker
        :return: JSON response containing a message
        """
        if get_db().get_speaker_by_id(speaker_id) is None:
            raise RequestError(404, 'speaker not found')

        get_db().delete_speaker(speaker_id)

        return jsonify({'message': 'speaker deleted successfully'})


class ReviewsView(MethodView):
    """
    This view handles all the /speakers requests.
    """

    def get(self, review_id):
        """
        Handle GET requests.

        Returns JSON representing all of the reviews if review_id is None, or a
        single review if review_id is not None.

        :param review_id: id of a review, or None for all reviews
        :return: JSON response
        """
        if review_id is None:
            return jsonify(get_db().get_all_reviews())
        else:
            review = get_db().get_review_by_id(review_id)

            if review is not None:
                response = jsonify(review)
            else:
                raise RequestError(404, 'review not found')

            return response

    def delete(self, review_id):
        """
        Handle DELETE requests. The review_id must be provided.

        :param review_id: id of a review
        :return: JSON response containing a message
        """
        if get_db().get_review_by_id(review_id) is None:
            raise RequestError(404, 'review not found')

        get_db().delete_review(review_id)

        return jsonify({'message': 'review deleted successfully'})


# Register SpeechesView as the handler for all the /speeches requests
speeches_view = SpeechesView.as_view('speeches_view')
app.add_url_rule('/speeches', defaults={'speech_id': None},
                 view_func=speeches_view, methods=['GET', 'DELETE'])
app.add_url_rule('/speeches', view_func=speeches_view, methods=['POST'])
app.add_url_rule('/speeches/<int:speech_id>', view_func=speeches_view,
                 methods=['GET', 'DELETE'])

# Register TopicsView as the handler for all the /topics/ requests
topics_view = TopicsView.as_view('topics_view')
app.add_url_rule('/topics', defaults={'topic_id': None},
                 view_func=topics_view, methods=['GET', 'DELETE'])
app.add_url_rule('/topics', view_func=topics_view, methods=['POST'])
app.add_url_rule('/topics/<int:topic_id>', view_func=topics_view,
                 methods=['GET', 'DELETE'])

# Register OwnersView as the handler for all the /owners/ requests
speakers_view = SpeakersView.as_view('speakers_view')
app.add_url_rule('/speakers', defaults={'speaker_id': None},
                 view_func=speakers_view, methods=['GET', 'DELETE'])
app.add_url_rule('/speakers', view_func=speakers_view, methods=['POST'])
app.add_url_rule('/speakers/<int:speaker_id>', view_func=speakers_view,
                 methods=['GET', 'DELETE'])

# Register ReviewsView as the handler for all the /reviews/ requests
reviews_view = ReviewsView.as_view('reviews_view')
app.add_url_rule('/reviews', defaults={'review_id': None},
                 view_func=reviews_view, methods=['GET', 'DELETE'])
app.add_url_rule('/reviews/<int:review_id>', view_func=reviews_view,
                 methods=['GET', 'DELETE'])

if __name__ == '__main__':
    app.run(debug=True)
