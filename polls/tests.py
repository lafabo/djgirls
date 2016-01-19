from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from .models import Question
import datetime


# Create your tests here.
def create_question(question_text, days):
	"""
	crates a question with given :param question_text:
	published with :param days: offset to now (negative to pub_date in the past,
	positive for not published yet
	"""
	time = timezone.now() + datetime.timedelta(days=days)
	return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionViewTests(TestCase):
	def test_index_view_with_no_questions(self):
		"""if no questions exist show message"""
		response = self.client.get(reverse('polls:index'))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "No polls are available.")
		self.assertQuerysetEqual(response.context['latest_question_list'], [])

	def test_index_view_with_a_past_question(self):
		"""Questions with a pub_date in the past should be displayed on the index"""
		create_question(question_text="Past question", days=-30)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			['<Question: Past question>']
		)

	def test_index_view_with_a_future_question(self):
		"""future polls should not be displayed on the index"""
		create_question(question_text="Future question", days=30)
		response = self.client.get(reverse('polls:index'))
		self.assertContains(response, "No polls are available", status_code=200)
		self.assertQuerysetEqual(response.context['latest_question_list'],[])

	def test_index_view_with_future_and_past_question(self):
		"""Future - no, past - yes"""
		create_question(question_text="Past question", days=-30)
		create_question(question_text="Future question", days=30)
		response = self.client.get(reverse('polls:index'))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
			['<Question: Past question>']
		)

	def test_index_view_with_two_past_questions(self):
		""" the questions index page may display multiply questions """
		create_question(question_text='Past question 1', days=-30)
		create_question(question_text='Past question 2', days=-4)
		response = self.client.get((reverse('polls:index')))
		self.assertQuerysetEqual(
			response.context['latest_question_list'],
				['<Question: Past question 2>', '<Question: Past question 1']
		)


class QuestionIndexDetailTests(TestCase):
	def test_detail_view_with_a_future_question(self):
		"""Should  return 404 for a future questions details"""
		future_question = create_question(question_text='Future question', days=5)
		response = self.client.get(reverse('polls:detail', args=(future_question.id, )))
		self.assertEqual(response.status_code, 404)

	def test_detail_view_with_a_past_question(self):
		past_question = create_question(question_text='Past Question', days=-5)
		response = self.client.get(reverse('polls:detail', args=(past_question.id, )))
		self.assertContains(response, past_question.question_text, status_code=200)


class QuestionMethodTests(TestCase):
	def test_was_published_recently_with_future_question(self):
		"""was_published_recently() should return false
		when question pub_date > time.now"""
		time = timezone.now() + datetime.timedelta(days=30)
		future_question = Question(pub_date=time)
		self.assertEqual(future_question.was_published_recently(), False)

	def test_was_published_recently_with_recent_question(self):
		"""
		was_published_recently() shoud terurn True for questions
		with pub_date in last day
		"""
		time = timezone.now() - datetime.timedelta(hours=1)
		recent_question = Question(pub_date=time)
		self.assertEqual(recent_question.was_published_recently(), True)
