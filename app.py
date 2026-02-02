from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import render_template,request,url_for,redirect,abort,flash,jsonify,session,current_app
from flask_migrate import Migrate
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from models import Notification,db
from urllib.parse import quote

app=Flask(__name__)

@app.before_request
def auto_admin_session():
    if request.path.startswith("/admin"):
        session["is_admin"] = True


app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
app.config['SECRET_KEY'] = 'any-random-string-here-for-now'
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['MAX_CONTENT_LENGTH']= 3*1024*1024 #3MB

db.init_app(app)
migrate = Migrate(app, db)



class Entries(db.Model):
    __tablename__="entries"
    id=db.Column(db.Integer,primary_key=True)
    #This serves as index to retrieve the required data
    patient_name=db.Column(db.String(100), nullable=False, index=True)

    image_name = db.Column(db.String(255), nullable=False)
    narrative = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@app.route("/admin")
def admin_dashboard():
    return render_template("admin.html")

def require_admin():
    admin_key = request.headers.get("X-ADMIN-KEY")
    expected_key = os.environ.get("ADMIN_KEY")
    if not expected_key or admin_key != expected_key:
        abort(403)


@app.route("/api/admin/notifications/unread-count", methods=["GET"])
def unread_notification_count():
    require_admin()
    count = Notification.query.filter_by(seen=False).count()
    return jsonify({"unread_count": count})

@app.route("/api/admin/notifications", methods=["GET"])
def get_notifications():
    require_admin()
    notifications = (
        Notification.query
        .order_by(Notification.created_at.desc())
        .limit(20)
        .all()
    )

    return jsonify([n.to_dict() for n in notifications])

@app.route("/api/admin/notifications/mark-seen", methods=["POST"])
def mark_notifications_seen():
    require_admin()
    Notification.query.filter_by(seen=False).update({"seen": True})
    db.session.commit()
    return jsonify({"status": "ok"})

@app.errorhandler(413)
def file_too_large(error):
    flash("Image size must be less than 3MB")
    return redirect(url_for('upload'))

@app.route('/')
def home():
    return render_template('index.html') 



@app.route('/upload', methods=['GET', 'POST'])
def upload():
    patient_name = None
    if request.method == 'POST':
        # Get form data
        patient_name = request.form.get('patient_name')
        narrative = request.form.get('narrative')
        file = request.files.get('patient_image')

        if file and patient_name:

            try:
                # Secure the file name
                filename = secure_filename(file.filename)
                upload_folder = current_app.config['UPLOAD_FOLDER']

                os.makedirs(upload_folder, exist_ok=True)

                if file.mimetype not in {"image/jpeg", "image/png", "image/jpg"}:
                    abort(400, "Unsupported file type")

                name, ext = os.path.splitext(filename)
                timestamp = str(datetime.utcnow().timestamp()).replace(".", "")
                filename = f"{timestamp}_{name}{ext}"

                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)



                new_entry = Entries(
                    patient_name=patient_name,
                    image_name=filename,
                    narrative=narrative
                )

                db.session.add(new_entry)
                db.session.commit()

                now = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")

                notification = Notification(
                    patient_name=patient_name,
                    image_name=filename,
                    title=patient_name,
                    message=f"Uploaded {filename} at {now}",
                    seen=False
                )

                db.session.add(notification)
                db.session.commit()

                flash("Upload successful! File saved and entry recorded in the database.", "success")
                return redirect(url_for("gallery", search_term=quote(patient_name)))
            
            except Exception as e:
                db.session.rollback()  # Undo DB changes if it crashes halfway
                current_app.logger.error(f"An error occurred during upload: {e}", exc_info=True)
                return "An unexpected error occurred. Please try again later.", 500
        else:
            flash("Please provide a name and select a file.", "error")
            return redirect(url_for('upload'))

    return render_template(
    "upload.html",
    max_file_size=app.config['MAX_CONTENT_LENGTH'])


@app.route('/search')
def search():
    query = request.args.get('q') # Make sure this matches name="q" in your HTML
    if query:
        return redirect(url_for('gallery', search_term=query))
    return redirect(url_for('home'))

@app.route('/gallery/<path:search_term>')
def gallery(search_term):
    user_entries = Entries.query.filter(Entries.patient_name.ilike(f"%{search_term}%")).all()
    
    return render_template('gallery.html', entries=user_entries, patient=search_term)
    

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=False)
