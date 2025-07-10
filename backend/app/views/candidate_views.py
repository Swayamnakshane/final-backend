from flask import jsonify, request
from ..models import  db, Candidate,Batch, AssignedMCQ, CandidateAnswer, CandidateExamStatus,PythonMCQ
from flask.views import MethodView
from flask_bcrypt import Bcrypt
import random
import json
from datetime import datetime, timedelta
import pytz # Combined import
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity # Combined import

# Initialize Bcrypt
bcrypt = Bcrypt()

from datetime import datetime

# Initialize Timezone and constants
IST = pytz.timezone('Asia/Kolkata')
OTP_EXPIRY_TIME = 10  # Time in minutes after which OTP expires

from pytz import timezone

IST = timezone('Asia/Kolkata')

from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, get_jti, create_access_token, create_refresh_token
from flask import jsonify, request



IST = timezone("Asia/Kolkata")
jwt = JWTManager()
# @jwt.token_in_blocklist_loader
# def check_if_token_revoked(jwt_header, jwt_payload):
#     identity = jwt_payload["sub"]
#     jti = jwt_payload["jti"]
#     role = jwt_payload.get("role")

#     if role == "candidate":
#         candidate = Candidate.query.get(identity)
#         if not candidate:
#             return True  # Block token if candidate doesn't exist
#         return candidate.active_jti != jti

#     if role == "admin":
#         return False  # Skip revocation for admins

#     return True  # Block all unknown roles
from flask.views import MethodView
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jti
)
from datetime import datetime

class CandidateLoginAPI(MethodView):
    def post(self):
        data = request.get_json()
        user_id = data.get("user_id")
        password = data.get("password")

        candidate = Candidate.query.filter_by(user_id=user_id).first()

        

        # Get exam status
        exam_status = CandidateExamStatus.query.filter_by(
            candidate_id=candidate.candidate_id
        ).first()

        access_token = create_access_token(identity=candidate.user_id)
        refresh_token = create_refresh_token(identity=candidate.user_id)

        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "is_submitted": exam_status.is_submitted if exam_status else False
        }), 200



