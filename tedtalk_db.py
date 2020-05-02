"""
This module contains the class TedTalkDatabase, which provides an interface to
an SQLite database containing information about Ted Talks. It is designed to be
used for the HTML web pages in tedtalks_html.py and
REST API implementation in tedtalks_api.py.
"""


import os
import sqlite3
import csv


def row_to_dict_or_none(cur):
    """
    Given a cursor that has just been used to execute a query, try to fetch one
    row. If the there is no row to fetch, return None, otherwise return a
    dictionary representation of the row.

    :param cur: a cursor that has just been used to execute a query
    :return: a dict representation of the next row, or None
    """
    row = cur.fetchone()

    if row is None:
        return None
    else:
        return dict(row)


class TedTalkDatabase:
    """
    This class provides methods for getting and inserting information about
    speeches, speakers, topics, and reviews into an SQLite database.
    """

    def __init__(self, sqlite_filename):
        """
        Creates a connection to the database, and creates tables if the
        database file did not exist prior to object creation.

        :param sqlite_filename: the name of the SQLite database file
        """
        if os.path.isfile(sqlite_filename):
            create_tables = False
        else:
            create_tables = True

        self.conn = sqlite3.connect(sqlite_filename)
        self.conn.row_factory = sqlite3.Row

        cur = self.conn.cursor()
        cur.execute('PRAGMA foreign_keys = 1')
        cur.execute('PRAGMA journal_mode = WAL')
        cur.execute('PRAGMA synchronous = NORMAL')

        if create_tables:
            self.create_tables()

    def create_tables(self):
        """
        Create the tables speaker, topic, speech, and review.
        """
        cur = self.conn.cursor()
        cur.execute('CREATE TABLE speaker(speaker_id INTEGER PRIMARY KEY, '
                    '    speaker TEXT UNIQUE)')
        cur.execute('CREATE TABLE topic(topic_id INTEGER PRIMARY KEY, '
                    '    topic TEXT UNIQUE)')
        cur.execute('CREATE TABLE speech(speech_id INTEGER PRIMARY KEY, '
                    '    title TEXT, duration INTEGER, '
                    '    views INTEGER, date DATE, '
                    '    topic_id INTEGER, speaker_id INTEGER, '
                    '    FOREIGN KEY (topic_id) REFERENCES topic(topic_id), '
                    '    FOREIGN KEY (speaker_id) '
                    '       REFERENCES speaker(speaker_id))')
        cur.execute('CREATE TABLE review(review_id INTEGER PRIMARY KEY, '
                    '    content TEXT, speech_id INTEGER, '
                    '    FOREIGN KEY (speech_id) REFERENCES speech(speech_id))')
        self.conn.commit()

    def insert_review(self, content, speech_id):
        """
        Inserts a review into the database. The review's speech_id
        must already exist in the database.

        Returns a dictionary representation of the review.

        :param content: content of the review
        :param speech_id: id of the speech that the review refers to
        :return: a dict representing the review
        """
        cur = self.conn.cursor()
        speech_dict = self.get_speech_by_id(speech_id)
        try:
            speech_id = speech_dict['speech_id']

            query = ('INSERT INTO review(content, speech_id) '
                     'VALUES(?, ?)')

            cur.execute(query, (content, speech_id))

            self.conn.commit()

            return self.get_review_by_id(cur.lastrowid)

        except TypeError:
            print("Speech with the given ID does not exist.")
            return 1

    def get_review_by_id(self, review_id):
        """
        Given a review's primary key, return a dictionary representation of the
        review, or None if there is no review with that primary key.

        :param review_id: the primary key of the review
        :return: a dict representing the review
        """
        cur = self.conn.cursor()

        query = ('SELECT review.review_id as review_id, '
                 'review.content as content, '
                 'speech.speech_id as speech_id, '
                 'speech.title as speech_title '
                 'FROM speech, review '
                 'WHERE review.speech_id = speech.speech_id '
                 'AND review.review_id = ?')

        cur.execute(query, (review_id,))
        return row_to_dict_or_none(cur)

    def get_all_reviews(self):
        """
        Return a list dictionaries representing all of the reviews in the
        database.

        :return: a list of dict objects representing reviews
        """

        cur = self.conn.cursor()

        query = ('SELECT review.review_id as review_id, '
                 'review.content as content, '
                 'speech.speech_id as speech_id, '
                 'speech.title as speech_title '
                 'FROM speech, review '
                 'WHERE review.speech_id = speech.speech_id')

        reviews = []
        cur.execute(query)

        for row in cur.fetchall():
            reviews.append(dict(row))

        return reviews

    def get_reviews_by_speech(self, speech_id):
        """
        Given a speech's primary key, return a list of
        all reviews for that speech.

        :param speech_id: the primary key of the speech
        :return: a list dict representing the reviews for the given speech
        """
        cur = self.conn.cursor()

        query = ('SELECT review.review_id as review_id, '
                 'review.content as content, '
                 'speech.title as speech_title, '
                 'speech.speech_id as speech_id '
                 'FROM review, speech '
                 'WHERE speech.speech_id = review.speech_id '
                 'AND speech.speech_id = ?')

        reviews = []
        cur.execute(query, (speech_id,))
        for row in cur.fetchall():
            reviews.append(dict(row))

        return reviews

    def delete_review(self, review_id):
        """
        Delete the review with the given primary key.

        :param review_id: primary key of the review
        """

        cur = self.conn.cursor()

        query = 'DELETE FROM review WHERE review_id = ?'
        cur.execute(query, (review_id,))

        self.conn.commit()

    def insert_speech(self, title, duration, views, date, topic, speaker):
        """
        Inserts a speech into the database. If the speech's topic/speaker
        is not already in the database, inserts topic/speaker too.

        Returns a dictionary representation of the speech.

        :param title: title of the speech
        :param duration: duration of the speech, in seconds
        :param views: number of views of the speech
        :param date: the date of the speech
        :param topic: the topic of the speaker
        :param speaker: name of the speaker
        :return: a dict representing the speech
        """
        cur = self.conn.cursor()
        self.insert_topic(topic)
        self.insert_speaker(speaker)
        topic_dict = self.get_topic_by_name(topic)
        topic_id = topic_dict['topic_id']
        speaker_dict = self.get_speaker_by_name(speaker)
        speaker_id = speaker_dict['speaker_id']

        query = ('INSERT INTO speech(title, duration, views, '
                 '                   date, topic_id, speaker_id) '
                 'VALUES(?, ?, ?, ?, ?, ?)')

        cur.execute(query, (title, duration, views,
                            date, topic_id, speaker_id))
        self.conn.commit()

        return self.get_speech_by_id(cur.lastrowid)

    def get_speech_by_id(self, speech_id):
        """
        Given a speech's primary key, return a dictionary representation of the
        speech, or None if there is no speech with that primary key.

        :param speech_id: the primary key of the speech
        :return: a dict representing the speech
        """
        cur = self.conn.cursor()

        query = ('SELECT speech.speech_id as speech_id, speech.title as title, '
                 'speech.duration as duration, speech.views as views, '
                 'speech.date as date, topic.topic as topic, '
                 'topic.topic_id as topic_id, '
                 'speaker.speaker as speaker, '
                 'speaker.speaker_id as speaker_id '
                 'FROM speech, topic, speaker '
                 'WHERE speech.topic_id = topic.topic_id '
                 'AND speech.speaker_id = speaker.speaker_id '
                 'AND speech.speech_id = ?')

        cur.execute(query, (speech_id,))
        return row_to_dict_or_none(cur)

    def get_all_speeches(self):
        """
        Return a list dictionaries representing all of the speeches in the
        database.

        :return: a list of dict objects representing speeches
        """

        cur = self.conn.cursor()

        query = ('SELECT speech.speech_id as speech_id, speech.title as title, '
                 'speech.duration as duration, speech.views as views, '
                 'speech.date as date, topic.topic as topic, '
                 'topic.topic_id as topic_id, '
                 'speaker.speaker as speaker, '
                 'speaker.speaker_id as speaker_id '
                 'FROM speech, topic, speaker '
                 'WHERE speech.topic_id = topic.topic_id '
                 'AND speech.speaker_id = speaker.speaker_id')

        speeches = []
        cur.execute(query)

        for row in cur.fetchall():
            speeches.append(dict(row))

        return speeches

    def get_speeches_by_speaker(self, speaker_id):
        """
        Given a speaker's primary key, return a list of
        all speeches by that speaker.

        :param speaker_id: the primary key of the speaker
        :return: a list dict representing the speeches by that speaker
        """
        cur = self.conn.cursor()

        query = ('SELECT speech.speech_id as speech_id, speech.title as title, '
                 'speech.duration as duration, speech.views as views, '
                 'speech.date as date, topic.topic as topic, '
                 'topic.topic_id as topic_id, '
                 'speaker.speaker as speaker, '
                 'speaker.speaker_id as speaker_id '
                 'FROM speech, topic, speaker '
                 'WHERE speech.topic_id = topic.topic_id '
                 'AND speech.speaker_id = speaker.speaker_id '
                 'AND speaker.speaker_id = ?')

        speeches = []
        cur.execute(query, (speaker_id,))
        for row in cur.fetchall():
            speeches.append(dict(row))

        return speeches

    def get_speeches_by_topic(self, topic_id):
        """
        Given a topic's primary key, return a list of
        all speeches with that topic.

        :param topic_id: the primary key of the topic
        :return: a list dict representing the speeches with the given topic
        """
        cur = self.conn.cursor()

        query = ('SELECT speech.speech_id as speech_id, speech.title as title, '
                 'speech.duration as duration, speech.views as views, '
                 'speech.date as date, topic.topic as topic, '
                 'topic.topic_id as topic_id, '
                 'speaker.speaker as speaker, '
                 'speaker.speaker_id as speaker_id '
                 'FROM speech, topic, speaker '
                 'WHERE speech.topic_id = topic.topic_id '
                 'AND speech.speaker_id = speaker.speaker_id '
                 'AND topic.topic_id = ?')

        speeches = []
        cur.execute(query, (topic_id,))
        for row in cur.fetchall():
            speeches.append(dict(row))

        return speeches

    def delete_speech(self, speech_id):
        """
        Delete the speech with the given primary key.

        :param speech_id: primary key of the speech
        """

        cur = self.conn.cursor()

        query1 = 'DELETE FROM review WHERE speech_id = ?'
        cur.execute(query1, (speech_id,))
        query2 = 'DELETE FROM speech WHERE speech_id = ?'
        cur.execute(query2, (speech_id,))

        self.conn.commit()

    def insert_topic(self, topic):
        """
        Insert a topic into the database if it does not exist. Do nothing if
        there is already a topic with the given name in the database.

        Return a dict representation of the topic.

        :param topic: the topic of the speech
        :return: dict representing the topic
        """
        cur = self.conn.cursor()
        query = 'INSERT OR IGNORE INTO topic(topic) VALUES(?)'
        cur.execute(query, (topic,))
        self.conn.commit()
        return self.get_topic_by_name(topic)

    def get_all_topics(self):
        """
        Get a list of dictionary representations of all the topics in the
        database.

        :return: list of dicts representing all topics
        """
        cur = self.conn.cursor()

        query = 'SELECT * FROM topic'

        topics = []
        cur.execute(query)

        for row in cur.fetchall():
            topics.append(dict(row))

        return topics

    def get_topic_by_id(self, topic_id):
        """
        Get a dictionary representation of the topic with the given primary
        key. Return None if the topic does not exist.

        :param topic_id: primary key of the topic
        :return: a dict representing the topic, or None
        """
        cur = self.conn.cursor()
        query = 'SELECT topic_id, topic FROM topic WHERE topic_id = ?'
        cur.execute(query, (topic_id,))
        return row_to_dict_or_none(cur)

    def get_topic_by_name(self, topic):
        """
        Get a dictionary representation of the topic with the given name.
        Return None if there is no such topic.

        :param topic: the name of the topic
        :return: a dict representing the topic, or None
        """
        cur = self.conn.cursor()
        query = 'SELECT topic_id, topic FROM topic WHERE topic = ?'
        cur.execute(query, (topic,))
        return row_to_dict_or_none(cur)

    def delete_topic(self, topic_id):
        """
        Delete the topic with the given id, and
        delete relevant speeches and reviews for that topic.

        :param topic_id: primary key of the topic
        """

        cur = self.conn.cursor()

        speeches = []
        speeches = self.get_speeches_by_topic(topic_id)
        for speech in speeches:
            speech_id = speech['speech_id']
            query = 'DELETE FROM review WHERE speech_id = ?'
            cur.execute(query, (speech_id,))

        query1 = 'DELETE FROM speech WHERE topic_id = ?'
        cur.execute(query1, (topic_id,))
        query2 = 'DELETE FROM topic WHERE topic_id = ?'
        cur.execute(query2, (topic_id,))

        self.conn.commit()

    def insert_speaker(self, speaker):
        """
        Insert a speaker into the database if he/she/they does not exist.
        Do nothing if there is already a speaker
        with the given name in the database.

        Return a dict representation of the speaker.

        :param speaker: name of the speaker
        :return: dict representing the speaker
        """
        cur = self.conn.cursor()
        query = 'INSERT OR IGNORE INTO speaker(speaker) VALUES(?)'
        cur.execute(query, (speaker,))
        self.conn.commit()
        return self.get_speaker_by_name(speaker)

    def get_all_speakers(self):
        """
        Get a list of dictionary representations of all the speakers in the
        database.

        :return: list of dicts representing all speakers
        """
        cur = self.conn.cursor()

        query = 'SELECT * FROM speaker'

        speakers = []
        cur.execute(query)

        for row in cur.fetchall():
            speakers.append(dict(row))

        return speakers

    def get_speaker_by_id(self, speaker_id):
        """
        Get a dictionary representation of the speaker with the given primary
        key. Return None if the speaker does not exist.

        :param speaker_id: primary key of the speaker
        :return: a dict representing the speaker, or None
        """
        cur = self.conn.cursor()
        query = 'SELECT speaker_id, speaker FROM speaker WHERE speaker_id = ?'
        cur.execute(query, (speaker_id,))
        return row_to_dict_or_none(cur)

    def get_speaker_by_name(self, speaker):
        """
        Get a dictionary representation of the speaker with the given name.
        Return None if there is no such speaker.

        :param speaker: name of the speaker
        :return: a dict representing the speaker, or None
        """
        cur = self.conn.cursor()
        query = 'SELECT speaker_id, speaker FROM speaker WHERE speaker = ?'
        cur.execute(query, (speaker,))
        return row_to_dict_or_none(cur)

    def delete_speaker(self, speaker_id):
        """
        Delete the speaker and the speeches with the given speaker id.

        :param speaker_id: primary key of the speaker
        """

        cur = self.conn.cursor()

        speeches = []
        speeches = self.get_speeches_by_speaker(speaker_id)
        for speech in speeches:
            speech_id = speech['speech_id']
            query = 'DELETE FROM review WHERE speech_id = ?'
            cur.execute(query, (speech_id,))

        query1 = 'DELETE FROM speech WHERE speaker_id = ?'
        cur.execute(query1, (speaker_id,))
        query2 = 'DELETE FROM speaker WHERE speaker_id = ?'
        cur.execute(query2, (speaker_id,))

        self.conn.commit()


if __name__ == '__main__':

    db = TedTalkDatabase('tedtalks.sqlite')
    with open('sample.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            db.insert_speech(row['title'], row['duration'], row['views'],
                             row['date'], row['topic'], row['speaker'])
