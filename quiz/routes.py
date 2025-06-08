from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from model.quizdto import QuizDto
from model.questiondto import QuestionDto
from model.attemptdto import AttemptDto
from db import srp
from sirope import OID

# Inicialización del Blueprint para los quizzes
quiz_bp = Blueprint('quiz', __name__)

# Ruta para ver todos los quizzes del usuario
@quiz_bp.route("/quizzes")
@login_required
def quizzes():
    # Obtener todos los quizzes creados por el usuario logueado
    quizzes = srp.filter(QuizDto, lambda q: q.user_email == current_user.email)
    return render_template("quizzes.html", quizzes=quizzes)

# Ruta para crear un nuevo quiz
@quiz_bp.route("/create_quiz", methods=["GET", "POST"])
@login_required
def create_quiz():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        user_email = current_user.email  # Obtener el email del usuario logueado

        # Crear un nuevo quiz y guardarlo en la base de datos
        quiz = QuizDto(title, description, user_email)
        oid = srp.save(quiz)
        quiz._oid = oid  # Guarda el OID real asignado por Sirope
        srp.save(quiz)   # Guarda de nuevo para persistir el OID

        # Redirigir al usuario a la página de añadir preguntas al quiz recién creado
        return redirect(url_for("quiz.add_question", quiz_id=quiz.title))

    return render_template("create_quiz.html")


# Ruta para ver los detalles de un quiz y resolverlo
@quiz_bp.route("/solve_quiz/<quiz_id>", methods=["GET", "POST"])
@login_required
def solve_quiz(quiz_id):
    quiz = srp.find_first(QuizDto, lambda q: q.title == quiz_id)
    questions = [srp.load(qid) for qid in quiz.questions_oids]
    question_index = int(request.args.get('question_index', 0))

    # Inicializa las respuestas en la sesión si es la primera pregunta
    if question_index == 0 and request.method == "GET":
        session['quiz_answers'] = []

    if request.method == "POST":
        selected_option = int(request.form.get("selected_option"))
        answers = session.get('quiz_answers', [])
        answers.append(selected_option)
        session['quiz_answers'] = answers

        if question_index + 1 < len(questions):
            # Siguiente pregunta
            return redirect(url_for("quiz.solve_quiz", quiz_id=quiz_id, question_index=question_index + 1))
        else:
            # Última pregunta: calcular score y guardar intento
            score = 0
            for i, question in enumerate(questions):
                if answers[i] == question.correct_option:
                    score += 1

            attempt = AttemptDto(current_user.email, quiz.title, answers, score)
            srp.save(attempt)
            session.pop('quiz_answers', None)
            flash(f"Tu puntuación es: {score}/{len(questions)}")
            return redirect(url_for("quiz.view_attempts", quiz_id=quiz_id))

    return render_template("solve_quiz.html", quiz=quiz, questions=questions, question_index=question_index)



# Ruta para ver los intentos previos de un usuario
@quiz_bp.route("/view_attempts/<quiz_id>")
@login_required
def view_attempts(quiz_id):
    attempts = AttemptDto.find_by_user(srp, current_user.email)
    attempts_for_quiz = [attempt for attempt in attempts if attempt.quiz_title == quiz_id]
    attempts_for_quiz.sort(key=lambda a: a.date, reverse=True)
    quiz = srp.find_first(QuizDto, lambda q: q.title == quiz_id)
    questions = [srp.load(qid) for qid in quiz.questions_oids]
    return render_template("view_attempts.html", attempts=attempts_for_quiz, quiz_title=quiz_id, questions=questions)


# Ruta para editar un quiz
@quiz_bp.route("/edit_quiz/<quiz_id>", methods=["GET", "POST"])
@login_required
def edit_quiz(quiz_id):
    quiz = srp.find_first(QuizDto, lambda q: q.title == quiz_id)
    questions = [srp.load(qid) for qid in quiz.questions_oids]

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        if title and description:
            quiz._title = title
            quiz._description = description
            srp.save(quiz)
            flash("Quiz actualizado exitosamente.")
            return redirect(url_for("quiz.quizzes"))
        else:
            flash("Por favor, completa todos los campos.")

    return render_template("edit_quiz.html", quiz=quiz, questions=questions)

