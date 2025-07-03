from flask import Blueprint
from ..views import candidate_views

candidate_bp = Blueprint('candidate_bp', __name__) # Removed url_prefix here, it's in app.register_blueprint




candidate_bp.add_url_rule(
    "/login",
    view_func=candidate_views.CandidateLoginAPI.as_view("candidate_login_api"),
    methods=["POST"]
)

candidate_bp.add_url_rule(
    "/profile",
    view_func=candidate_views.CandidateProfileAPI.as_view("candidate_profile_api"),
    methods=["GET"]
)

candidate_bp.add_url_rule(
    "/get/questions",
    view_func=candidate_views.CandidateMcqsAPI.as_view("candidate_question_api"),
    methods=["GET"]
)

candidate_bp.add_url_rule(
    "/answer",
    view_func=candidate_views.CandidateSaveAnswerAPI.as_view("candidate_answer_api"),
    methods=["POST"]
)

candidate_bp.add_url_rule(
    "/get/all/answers",
    view_func=candidate_views.GetAllAnswersAPI.as_view("candidate_answer_status_api"),
    methods=["GET"]
)

candidate_bp.add_url_rule(
    "/start_exam",
    view_func=candidate_views.StartExamAPI.as_view("start_exam_api"),
    methods=["POST"]
)

candidate_bp.add_url_rule(
    "/submit/exam",
    view_func=candidate_views.SubmitExamAPI.as_view("submit_exam_api"),
    methods=["POST"]
)

candidate_bp.add_url_rule(
    "/log_tab_switch",
    view_func=candidate_views.TabSwitching.as_view("tab_switching_api"),
    methods=["POST"]
)

