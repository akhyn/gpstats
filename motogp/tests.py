import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone


from .models import Season, EventLocation, Event, Session, Result, Rider, Brand, Team, Category

from .scraper import insert_in_database


test_scraped_race_data = [
    ['scraped_race_data_source_url'],
    ['Pos.', 'Points', 'Num.', 'Rider', 'Nation', 'Team', 'Bike', 'Km/h', 'Time/Gap'],
    [('1', '91', '11', 'Dummy RIDERONE', 'COUNTRYONE', 'TeamOne', 'BrandOne', '111.1', "1'11'111", '')],
    [('2', '92', '22', 'Dummy RIDERTWO', 'COUNTRYTWO', 'TeamTwo', 'BrandTwo', '222.2', "2'22'222", '')],
    [('3', '93', '33', 'Dummy RIDER THREE', 'COUNTRYONE', 'TeamOne', 'BrandOne', '333.3', "3'33'333", '')],
    [('4', '', '', '', '', '', '', '', "", '')], # Should get discarded
    [('5', '94', '44', 'Dummy McRIDERFOUR', 'COUNTRYONE', 'TeamOne', 'BrandOne', '444.4', "4'44'444", '')],
]

test_scraped_timed_data = [
    ['scraped_time_data_source_url'],
    ['Pos.', 'Num.', 'Rider', 'Nation', 'Team', 'Bike', 'Km/h', 'Time', 'Gap 1st/Prev.'],
    [('1', '11', 'Dummy RIDERONE', 'COUNTRYONE', 'TeamOne', 'BrandOne', '111.1', "1'11'111", '')],
    [('2', '22', 'Dummy RIDERTWO', 'COUNTRYTWO', 'TeamTwo', 'BrandTwo', '222.2', "2'22'222", '0.111 / 1.111')],
    [('3', '33', 'Dummy RIDER THREE', 'COUNTRYONE', 'TeamOne', 'BrandOne', '333.3', "3'33'333", '0.222 / 0.111')],
    [('4', '44', 'Dummy McRIDERFOUR', 'COUNTRYONE', 'TeamOne', 'BrandOne', '444.4', "4'44'444", '0.333 / 0.111')],
    [('5', '55', 'Dummy RIDERFIVE', 'COUNTRYFIVE', 'Team 5', 'Brand 5', '555.5', "5'55'555", '0.555 / 0.111')],
    [('6', '66', 'Dummy S RIDERSIX', 'COUNTRYONE', 'TeamOne', 'BrandOne', '666.4', "6'44'444", '0.333 / 0.111')],
    [('7', '77', 'Dummy SEVENTH', 'COUNTRYONE', 'TeamOne', 'BrandOne', '744.4', "7'44'444", '0.333 / 0.111')],
    [('8', '88', 'Dummy EIGHTRIDER', 'COUNTRYONE', 'TeamOne', 'BrandOne', '844.4', "8'44'444", '0.333 / 0.111')],
    [('9', '99', 'Dummy N I N E', 'COUNTRYONE', 'TeamOne', 'BrandOne', '944.4', "9'44'444", '0.333 / 0.111')],
    [('10', '1010', 'Dummy TEN', 'COUNTRYONE', 'TeamOne', 'BrandOne', '1044.4', "10'44'444", '0.333 / 0.111')],
    [('11', '1111', 'Dummy McELEVEN', 'COUNTRYONE', 'TeamOne', 'BrandOne', '1144.4', "11'44'444", '0.333 / 0.111')],
    [('12', '1212', 'Dummy TWELVE', 'COUNTRYONE', 'TeamOne', 'BrandOne', '1244.4', "12'44'444", '0.333 / 0.111')],
    [('13', '1313', 'Dummy THIRTEEN', 'COUNTRYONE', 'TeamOne', 'BrandOne', '1344.4', "13'44'444", '0.333 / 0.111')],
]

