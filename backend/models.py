from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Brand(db.Model):
    __tablename__ = 'brands'

    id = db.Column(db.Integer, primary_key=True)
    # Indexed: GET /api/brands orders by name to populate the brand dropdown
    # in the campaign form and report filter.
    name = db.Column(db.String(100), nullable=False, index=True)
    industry = db.Column(db.String(100), nullable=False)
    contact_email = db.Column(db.String(120), nullable=False)

    campaigns = db.relationship('Campaign', backref='brand', lazy=True)


class Influencer(db.Model):
    __tablename__ = 'influencers'

    id = db.Column(db.Integer, primary_key=True)
    # Indexed: GET /api/influencers orders by name to populate the influencer
    # multi-select checkbox list in the campaign form.
    name = db.Column(db.String(100), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    platform = db.Column(db.String(50), nullable=False)  # Instagram, YouTube, TikTok, Twitter
    follower_count = db.Column(db.Integer, nullable=False, default=0)
    engagement_rate = db.Column(db.Float, nullable=False, default=0.0)


campaign_influencers = db.Table(
    'campaign_influencers',
    db.Column('campaign_id', db.Integer, db.ForeignKey('campaigns.id', ondelete='CASCADE'), primary_key=True),
    db.Column('influencer_id', db.Integer, db.ForeignKey('influencers.id', ondelete='CASCADE'), primary_key=True),
    db.Column('agreed_rate', db.Float, nullable=False, default=0.0),
    db.Column('status', db.String(20), nullable=False, default='pending')  # pending, accepted, declined
)


class Campaign(db.Model):
    __tablename__ = 'campaigns'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    budget = db.Column(db.Float, nullable=False, default=0.0)
    # Indexed: report filters by date range and the campaigns list orders by start_date desc.
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    # Indexed: report filter + FK lookups (brand → campaigns join).
    brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'), nullable=False, index=True)
    # Indexed: report filter on platform.
    platform = db.Column(db.String(50), nullable=False, index=True)
    # Indexed: report filter on status (low-cardinality, but used in nearly every report query).
    status = db.Column(db.String(20), nullable=False, default='draft', index=True)  # draft, active, completed, cancelled

    influencers = db.relationship('Influencer', secondary=campaign_influencers, backref='campaigns', lazy=True)

    # Composite index for the most common report filter combination: brand + status.
    # Helps when filtering "all active campaigns for brand X".
    __table_args__ = (
        db.Index('ix_campaigns_brand_status', 'brand_id', 'status'),
    )
