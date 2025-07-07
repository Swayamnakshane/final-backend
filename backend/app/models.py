from datetime import datetime, timedelta, timezone
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import JSON
from enum import Enum

db = SQLAlchemy()
utc_now = lambda: datetime.now(timezone.utc)

# ---------------- ENUMS ----------------
class GenderEnum(Enum):
    Male = "Male"
    Female = "Female"
    Other = "Other"

class DifficultyEnum(Enum):
    Easy = "Easy"
    Medium = "Medium"
    Hard = "Hard"

# ---------------- Association Table ----------------
candidate_batch = db.Table(
    'candidate_batch',
    db.Column('candidate_id', db.Integer, db.ForeignKey('candidates.candidate_id'), primary_key=True),
    db.Column('batch_id', db.Integer, db.ForeignKey('exam.batch_id'), primary_key=True)
)

# ---------------- Admin ----------------
class Admin(db.Model):
    __tablename__ = 'admins'
    admin_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.Enum(GenderEnum), nullable=True)
    password = db.Column(db.String(255), nullable=False)
    dob = db.Column(db.Date)
    mobile = db.Column(db.String(15))
    email = db.Column(db.String(100), unique=True, nullable=False)
    otp = db.Column(db.String(6))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    otp_expiry = db.Column(db.DateTime, default=lambda: utc_now() + timedelta(minutes=10))

    batches = db.relationship('Batch', backref='admin', lazy=True)
    mcqs_created = db.relationship('PythonMCQ', backref='creator', lazy=True)
    mcqs_assigned = db.relationship('AssignedMCQ', backref='assigner', lazy=True)

# ---------------- Exam Category ----------------
class ExamCategory(db.Model):
    __tablename__ = 'exam_categories'
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

# ---------------- Batch (Exam) ----------------
class Batch(db.Model):
    __tablename__ = 'exam'
    batch_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    keywords = db.Column(JSON)
    total_candidates = db.Column(db.Integer, default=0)
    exam_duration = db.Column(db.Integer, default=60)  # in minutes
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('admins.admin_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    is_active = db.Column(db.Boolean, default=True)

    category_id = db.Column(db.Integer, db.ForeignKey('exam_categories.id'))
    category = db.relationship('ExamCategory', backref='exam', lazy=True)

    candidates = db.relationship('Candidate', secondary=candidate_batch, back_populates='batches', lazy=True)
    rounds = db.relationship('InterviewRound', backref='batch', lazy=True)
    exam_statuses = db.relationship('CandidateExamStatus', backref='batch', lazy=True)
    questions = db.relationship('BatchQuestion', backref='batch', lazy=True)
    mcqs = db.relationship('PythonMCQ', backref='batch', lazy=True)

# ---------------- Candidate ----------------
class Candidate(db.Model):
    __tablename__ = 'candidates'
    candidate_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)
    last_login_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    active_jti = db.Column(db.String(36), nullable=True)
    tab_switch_count = db.Column(db.Integer, default=0)

    # Profile
    education = db.Column(db.String(100))
    college_name = db.Column(db.String(255))
    group = db.Column(db.String(100))
    year_of_passing = db.Column(db.Integer)
    job_role = db.Column(db.String(100))
    company_name = db.Column(db.String(255))
    job_description = db.Column(db.Text)
    from_date = db.Column(db.Date)
    to_date = db.Column(db.Date)
    currently_working = db.Column(db.Boolean, default=False)
    skills = db.Column(db.Text)
    student_bio = db.Column(db.Text)
    address = db.Column(db.Text)

    # Password Reset / OTP
    otp = db.Column(db.String(10))
    new_password = db.Column(db.String(255))
    confirm_password = db.Column(db.String(255))

    # Relationships
    batches = db.relationship('Batch', secondary=candidate_batch, back_populates='candidates', lazy=True)
    assigned_mcqs = db.relationship('AssignedMCQ', backref='candidate', lazy=True)
    answers = db.relationship('CandidateAnswer', backref='candidate', lazy=True)
    exam_statuses = db.relationship('CandidateExamStatus', backref='candidate', lazy=True)

# ---------------- Interview Round ----------------
class InterviewRound(db.Model):
    __tablename__ = 'interview_rounds'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey('exam.batch_id'), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

# ---------------- Python MCQs ----------------
class PythonMCQ(db.Model):
    __tablename__ = 'mcqs'
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    options = db.Column(JSON, nullable=False)
    answer = db.Column(db.String(1), nullable=False)
    topic = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.Enum(DifficultyEnum), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)
    category_name = db.Column(db.String(100))

    batch_id = db.Column(db.Integer, db.ForeignKey('exam.batch_id'))
    created_by = db.Column(db.Integer, db.ForeignKey('admins.admin_id'))

    category_id = db.Column(db.Integer, db.ForeignKey('exam_categories.id'))
    category = db.relationship('ExamCategory', backref='mcqs', lazy=True)

    answers = db.relationship('CandidateAnswer', backref='question', lazy=True)
    assigned_mcqs = db.relationship('AssignedMCQ', backref='question', lazy=True)

# ---------------- Candidate Answer ----------------
class CandidateAnswer(db.Model):
    __tablename__ = 'candidate_answers'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.candidate_id'), nullable=False, index=True)
    candidate_name = db.Column(db.String(100))  # ✅ Add this line
    candidate_email = db.Column(db.String(100),)  # ✅ Add this line
    question_id = db.Column(db.Integer, db.ForeignKey('mcqs.id'), nullable=False, index=True)
    actual_answer = db.Column(db.String(1), nullable=False)
    selected_option = db.Column(db.String(1))
    is_saved = db.Column(db.Boolean, default=False)
    total_marks = db.Column(db.Integer, default=0)
    answered_at = db.Column(db.DateTime, default=utc_now)


# ---------------- Candidate Exam Status ----------------
class CandidateExamStatus(db.Model):
    __tablename__ = 'candidate_exam_status'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.candidate_id'), nullable=False)
    candidate_name = db.Column(db.String(100))  # ✅ Add this line
    candidate_email = db.Column(db.String(100))  # ✅ Add this line
    batch_id = db.Column(db.Integer, db.ForeignKey('exam.batch_id'), nullable=False)
    started_at = db.Column(db.DateTime, default=utc_now)
    ended_at = db.Column(db.DateTime)
    correct_answers = db.Column(db.Integer, default=0)
    wrong_answers = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=0)
    marks_obtained = db.Column(db.Integer, default=0)
    time_taken = db.Column(db.Integer, default=0)  # In minutes
    is_submitted = db.Column(db.Boolean, default=False)

# ---------------- Batch Question ----------------
class BatchQuestion(db.Model):
    __tablename__ = 'exam_questions'
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('exam.batch_id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('mcqs.id'), nullable=False)

# ---------------- Assigned MCQs ----------------
class AssignedMCQ(db.Model):
    __tablename__ = 'assigned_mcqs'
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.candidate_id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('mcqs.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=utc_now)
    assigned_by = db.Column(db.Integer, db.ForeignKey('admins.admin_id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('candidate_id', 'question_id', name='uq_candidate_question'),
    )
