from flask import Blueprint, render_template, send_file
from decorators import admin_required, login_required
from database import Database
import pandas as pd
import io
from datetime import datetime, timedelta

admin_analysis_bp = Blueprint("admin_analysis", __name__)

# ============================
# ANALYTICS DASHBOARD
# ============================
@admin_analysis_bp.route("/admin/analysis")
@login_required
@admin_required
def analysis_dashboard():
    db = Database.get_db()

    # 1. BASIC COUNTS
    total_images = db.uploads.count_documents({"is_active": True})
    total_users = db.users.count_documents({})

    # 2. GLOBAL SENTIMENT STATS (PIE CHART)
    sentiment_pipeline = [
        {"$match": {"is_active": True}},
        {"$group": {"_id": "$sentiment", "count": {"$sum": 1}}}
    ]
    sentiment_results = list(db.uploads.aggregate(sentiment_pipeline))

    stats = {"Positive": 0, "Neutral": 0, "Negative": 0}
    for row in sentiment_results:
        if row["_id"]:
            key = row["_id"].title()
            if key in stats:
                stats[key] += row["count"]

    percentages = {
        k: round((v / total_images) * 100, 1) if total_images > 0 else 0
        for k, v in stats.items()
    }

    pie_data = [stats["Positive"], stats["Neutral"], stats["Negative"]]

    # 3. 7-DAY UPLOAD TREND (Robust created_at logic)
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    start_date = today - timedelta(days=6)

    trend_pipeline = [
        {"$match": {"is_active": True, "created_at": {"$gte": start_date}}},
        {"$project": {"_id": 0, "date_str": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}}}}
    ]
    try:
        raw_trend_data = list(db.uploads.aggregate(trend_pipeline))
    except Exception:
        raw_trend_data = []

    date_counts = {}
    for item in raw_trend_data:
        d_str = item.get('date_str')
        if d_str: date_counts[d_str] = date_counts.get(d_str, 0) + 1

    chart_labels = []
    chart_values = []
    current_itr = start_date
    for _ in range(7):
        key = current_itr.strftime("%Y-%m-%d")
        chart_labels.append(current_itr.strftime("%d %b"))
        chart_values.append(date_counts.get(key, 0))
        current_itr += timedelta(days=1)

    # 4. USER PERFORMANCE TABLE
    user_pipeline = [
        {"$match": {"is_active": True}},
        {
            "$group": {
                "_id": "$username",
                "upload_count": {"$sum": 1},
                "pos_count": {"$sum": {"$cond": [{"$eq": ["$sentiment", "Positive"]}, 1, 0]}},
                "neu_count": {"$sum": {"$cond": [{"$eq": ["$sentiment", "Neutral"]}, 1, 0]}},
                "neg_count": {"$sum": {"$cond": [{"$eq": ["$sentiment", "Negative"]}, 1, 0]}},
                "last_active": {"$max": "$created_at"}
            }
        },
        {"$sort": {"upload_count": -1}}
    ]
    users_report = list(db.uploads.aggregate(user_pipeline))

    return render_template(
        "admin_analysis_dashboard.html",
        total_images=total_images,
        total_users=total_users,
        stats=stats,
        percentages=percentages,
        users_report=users_report,
        chart_labels=chart_labels,
        chart_values=chart_values,
        pie_data=pie_data
    )

# ============================
# EXPORT EXCEL
# ============================
@admin_analysis_bp.route("/admin/export_excel")
@login_required
@admin_required
def export_excel():
    db = Database.get_db()
    pipeline = [
        {"$match": {"is_active": True}},
        {
            "$group": {
                "_id": "$username",
                "Total_Uploads": {"$sum": 1},
                "Positive_Sentiments": {"$sum": {"$cond": [{"$eq": ["$sentiment", "Positive"]}, 1, 0]}},
                "Neutral_Sentiments": {"$sum": {"$cond": [{"$eq": ["$sentiment", "Neutral"]}, 1, 0]}},
                "Negative_Sentiments": {"$sum": {"$cond": [{"$eq": ["$sentiment", "Negative"]}, 1, 0]}}
            }
        }
    ]
    data = list(db.uploads.aggregate(pipeline))
    if not data: return "No data available", 404

    df = pd.DataFrame(data)
    df.rename(columns={"_id": "Username"}, inplace=True)
    df["Health_Score_%"] = (df["Positive_Sentiments"] / df["Total_Uploads"] * 100).round(1)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="User Sentiment Analysis")
    output.seek(0)
    
    return send_file(output, download_name=f"User_Analysis_{datetime.utcnow().strftime('%Y-%m-%d')}.xlsx", as_attachment=True)