# Ruta para editar una pregunta
@quiz_bp.route("/edit_question/<question_oid>", methods=["GET", "POST"])
@login_required
def edit_question(question_oid):
    question = srp.load(OID.from_text(question_oid))
    if request.method == "POST":
        question_text = request.form["question_text"]
        options = [
            request.form["option_a"],
            request.form["option_b"],
            request.form["option_c"],
            request.form["option_d"]
        ]
        correct_option = int(request.form["correct_option"])
        question._question_text = question_text
        question._options = options
        question._correct_option = correct_option
        srp.save(question)
        flash("Pregunta actualizada exitosamente.")
        # Redirige de vuelta al quiz de edición
        return redirect(url_for("quiz.edit_quiz", quiz_id=request.form["quiz_id"]))
    return render_template("edit_question.html", question=question)

# Ruta para eliminar un quiz
@quiz_bp.route("/delete_quiz/<quiz_id>", methods=["POST"])
@login_required
def delete_quiz(quiz_id):
    # Buscar el quiz por título
    quiz = srp.find_first(QuizDto, lambda q: q.title == quiz_id)

    if quiz and quiz.user_email == current_user.email:
        # Eliminar preguntas asociadas
        for qid in quiz.questions_oids:
            srp.delete(qid)
        # Eliminar el quiz usando su OID real
        if quiz.oid is not None:
            srp.delete(quiz.oid)
            flash("Quiz eliminado exitosamente.")
        else:
            flash("No se pudo eliminar el quiz: OID no encontrado.")
    else:
        flash("No tienes permiso para eliminar este quiz.")

    return redirect(url_for("quiz.quizzes"))



# Ruta para añadir preguntas a un quiz
@quiz_bp.route("/add_question/<quiz_id>", methods=["GET", "POST"])
@login_required
def add_question(quiz_id):
    quiz = srp.find_first(QuizDto, lambda q: q.title == quiz_id)

    if request.method == "POST":
        action = request.form.get("action")
        # Guarda la pregunta si los campos están presentes (evita guardar si el usuario no ha rellenado nada)
        if all(request.form.get(f) for f in ["question_text", "option_a", "option_b", "option_c", "option_d", "correct_option"]):
            question_text = request.form["question_text"]
            options = [
                request.form["option_a"],
                request.form["option_b"],
                request.form["option_c"],
                request.form["option_d"]
            ]
            correct_option = int(request.form["correct_option"])
            question = QuestionDto(question_text, options, correct_option)
            srp.save(question)
            quiz.add_question_oid(question.__oid__)
            srp.save(quiz)

        if action == "add":
            return redirect(url_for("quiz.add_question", quiz_id=quiz_id))
        elif action == "finish":
            flash("Quiz completado y guardado correctamente.")
            return redirect(url_for("quiz.quizzes"))

    return render_template("add_question.html", quiz=quiz)

@quiz_bp.route("/solve_others_quizzes", methods=["GET", "POST"])
@login_required
def solve_others_quizzes():
    # Obtener todos los quizzes (propios o de otros usuarios)
    quizzes = srp.filter(QuizDto, lambda q: q.user_email == current_user.email or q.user_email != current_user.email)

    if request.method == "POST":
        # Acceder al quiz seleccionado
        quiz_id = request.form["quiz_id"]
        return redirect(url_for("quiz.solve_quiz", quiz_id=quiz_id))

    return render_template("solve_others_quizzes.html", quizzes=quizzes)

@quiz_bp.route("/cancel_quiz/<quiz_id>")
@login_required
def cancel_quiz(quiz_id):
    quiz = srp.find_first(QuizDto, lambda q: q.title == quiz_id)
    if quiz and quiz.user_email == current_user.email:
        # Elimina preguntas asociadas
        for qid in quiz.questions_oids:
            srp.delete(qid)
        # Elimina el quiz
        if quiz.oid is not None:
            srp.delete(quiz.oid)
    flash("Quiz cancelado.")
    return redirect(url_for("index"))
