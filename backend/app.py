#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from flask import Flask, jsonify, request
from sqlalchemy import text, event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_ENGINE_OPTIONS
from models import db, Brand, Influencer, Campaign, campaign_influencers
from flask_cors import CORS
from datetime import datetime

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = SQLALCHEMY_ENGINE_OPTIONS

db.init_app(app)


# SQLite ships with foreign-key enforcement OFF by default — the ON DELETE CASCADE
# clauses in models.py are inert without this PRAGMA, and a bad brand_id on insert
# would silently succeed instead of raising IntegrityError. 
@event.listens_for(Engine, "connect")
def _enable_sqlite_foreign_keys(dbapi_conn, conn_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


# Upgrade SQLite's default BEGIN DEFERRED to BEGIN IMMEDIATE for every transaction.
# DEFERRED lets two concurrent writers both open a transaction, then race to
# upgrade to a write lock — the loser gets SQLITE_BUSY mid-transaction. IMMEDIATE
# takes the write lock up front, so the second writer blocks cleanly at BEGIN.
# This is the concurrency story behind the SERIALIZABLE choice (see config.py).
with app.app_context():
    @event.listens_for(db.engine, "begin")
    def _begin_immediate(conn):
        conn.exec_driver_sql("BEGIN IMMEDIATE")

#----------------------------------------------------------------------------#
# Helpers
#----------------------------------------------------------------------------#

def campaign_to_dict(c):
    return {
        "id": c.id,
        "title": c.title,
        "description": c.description,
        "budget": c.budget,
        "start_date": c.start_date.isoformat(),
        "end_date": c.end_date.isoformat(),
        "brand_id": c.brand_id,
        "brand_name": c.brand.name,
        "platform": c.platform,
        "status": c.status,
        "influencers": [
            {
                "id": i.id,
                "name": i.name,
                "platform": i.platform,
                "follower_count": i.follower_count,
            }
            for i in c.influencers
        ],
    }

#----------------------------------------------------------------------------#
# Routes — Brands (read-only, for dropdowns)
#----------------------------------------------------------------------------#

@app.route('/api/brands', methods=['GET'])
def get_brands():
    brands = Brand.query.order_by(Brand.name).all()
    return jsonify([
        {"id": b.id, "name": b.name, "industry": b.industry, "contact_email": b.contact_email}
        for b in brands
    ])

#----------------------------------------------------------------------------#
# Routes — Influencers (read-only, for dropdowns / assignment)
#----------------------------------------------------------------------------#

@app.route('/api/influencers', methods=['GET'])
def get_influencers():
    influencers = Influencer.query.order_by(Influencer.name).all()
    return jsonify([
        {
            "id": i.id,
            "name": i.name,
            "email": i.email,
            "platform": i.platform,
            "follower_count": i.follower_count,
            "engagement_rate": i.engagement_rate,
        }
        for i in influencers
    ])

#----------------------------------------------------------------------------#
# Routes — Campaigns CRUD
#----------------------------------------------------------------------------#

@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    campaigns = Campaign.query.order_by(Campaign.start_date.desc()).all()
    return jsonify([campaign_to_dict(c) for c in campaigns])


@app.route('/api/campaigns/<int:campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    c = Campaign.query.get_or_404(campaign_id)
    return jsonify(campaign_to_dict(c))


@app.route('/api/campaigns', methods=['POST'])
def create_campaign():
    data = request.get_json()

    # Single transaction: insert campaign + populate join table atomically.
    # If the influencer lookup or the join-table insert fails, rollback discards
    # the half-built campaign. Without this, a failure between db.session.add and
    # commit would leave a campaign with no influencers (or, worse, partially
    # populated join rows on retry).
    try:
        campaign = Campaign(
            title=data['title'],
            description=data.get('description', ''),
            budget=data['budget'],
            start_date=datetime.strptime(data['start_date'], '%Y-%m-%d').date(),
            end_date=datetime.strptime(data['end_date'], '%Y-%m-%d').date(),
            brand_id=data['brand_id'],
            platform=data['platform'],
            status=data.get('status', 'draft'),
        )

        influencer_ids = data.get('influencer_ids', [])
        if influencer_ids:
            influencers = Influencer.query.filter(Influencer.id.in_(influencer_ids)).all()
            campaign.influencers = influencers

        db.session.add(campaign)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create campaign", "detail": str(e)}), 500

    return jsonify(campaign_to_dict(campaign)), 201


@app.route('/api/campaigns/<int:campaign_id>', methods=['PUT'])
def update_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    data = request.get_json()

    # Single transaction: column updates and join-table replacement happen
    # atomically. Replacing influencers is a delete-then-insert under the hood;
    # rolling back on failure prevents leaving a campaign with zero influencers
    # if the new inserts fail.
    try:
        campaign.title = data.get('title', campaign.title)
        campaign.description = data.get('description', campaign.description)
        campaign.budget = data.get('budget', campaign.budget)
        campaign.platform = data.get('platform', campaign.platform)
        campaign.status = data.get('status', campaign.status)
        campaign.brand_id = data.get('brand_id', campaign.brand_id)

        if 'start_date' in data:
            campaign.start_date = datetime.strptime(data['start_date'], '%Y-%m-%d').date()
        if 'end_date' in data:
            campaign.end_date = datetime.strptime(data['end_date'], '%Y-%m-%d').date()

        if 'influencer_ids' in data:
            influencers = Influencer.query.filter(Influencer.id.in_(data['influencer_ids'])).all()
            campaign.influencers = influencers

        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update campaign", "detail": str(e)}), 500

    return jsonify(campaign_to_dict(campaign))


@app.route('/api/campaigns/<int:campaign_id>', methods=['DELETE'])
def delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    try:
        db.session.delete(campaign)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete campaign", "detail": str(e)}), 500
    return jsonify({"message": "Campaign deleted"}), 200

#----------------------------------------------------------------------------#
# Routes — Search (raw SQL, parameterized)
#----------------------------------------------------------------------------#

# Demonstrates SQL-injection protection with raw SQL. Every other write/read
# above goes through the SQLAlchemy ORM, which parameterizes automatically; this
# endpoint uses sqlalchemy.text() with a bound parameter (:pattern) so we can
# point at an explicit prepared-statement example.
#
# Why this is safe even with attacker-controlled input:
#   q = "'; DROP TABLE campaigns; --"
# becomes a single bound string value, not appended SQL. The driver sends the
# query and the parameter separately; SQLite never parses `q` as SQL.
#
# What would be UNSAFE:
#   db.session.execute(text(f"... WHERE title LIKE '%{q}%'"))  # f-string = injection.
@app.route('/api/campaigns/search', methods=['GET'])
def search_campaigns():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])

    stmt = text("""
        SELECT id, title, brand_id, platform, status, budget,
               start_date, end_date
        FROM campaigns
        WHERE title LIKE :pattern OR description LIKE :pattern
        ORDER BY start_date DESC
    """)
    rows = db.session.execute(stmt, {"pattern": f"%{q}%"}).mappings().all()
    return jsonify([
        {
            "id": r["id"],
            "title": r["title"],
            "brand_id": r["brand_id"],
            "platform": r["platform"],
            "status": r["status"],
            "budget": r["budget"],
            "start_date": r["start_date"],
            "end_date": r["end_date"],
        }
        for r in rows
    ])

