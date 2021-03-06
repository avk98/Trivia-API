import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginate(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]

    return questions[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app)
    # CORS Headers

    '''
    @TODO: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    '''
    @app.route('/categories')
    def view_categories():
        selection = Category.query.order_by(Category.id).all()
        category = paginate(request, selection)
        if len(category) == 0:
            abort(404)
        return jsonify({
            "success": True,
            "categories": {c['id']: c['type'] for c in category},
            "total_categories": len(selection)
        })
    '''
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    '''
    @app.route('/questions')
    def retrieve_questions():
        selection = Question.query.order_by(Question.id).all()
        current_question = paginate(request, selection)
        if len(current_question) == 0:
            abort(404)
        return jsonify({
            "success": True,
            "questions": current_question,
            "total_questions": len(selection),
            "categories": {category.id: category.type for category in Category.query.order_by(Category.id).all()},
            "current_category": None
        })
    '''
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()
        if question == None:
            abort(422)
        question.delete()
        return jsonify({
            "success": True
        })
    '''
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    '''
    @app.route('/questions', methods=["POST"])
    def create_question():
        data = request.get_json()
        if 'searchTerm' in data:
            search = data['searchTerm']
            selection = Question.query.order_by(Question.id).filter(
                Question.question.ilike('%{}%'.format(search)))
            searches = paginate(request, selection)
            return jsonify({
                'success': True,
                'questions': searches,
                'total_questions': len(searches),
                'current_category': None
            })
        else:
            question = data['question']
            answer = data['answer']
            difficulty = data['difficulty']
            category = data['category']
            Question(question=question, answer=answer,
                     difficulty=difficulty, category=category).insert()
            return jsonify({
                "success": True
            })
        abort(422)
    '''@TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    '''

    '''
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    '''
    @app.route('/categories/<int:category_id>/questions')
    def questions_category(category_id):
        questions = Question.query.order_by(Question.id).filter(
            Question.category == category_id).all()
        current_questions = paginate(request, questions)
        return jsonify({
            "success": True,
            "questions": current_questions,
            'total_questions': len(current_questions),
            "current_category": category_id
        })
    '''
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    '''
    @app.route('/quizzes', methods=["POST"])
    def render_questions():
        data = request.get_json()
        previousQuestions = data['previous_questions']
        category = data['quiz_category']['id']
        if category == 0:
            currentQuestion = Question.query.filter(
                Question.id.notin_(previousQuestions)).all()
        else:
            currentQuestion = Question.query.filter(
                Question.category == data['quiz_category']['id']).filter(Question.id.notin_(previousQuestions)).all()
        if len(currentQuestion) == 0:
            return jsonify({
                'success': True,
                'question': None
            }), 200

        return jsonify({
            "success": True,
            "question": random.choice(currentQuestion).format()
        })
    '''
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    '''
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            "message": 'Resource not found',
            "error": 404
        }), 404

    @app.errorhandler(422)
    def not_found(error):
        return jsonify({
            'success': False,
            "message": 'Unprocessable request',
            "error": 422
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    return app