class TokenRefreshAPI(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()  # will be string
        candidate = Candidate.query.get(int(current_user))  # convert back to int

        new_access_token = create_access_token(
            identity=str(current_user),
            additional_claims={"role": "candidate"}
        )

        if candidate:
            candidate.active_jti = get_jti(new_access_token)
            db.session.commit()

        return jsonify({
            "access_token": new_access_token
        }), 200


class CandidateProfileAPI(MethodView):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        candidate = Candidate.query.filter_by(user_id=user_id).first()

        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        if not candidate.batches:
            return jsonify({"error": "Candidate is not assigned to any batch"}), 404

        # Check for optional batch_id from query params
        batch_id = request.args.get("batch_id")

        if batch_id:
            # Validate the candidate is assigned to that batch
            batch = Batch.query.filter(
                Batch.batch_id == int(batch_id),
                Batch.candidates.any(user_id=user_id)
            ).first()

            if not batch:
                return jsonify({"error": "Batch not found or not assigned to candidate"}), 404
        else:
            # Default: pick the first assigned batch
            batch = candidate.batches[0]

        return jsonify({
            "candidate_name": candidate.name,
            "batch_id": batch.batch_id,
            "batch_title": batch.title,
            "exam_start_date": batch.start_date.strftime("%d-%m-%Y"),
            "exam_end_date": batch.end_date.strftime("%d-%m-%Y"),
            "exam_duration": batch.exam_duration  # in minutes
        }), 200


class CandidateMcqsAPI(MethodView):
    @jwt_required()
    def get(self):
        candidate_id = get_jwt_identity()  # This is user_id like 'sai002'

        candidate = Candidate.query.filter_by(user_id=candidate_id).first()
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        assignments = AssignedMCQ.query.filter_by(candidate_id=candidate.candidate_id).all()
        if not assignments:
            return jsonify({"message": "No MCQs assigned to this candidate"}), 200

        mcqs = []
        for a in assignments:
            mcq = a.question
            mcqs.append({
                "question_id": mcq.id,
                "question": mcq.question,
                "options": mcq.options
            })

        return jsonify({
            "mcqs": mcqs
        }), 200


        
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request, jsonify
from datetime import datetime
from app.models import Candidate, AssignedMCQ, CandidateAnswer, db
from pytz import timezone

IST = timezone("Asia/Kolkata")
class CandidateSaveAnswerAPI(MethodView):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        data = request.get_json()

        if not data or 'question_id' not in data or 'answer' not in data:
            return jsonify({"error": "Invalid input"}), 400

        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        question_id = data['question_id']
        selected_option = data['answer']

        # Verify question is assigned to candidate
        assigned = AssignedMCQ.query.filter_by(
            candidate_id=candidate.candidate_id,
            question_id=question_id
        ).first()
        if not assigned:
            return jsonify({"error": "Question not assigned to candidate"}), 403

        question = PythonMCQ.query.get(question_id)
        if not question:
            return jsonify({"error": "Question not found"}), 404

        actual_answer = question.answer

        existing = CandidateAnswer.query.filter_by(
            candidate_id=candidate.candidate_id,
            question_id=question_id
        ).first()

        if existing:
            existing.selected_option = selected_option
            existing.answered_at = datetime.now(IST)
            existing.is_saved = True
            existing.total_marks = 1 if selected_option == actual_answer else 0
        else:
            new_answer = CandidateAnswer(
                candidate_id=candidate.candidate_id,
                question_id=question_id,
                actual_answer=actual_answer,
                candidate_name=candidate.name,  # ✅ Make sure model has this field
                candidate_email=candidate.email,  # ✅ Make sure model has this field
                selected_option=selected_option,
                is_saved=True,
                total_marks=1 if selected_option == actual_answer else 0,
                answered_at=datetime.now(IST)
            )
            db.session.add(new_answer)

        db.session.commit()
        return jsonify({"message": "Answer saved successfully"}), 200





class GetAllAnswersAPI(MethodView):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        # Fetch candidate by user_id
        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        # Fetch all answers for the candidate
        answers = CandidateAnswer.query.filter_by(candidate_id=candidate.candidate_id).all()
        if not answers:
            return jsonify({"message": "No answers found for this candidate"}), 200

        # Prepare answer list
        answer_list = []
        for answer in answers:
            answer_list.append({
                "question_id": answer.question_id,
                "selected_option": answer.selected_option,
                "is_saved": answer.is_saved,
                "answered_at": answer.answered_at.strftime("%d-%m-%Y %H:%M:%S") if answer.answered_at else None
            })

        return jsonify({"answers": answer_list}), 200






from datetime import datetime, timedelta, timezone
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify
from app.models import db, Candidate, CandidateAnswer, CandidateExamStatus

IST = timezone(timedelta(hours=5, minutes=30))


class StartExamAPI(MethodView):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        now = datetime.now(IST)

        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404
        if not candidate.batches:
            return jsonify({"error": "Candidate not assigned to any batch"}), 400

        batch = candidate.batches[0]
        exam_duration = batch.exam_duration

        status = CandidateExamStatus.query.filter_by(
            candidate_id=candidate.candidate_id,
            batch_id=batch.batch_id
        ).first()

        if status:
            started_at = status.started_at
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=IST)
            end_time = started_at + timedelta(minutes=exam_duration)

            if status.is_submitted:
                return jsonify({"error": "You have already submitted this exam."}), 403

            if now >= end_time:
                answers = CandidateAnswer.query.filter_by(candidate_id=candidate.candidate_id).all()
                correct = sum(1 for a in answers if a.selected_option == a.actual_answer)
                wrong = sum(1 for a in answers if a.selected_option and a.selected_option != a.actual_answer)

                status.correct_answers = correct
                status.wrong_answers = wrong
                status.total_questions = len(answers)
                status.marks_obtained = correct
                status.ended_at = end_time
                status.time_taken = exam_duration
                status.is_submitted = True
                candidate.tab_switch_count = 0
                candidate.active_jti = None

                db.session.commit()
                return jsonify({"error": "Your exam duration is over. It has been auto-submitted."}), 403

            return jsonify({
                "message": "Exam already started.",
                "started_at": started_at.strftime("%Y-%m-%d %H:%M:%S"),
                "ends_at": end_time.strftime("%Y-%m-%d %H:%M:%S")
            }), 200

        started_at = now
        ends_at = started_at + timedelta(minutes=exam_duration)

        new_status = CandidateExamStatus(
            candidate_id=candidate.candidate_id,
            batch_id=batch.batch_id,
            started_at=started_at,
            ended_at=None,
            time_taken=None,
            correct_answers=0,
            wrong_answers=0,
            total_questions=0,
            marks_obtained=0,
            is_submitted=False,
            candidate_name=candidate.name,
            candidate_email=candidate.email
        )

        db.session.add(new_status)
        db.session.commit()

        return jsonify({
            "message": "Exam started successfully.",
            "started_at": started_at.strftime("%Y-%m-%d %H:%M:%S"),
            "ends_at": ends_at.strftime("%Y-%m-%d %H:%M:%S")
        }), 200