#----------------------------------------------------------------------------#
# Routes — Report
#----------------------------------------------------------------------------#

@app.route('/api/reports/campaigns', methods=['GET'])
def campaign_report():
    query = Campaign.query

    # Filter by date range
    start = request.args.get('start_date')
    end = request.args.get('end_date')
    if start:
        query = query.filter(Campaign.start_date >= datetime.strptime(start, '%Y-%m-%d').date())
    if end:
        query = query.filter(Campaign.end_date <= datetime.strptime(end, '%Y-%m-%d').date())

    # Filter by brand
    brand_id = request.args.get('brand_id')
    if brand_id:
        query = query.filter(Campaign.brand_id == int(brand_id))

    # Filter by platform
    platform = request.args.get('platform')
    if platform:
        query = query.filter(Campaign.platform == platform)

    # Filter by status
    status = request.args.get('status')
    if status:
        query = query.filter(Campaign.status == status)

    campaigns = query.order_by(Campaign.start_date.desc()).all()
    campaign_list = [campaign_to_dict(c) for c in campaigns]

    # Compute statistics
    total = len(campaigns)
    if total > 0:
        avg_budget = sum(c.budget for c in campaigns) / total
        total_budget = sum(c.budget for c in campaigns)
        avg_influencers = sum(len(c.influencers) for c in campaigns) / total
        total_influencers = sum(len(c.influencers) for c in campaigns)
    else:
        avg_budget = 0
        total_budget = 0
        avg_influencers = 0
        total_influencers = 0

    return jsonify({
        "campaigns": campaign_list,
        "statistics": {
            "total_campaigns": total,
            "average_budget": round(avg_budget, 2),
            "total_budget": round(total_budget, 2),
            "average_influencers_per_campaign": round(avg_influencers, 2),
            "total_influencers_assigned": total_influencers,
        }
    })

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