test_scraped_Q2_data = [
    ['scraped_time_data_source_url'],
    ['Pos.', 'Num.', 'Rider', 'Nation', 'Team', 'Bike', 'Km/h', 'Time', 'Gap 1st/Prev.'],
    [('1', '11', 'Dummy RIDERONE', 'COUNTRYONE', 'TeamOne', 'BrandOne', '111.1', "1'11'111", '')],
    [('2', '22', 'Dummy RIDERTWO', 'COUNTRYTWO', 'TeamTwo', 'BrandTwo', '222.2', "2'22'222", '0.111 / 1.111')],
    [('3', '33', 'Dummy RIDER THREE', 'COUNTRYONE', 'TeamOne', 'BrandOne', '333.3', "3'33'333", '0.222 / 0.111')],
    [('4', '44', 'Dummy McRIDERFOUR', 'COUNTRYONE', 'TeamOne', 'BrandOne', '444.4', "4'44'444", '0.333 / 0.111')],
    [('5', '55', 'Dummy RIDERFIVE', 'COUNTRYFIVE', 'Team 5', 'Brand 5', '555.5', "5'55'555", '0.555 / 0.111')],
    [('6', '66', 'Dummy S RIDERSIX', 'COUNTRYONE', 'TeamOne', 'BrandOne', '666.4', "6'44'444", '0.333 / 0.111')],
    [('7', '77', 'Dummy SEVENTH', 'COUNTRYONE', 'TeamOne', 'BrandOne', '744.4', "7'44'444", '0.333 / 0.111')],
    [('8', '88', 'Dummy EIGHTRIDER', 'COUNTRYONE', 'TeamOne', 'BrandOne', '844.4', "8'44'444", '0.333 / 0.111')],
    [('9', '99', 'Dummy N I N E', 'COUNTRYONE', 'TeamOne', 'BrandOne', '944.4', "9'44'444", '0.333 / 0.111')],
    [('10', '1010', 'Dummy TEN', 'COUNTRYONE', 'TeamOne', 'BrandOne', '1044.4', "10'44'444", '0.333 / 0.111')],
    [('12', '1212', 'Dummy TWELVE', 'COUNTRYONE', 'TeamOne', 'BrandOne', '1244.4', "12'44'444", '0.333 / 0.111')],
    [('13', '1313', 'Dummy THIRTEEN', 'COUNTRYONE', 'TeamOne', 'BrandOne', '1344.4', "13'44'444", '0.333 / 0.111')],
    # Rider eleven missing, did not pass Q1
]

test_scraped_Q1_data = [
    ['scraped_Q1_data_source_url'],
    ['Pos.', 'Num.', 'Rider', 'Nation', 'Team', 'Bike', 'Km/h', 'Time', 'Gap 1st/Prev.'],
    [('13', '1313', 'Dummy THIRTEEN', 'COUNTRYONE', 'TeamOne', 'BrandOne', '1344.4', "13'44'444", '0.333 / 0.111')],
    [('12', '1212', 'Dummy TWELVE', 'COUNTRYONE', 'TeamOne', 'BrandOne', '1244.4', "12'44'444", '0.333 / 0.111')],
    [('11', '1111', 'Dummy McELEVEN', 'COUNTRYONE', 'TeamOne', 'BrandOne', '1144.4', "11'44'444", '0.333 / 0.111')],
]


class DatabaseInsertionTests(TestCase):
    season = '1900'
    event = 'XXXX'
    category = '1cc'
    sessions_map = {
        'FP1': test_scraped_timed_data,
        'Q1': test_scraped_Q1_data,
        'Q2': test_scraped_Q2_data,
        'RAC': test_scraped_race_data,
        'RAC2': test_scraped_race_data,
    }

    def setUp(self, sources=None):
        if sources is None:
            sources = []
        for source in sources:
            results = self.sessions_map[source]
            insert_in_database(
                season=self.season,
                event=self.event,
                category=self.category,
                session=source,
                results=results,
                test_disk_write_skip=True
            )

    def test_timed_data_insertion(self):
        """=> Timed session data should properly create objects in database"""
        session = 'FP1'
        sessions = [session]
        self.setUp(sessions)

        cat, created = Category.objects.get_or_create(class_name=self.category)
        self.assertFalse(created, msg='Category object was not created')
        self.assertEqual(cat.class_name, self.category, msg='Category name not correct')

        e_loc, created = EventLocation.objects.get_or_create(location=self.event)
        self.assertFalse(created, msg='EventLocation object was not created')
        self.assertEqual(e_loc.location, self.event, msg='Event location not correct')

        y, created = Season.objects.get_or_create(year=int(self.season))
        self.assertFalse(created, msg='Season object was not created')
        self.assertEqual(y.year, int(self.season), msg='Season year value not correct')
        self.assertIn(cat, y.categories.all(), msg='Category not registered to Season')

        s, created = Session.objects.get_or_create(session_type=session)
        self.assertFalse(created, msg='Session object was not created')
        self.assertEqual(s.session_type, session, msg='Session type not correct')
        self.assertIs(cat.pk, s.category.pk, msg='Session category not correct')

        e, created = Event.objects.get_or_create(season=y, event_location=e_loc)
        self.assertFalse(created, msg='Event object was not created')

    def test_Q1_insertion(self):
        """=> Q1 session data should properly reuse previous session data"""
        sessions = ['FP1', 'Q1']
        self.setUp(sessions)

        self.assertEqual(2, Session.objects.all().count(), msg='Session count abnormal')
        q, created = Session.objects.get_or_create(session_type='Q1')
        self.assertFalse(created, msg='Q1 object not created')

    def test_Q2_insertion(self):
        pass

    def test_race_data_insertion(self):
        pass

    def test_restarted_race_insertion(self):
        pass


