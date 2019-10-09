from asltutor.models.dictionary import Dictionary
from asltutor.models.submission import Submission
from asltutor.models.user import User
from flask import Blueprint
from flask import request, Response
from bson import ObjectId

admin = Blueprint('admin', __name__)

# Everything in here should be privileged


@admin.route('/admin/stats', methods=['GET'])
def get_stats():
    """Get top most requested words

    Returns a list of JSON objects with the top 'N' where 5 <= N <= 100 most downloaded words.

    query parameter: /admin/stats?limit=somenumber
    where 5 <= somenumber <= 100

    no request body

    :rtype: json
    """
    limit = int(request.args.get('limit'))
    if limit < 5 or limit > 100:
        limit = 20
    o = Dictionary.objects(in_dictionary=False).order_by(
        '-times_requested')[:limit]
    return Response(o.to_json(), mimetype='application/json')


@admin.route('/admin/stats/users', methods=['GET'])
def get_user_stats():
    """Gets user stats

    Returns the following data points:
        total number of users
        total number of verified users
        total number of users registered within N number of days
        total number of users that logged within N number of days
        total number of submission
        total number of submissions created within N number of days
        average age of users

    no request body

    :rtype: json
    """
    num_users = User.objects.count()
    num_verified = User.objects(is_verified=True).count()

    num_submission = Submission.objects.count()
    # avg_age = User.objects
    pass


@admin.route('/admin/submissions', methods=['GET'])
def get_submissions():
    """Get a list of all submissions filtered based on certian criteria.

    Returns an array of all submissions. It can be filtered based on quizId and/or moduleId and/or userId.
    For example, a user can request all of their sumissions for any combination of moduleId or quizId.
    Must have at least one filter otherwise error

    :query param submission: The Id of the submission that a user is requesting.
    :type submission_id: str
    :query param quiz: The quiz Id that a user wants all submissions for
    :type quiz: str
    :query param module: The module Id that a user wants all submissions for
    :type module: str
    :query param user: The username of the user that the admin wants all the submissions for
    :type user: str

    :rtype: JSON
    """

    # If we are given a submission Id no filtering needs to be done. Return the document referenced by the id.
    submissionId = request.args.get('submission', None)
    username = request.args.get('user', None)
    quizId = request.args.get('quiz', None)
    moduleId = request.args.get('module', None)

    if submissionId:
        if ObjectId.is_valid(submissionId):
            # submission cannot be combined with other queries
            if not username and not quizId and not moduleId:
                return Response(Submission.objects.get_or_404(id=submissionId).to_json(), mimetype='application/json')
            else:
                return Response('Failed: Submission query cannot be combined with other queries', 400)
        else:
            return Response('Failed: invalid Id', 400)

    # if submissionId is not specified do further filtering
    subs = Submission.objects()
    if not username and not quizId and not moduleId:
        return Response('Failed: specify at least one filter to view submissions', 412)

    if username:
        user = User.objects.get_or_404(username=username)
        subs = subs.filter(user_id__exact=user.id)

    if moduleId:
        if ObjectId.is_valid(moduleId):
            subs = subs.filter(module_id__exact=moduleId)
        else:
            return Response('Failed: invalid Id', 400)

    if quizId:
        if ObjectId.is_valid(quizId):
            subs = Submission.objects(quiz_id__exact=quizId)
        else:
            return Response('Failed: invalid Id', 400)

    if subs:
        return Response(subs.to_json(), mimetype='application/json')
    return Response('Failed: No submission found for that query')