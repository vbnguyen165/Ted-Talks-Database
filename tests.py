"""
The tests in this file are written to be used with pytest.
A subset of the TedTalkDatabase methods are tested.
"""


from tedtalk_db import TedTalkDatabase


def build_db_path(directory):
    """
    Given a directory as a Path object, construct a path to a file named
    test.sqlite within that directory.

    :param directory: a Path object representing the directory
    :return: a Path object representing the path to the file
    """

    return directory / 'test.sqlite'


def test_initializer(tmp_path):
    """
    Test that the DogDatabase initializer runs without errors.

    :param tmp_path: a Path object representing the path to the temporary
     directory created via the pytest tmp_path fixture
    """

    TedTalkDatabase(build_db_path(tmp_path))


def test_insert_speech(tmp_path):
    """
    Test that insert_speech() runs without raising exceptions, and correctly
    returns a dictionary representing the new speech.
    """
    db = TedTalkDatabase(build_db_path(tmp_path))

    speech = db.insert_speech('The laws that sex workers really want', 1070,
                              1811102, '2016-05-19', 'activism', 'Juno Mac')

    assert speech['title'] == 'The laws that sex workers really want'
    assert speech['duration'] == 1070
    assert speech['views'] == 1811102
    assert speech['date'] == '2016-05-19'
    assert speech['topic'] == 'activism'
    assert speech['speaker'] == 'Juno Mac'


def test_get_speech_by_id(tmp_path):
    """
    Test that get_speech_by_id() returns None when it should,
    and properly returns
    a speech when there are 1 or 2 speeches in the database.
    """

    db = TedTalkDatabase(build_db_path(tmp_path))

    assert db.get_speech_by_id(1) is None

    speech_inserted = \
        db.insert_speech('The laws that sex workers really want', 1070, 1811102,
                         '2016-05-19', 'activism', 'Juno Mac')
    speech = db.get_speech_by_id(1)

    assert speech_inserted == speech

    assert db.get_speech_by_id(2) is None

    speech_inserted = \
        db.insert_speech('Science in service to the public good', 873,
                         872015, '2017-04-25', 'activism', 'Siddhartha Roy')

    speech = db.get_speech_by_id(2)

    assert speech_inserted == speech


def test_get_all_speeches(tmp_path):
    """
    Test that get_all_speeches() properly returns an empty list when no speeches
    have been inserted, and returns a correct list of speeches when
    there are one or two speeches in the database.
    """

    db = TedTalkDatabase(build_db_path(tmp_path))

    assert db.get_all_speeches() == []

    speech_inserted = \
        db.insert_speech('The laws that sex workers really want',
                         1070, 1811102, '2016-05-19', 'activism', 'Juno Mac')

    speeches_inserted = [speech_inserted]

    speeches = db.get_all_speeches()

    assert len(speeches) == 1
    assert speeches[0] == speech_inserted

    speeches_inserted.append(
        db.insert_speech('Science in service to the public good', 873,
                         872015, '2017-04-25', 'activism', 'Siddhartha Roy'))

    speeches = db.get_all_speeches()

    assert len(speeches) == 2

    for speech in speeches_inserted:
        assert speech in speeches


def test_insert_review(tmp_path):
    """
    Test that insert_review() runs only when speech_id exists in the database,
    and correctly returns a dictionary representing the new speech
    or an error code of 1.
    """
    db = TedTalkDatabase(build_db_path(tmp_path))

    assert db.insert_review("It's boring", 1) == 1

    db.insert_speech('The laws that sex workers really want', 1070,
                     1811102, '2016-05-19', 'activism', 'Juno Mac')

    review = db.insert_review("It's inspiring", 1)

    assert review['content'] == "It's inspiring"
    assert review['speech_id'] == 1


def test_get_reviews_by_speech(tmp_path):
    """
    Test that get_reviews_by_speech() properly returns an empty list when
    no reviews have been inserted for the given speech_id,
    and returns a correct list of reviews for the given speech_id when
    there are at least one reviews for the speech exist in the database.
    """

    db = TedTalkDatabase(build_db_path(tmp_path))

    db.insert_speech('The laws that sex workers really want',
                     1070, 1811102, '2016-05-19', 'activism', 'Juno Mac')

    assert db.get_reviews_by_speech(1) == []

    review_inserted = db.insert_review("It's inspiring!", 1)
    reviews_inserted = [review_inserted]
    reviews_inserted.append(
        db.insert_review("The speaker has greatly "
                         "appealed to my sense of reason.", 1))

    reviews = db.get_reviews_by_speech(1)

    assert len(reviews) == 2
    assert reviews[0] == review_inserted

    for review in reviews_inserted:
        assert review in reviews


def test_delete_speaker(tmp_path):
    """
    Test that delete_Speaker properly delete the speaker,
    the speeches and the reviews associated with that speaker.
    """
    db = TedTalkDatabase(build_db_path(tmp_path))

    db.insert_speech('The laws that sex workers really want',
                     1070, 1811102, '2016-05-19', 'activism', 'Juno Mac')

    db.insert_review("It's inspiring!", 1)
    db.insert_review("The speaker has greatly "
                     "appealed to my sense of reason.", 1)

    db.delete_speaker(1)

    assert db.get_speaker_by_id(1) is None
    assert db.get_speeches_by_speaker(1) == []
    assert db.get_reviews_by_speech(1) == []