class SeasonViewTests(TestCase):

    def setUp(self):
        season = '1900'
        event = 'XXXX'
        category = '1cc'
        session = 'RAC'
        results = test_scraped_race_data
        insert_in_database(
            season=season,
            event=event,
            category=category,
            session=session,
            results=results,
            test_disk_write_skip=True
        )

    # def test_default_view(self):
    #     """ => Index page should display current championship results """
    #     response = self.client.get(reverse('motogp:index'))
    #     y = Season.objects.all().latest()
    #     season_response = self.client.get(reverse('motogp:season', str(y.year)))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response, season_response)


from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage


class TestStaticFiles(TestCase):
    """Check if app contains required static files"""
    def test_css(self):
        abs_path = finders.find('motogp/style.css')
        self.assertTrue(staticfiles_storage.exists(abs_path))


# from .models import Question
#
#
# class QuestionModelTests(TestCase):
#
#     def test_was_published_recently_with_future_question(self):
#         """
#         was_published_recently() returns False for questions whose pub_date
#         is in the future.
#         """
#         time = timezone.now() + datetime.timedelta(days=30)
#         future_question = Question(pub_date=time)
#         self.assertIs(future_question.was_published_recently(), False)
#
#     def test_was_published_recently_with_old_question(self):
#         """
#         was_published_recently() returns False for questions whose pub_date
#         is older than 1 day.
#         """
#         time = timezone.now() - datetime.timedelta(days=1, seconds=1)
#         old_question = Question(pub_date=time)
#         self.assertIs(old_question.was_published_recently(), False)
#
#     def test_was_published_recently_with_recent_question(self):
#         """
#         was_published_recently() returns True for questions whose pub_date
#         is within the last day.
#         """
#         time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
#         recent_question = Question(pub_date=time)
#         self.assertIs(recent_question.was_published_recently(), True)
#
#
# def create_question(question_text, days):
#     """
#     Create a question with the given `question_text` and published the
#     given number of `days` offset to now (negative for questions published
#     in the past, positive for questions that have yet to be published).
#     """
#     time = timezone.now() + datetime.timedelta(days=days)
#     return Question.objects.create(question_text=question_text, pub_date=time)
#
#
# class QuestionIndexViewTests(TestCase):
#     def test_no_questions(self):
#         """
#         If no questions exist, an appropriate message is displayed.
#         """
#         response = self.client.get(reverse('motogp:index'))
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "No motogp are available.")
#         self.assertQuerysetEqual(response.context['latest_question_list'], [])
#
#     def test_past_question(self):
#         """
#         Questions with a pub_date in the past are displayed on the
#         index page.
#         """
#         create_question(question_text="Past question.", days=-30)
#         response = self.client.get(reverse('motogp:index'))
#         self.assertQuerysetEqual(
#             response.context['latest_question_list'],
#             ['<Question: Past question.>']
#         )
#
#     def test_future_question(self):
#         """
#         Questions with a pub_date in the future aren't displayed on
#         the index page.
#         """
#         create_question(question_text="Future question.", days=30)
#         response = self.client.get(reverse('motogp:index'))
#         self.assertContains(response, "No motogp are available.")
#         self.assertQuerysetEqual(response.context['latest_question_list'], [])
#
#     def test_future_question_and_past_question(self):
#         """
#         Even if both past and future questions exist, only past questions
#         are displayed.
#         """
#         create_question(question_text="Past question.", days=-30)
#         create_question(question_text="Future question.", days=30)
#         response = self.client.get(reverse('motogp:index'))
#         self.assertQuerysetEqual(
#             response.context['latest_question_list'],
#             ['<Question: Past question.>']
#         )
#
#     def test_two_past_questions(self):
#         """
#         The questions index page may display multiple questions.
#         """
#         create_question(question_text="Past question 1.", days=-30)
#         create_question(question_text="Past question 2.", days=-5)
#         response = self.client.get(reverse('motogp:index'))
#         self.assertQuerysetEqual(
#             response.context['latest_question_list'],
#             ['<Question: Past question 2.>', '<Question: Past question 1.>']
#         )
#
#
# class QuestionDetailViewTests(TestCase):
#     def test_future_question(self):
#         """
#         The detail view of a question with a pub_date in the future
#         returns a 404 not found.
#         """
#         future_question = create_question(question_text='Future question.', days=5)
#         url = reverse('motogp:detail', args=(future_question.id,))
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 404)
#
#     def test_past_question(self):
#         """
#         The detail view of a question with a pub_date in the past
#         displays the question's text.
#         """
#         past_question = create_question(question_text='Past Question.', days=-5)
#         url = reverse('motogp:detail', args=(past_question.id,))
#         response = self.client.get(url)
#         self.assertContains(response, past_question.question_text)
