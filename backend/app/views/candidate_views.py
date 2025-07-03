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

class CandidateLoginAPI(MethodView):
    def post(self):
        data = request.get_json()
        if not data:
            return jsonify({"message": "No input data provided"}), 400

        user_id = data.get("user_id")
        password = data.get("password")

        if not user_id or not password:
            return jsonify({"message": "User ID and password are required"}), 400

        # Find candidate
        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate or candidate.password != password:
            return jsonify({"message": "Invalid User ID or password"}), 401

        # Update last login time
        candidate.last_login_at = datetime.now(IST)
        db.session.commit()

        # Get first assigned batch
        batch_id = candidate.batches[0].batch_id if candidate.batches else None

        # Check if exam already submitted
        is_submitted = False
        if batch_id:
            exam_status = CandidateExamStatus.query.filter_by(
                candidate_id=candidate.candidate_id,
                batch_id=batch_id
            ).first()
            is_submitted = exam_status.is_submitted if exam_status else False

        # Generate access token
        access_token = create_access_token(identity=candidate.user_id)

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "candidate_name": candidate.name,
            "batch_id": batch_id,
            "is_submitted": is_submitted
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

        batch = candidate.batches[0]  # Assuming one batch per candidate for now

        return jsonify({
            "candidate_name": candidate.name,
            "batch_title": batch.title,
            "exam_start_date": batch.start_date.strftime("%d-%m-%Y"),
            "exam_end_date": batch.end_date.strftime("%d-%m-%Y"),
            "exam_duration": batch.exam_duration  # in minutes
        }), 200


class CandidateMcqsAPI(MethodView):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()

        candidate = Candidate.query.filter_by(user_id=user_id).first()
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

        # Fetch the actual MCQ to get the correct answer
        question = PythonMCQ.query.get(question_id)
        if not question:
            return jsonify({"error": "Question not found"}), 404

        actual_answer = question.answer

        # Save or update the answer
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



IST = timezone('Asia/Kolkata')

class StartExamAPI(MethodView):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()

        # Get candidate
        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        # Ensure candidate has a batch
        if not candidate.batches or len(candidate.batches) == 0:
            return jsonify({"error": "Candidate not assigned to any batch"}), 400

        # Assuming only one batch assigned
        batch = candidate.batches[0]

        # Check if exam is already submitted
        submitted_status = CandidateExamStatus.query.filter_by(
            candidate_id=candidate.candidate_id,
            batch_id=batch.batch_id,
            is_submitted=True
        ).first()

        if submitted_status:
            return jsonify({"error": "You have already submitted this exam."}), 403

        # Check if exam is already started but not submitted
        ongoing_status = CandidateExamStatus.query.filter_by(
            candidate_id=candidate.candidate_id,
            batch_id=batch.batch_id,
            is_submitted=False
        ).first()

        if ongoing_status:
            return jsonify({
                "message": "Exam already started.",
                "started_at": ongoing_status.started_at.strftime("%Y-%m-%d %H:%M:%S")
            }), 200

        # Start new exam session
        new_status = CandidateExamStatus(
            candidate_id=candidate.candidate_id,
            batch_id=batch.batch_id,
            started_at=datetime.now(IST),
            is_submitted=False
        )
        db.session.add(new_status)
        db.session.commit()

        return jsonify({"message": "Exam started successfully."}), 200


IST = timezone("Asia/Kolkata")

class SubmitExamAPI(MethodView):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()

        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        if not candidate.batches:
            return jsonify({"error": "Candidate not assigned to any batch"}), 400

        batch = candidate.batches[0]

        status = CandidateExamStatus.query.filter_by(
            candidate_id=candidate.candidate_id,
            batch_id=batch.batch_id
        ).first()

        if not status:
            return jsonify({"error": "Exam session not started"}), 404

        if status.is_submitted:
            return jsonify({"message": "Exam already submitted"}), 200

        answers = CandidateAnswer.query.filter_by(candidate_id=candidate.candidate_id).all()

        correct = 0
        wrong = 0
        total_marks = 0
        total_questions = len(answers)

        for ans in answers:
            if ans.selected_option:
                if ans.selected_option == ans.actual_answer:
                    correct += 1
                    total_marks += 1
                else:
                    wrong += 1

        ended_at = datetime.now(IST)

        # Convert ended_at to naive if started_at is naive
        time_taken = int(((ended_at.replace(tzinfo=None)) - status.started_at).total_seconds() // 60)

        status.correct_answers = correct
        status.wrong_answers = wrong
        status.total_questions = total_questions
        status.marks_obtained = total_marks
        status.ended_at = ended_at
        status.time_taken = time_taken
        status.is_submitted = True

        db.session.commit()

        return jsonify({
            "message": "Exam submitted successfully",
            "correct_answers": correct,
            "wrong_answers": wrong,
            "marks_obtained": total_marks,
            "total_questions": total_questions,
            "time_taken": time_taken
        }), 200


# class TabSwitching(MethodView):
#     @jwt_required()
    

#     def log_tab_switch():
#         user_id = get_jwt_identity()
#         timestamp = datetime.now()

#         candidate = Candidate.query.filter_by(user_id=user_id).first()
#         if not candidate:
#             return jsonify({"error": "Candidate not found"}), 404

#         candidate.tab_switch_count += 1
#         db.session.commit()

#         # Optional: Also log in a separate table or MongoDB if needed
#         # db.tab_switch_logs.insert_one({ "user_id": user_id, "timestamp": timestamp })

#         # Example: Disqualify after 3 tab switches
#         if candidate.tab_switch_count >= 3:
#             candidate.is_active = False
#             db.session.commit()
#             return jsonify({
#                 "message": "Disqualified for switching tabs too many times.",
#                 "disqualified": True
#             }), 403

#         return jsonify({
#             "message": "Tab switch logged",
#             "tab_switch_count": candidate.tab_switch_count,
#             "disqualified": False
#         }), 200

class TabSwitching(MethodView):
    @jwt_required()
    def post(self):
        user_id = get_jwt_identity()
        timestamp = datetime.now()

        candidate = Candidate.query.filter_by(user_id=user_id).first()
        if not candidate:
            return jsonify({"error": "Candidate not found"}), 404

        candidate.tab_switch_count += 1
        db.session.commit()

        return jsonify({
            "message": "Tab switch logged",
            "tab_switch_count": candidate.tab_switch_count
        }), 200