class SubmitExamAPI(MethodView):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate or not candidate.batches:
            return jsonify({"error": "Candidate not found or not assigned to any batch"}), 400

        batch = candidate.batches[0]
        exam_duration = batch.exam_duration

        status = CandidateExamStatus.query.filter_by(
            candidate_id=candidate.candidate_id,
            batch_id=batch.batch_id
        ).first()

        if not status:
            return jsonify({"error": "Exam not started"}), 400

        if status.is_submitted:
            return jsonify({
                "message": "You have already submitted the exam.",
                "correct_answers": status.correct_answers,
                "wrong_answers": status.wrong_answers,
                "marks_obtained": status.marks_obtained,
                "total_questions": status.total_questions,
                "time_taken": status.time_taken
            }), 200

        now = datetime.now(IST)
        started_at = status.started_at
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=IST)

        end_time = started_at + timedelta(minutes=exam_duration)
        if now > end_time:
            now = end_time

        answers = CandidateAnswer.query.filter_by(candidate_id=candidate.candidate_id).all()
        correct, wrong, total_marks = 0, 0, 0
        for ans in answers:
            if ans.selected_option:
                if ans.selected_option == ans.actual_answer:
                    correct += 1
                    total_marks += 1
                else:
                    wrong += 1

        total_questions = len(answers)
        time_taken_seconds = (now - started_at).total_seconds()
        time_taken = max(0, int(time_taken_seconds // 60))

        status.correct_answers = correct
        status.wrong_answers = wrong
        status.total_questions = total_questions
        status.marks_obtained = total_marks
        status.ended_at = now
        status.time_taken = time_taken
        status.is_submitted = True

        candidate.tab_switch_count = 0
        candidate.active_jti = None

        db.session.commit()

        return jsonify({
            "message": "Exam submitted successfully.",
            "correct_answers": correct,
            "wrong_answers": wrong,
            "marks_obtained": total_marks,
            "total_questions": total_questions,
            "time_taken": time_taken
        }), 200
class TabSwitching(MethodView):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        now = datetime.now(IST)

        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        candidate.tab_switch_count += 1
        db.session.commit()

        if not candidate.batches:
            return jsonify({"error": "Candidate not assigned to batch"}), 400

        batch = candidate.batches[0]
        status = CandidateExamStatus.query.filter_by(
            candidate_id=candidate.candidate_id,
            batch_id=batch.batch_id,
            is_submitted=False
        ).first()

        if not status:
            return jsonify({"error": "Exam not started or already submitted"}), 400

        started_at = status.started_at
        if started_at.tzinfo is None:
            started_at = started_at.replace(tzinfo=IST)

        if candidate.tab_switch_count >= 4:
            # Auto-submit logic
            answers = CandidateAnswer.query.filter_by(candidate_id=candidate.candidate_id).all()
            correct, wrong, total_marks = 0, 0, 0
            for ans in answers:
                if ans.selected_option:
                    if ans.selected_option == ans.actual_answer:
                        correct += 1
                        total_marks += 1
                    else:
                        wrong += 1

            total_questions = len(answers)
            time_taken_seconds = (now - started_at).total_seconds()
            time_taken = max(0, int(time_taken_seconds // 60))

            # Save to status
            status.correct_answers = correct
            status.wrong_answers = wrong
            status.total_questions = total_questions
            status.marks_obtained = total_marks
            status.ended_at = now
            status.time_taken = time_taken
            status.is_submitted = True

            candidate.active_jti = None
            db.session.commit()

            return jsonify({
                "message": "You switched tabs too many times. Exam is auto-submitted.",
                "tab_switch_count": candidate.tab_switch_count,
                "auto_submitted": True,
                "disqualified": True,
                "correct_answers": correct,
                "wrong_answers": wrong,
                "marks_obtained": total_marks,
                "total_questions": total_questions,
                "time_taken": time_taken
            }), 403

        return jsonify({
            "message": f"Warning: You have switched tabs {candidate.tab_switch_count} time(s). Max allowed is 3.",
            "tab_switch_count": candidate.tab_switch_count,
            "warning": True,
            "auto_submitted": False
        }), 200
