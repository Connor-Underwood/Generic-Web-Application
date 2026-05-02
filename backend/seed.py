"""Seed the database with sample data."""

from app import app
from models import db, Brand, Influencer, Campaign, campaign_influencers
from datetime import date

def seed():
    with app.app_context():
        # Drop and recreate all tables
        db.drop_all()
        db.create_all()

        # --- Brands ---
        brands = [
            Brand(name="Nike", industry="Sports & Apparel", contact_email="partnerships@nike.com"),
            Brand(name="Glossier", industry="Beauty & Skincare", contact_email="collabs@glossier.com"),
            Brand(name="Red Bull", industry="Energy & Lifestyle", contact_email="creators@redbull.com"),
            Brand(name="Spotify", industry="Music & Entertainment", contact_email="influencers@spotify.com"),
            Brand(name="HelloFresh", industry="Food & Meal Kits", contact_email="partners@hellofresh.com"),
        ]
        db.session.add_all(brands)
        db.session.flush()

        # --- Influencers ---
        influencers = [
            Influencer(name="Emma Johnson", email="emma@example.com", platform="Instagram", follower_count=1200000, engagement_rate=3.2),
            Influencer(name="Jake Martinez", email="jake@example.com", platform="YouTube", follower_count=850000, engagement_rate=5.1),
            Influencer(name="Sophia Lee", email="sophia@example.com", platform="TikTok", follower_count=3400000, engagement_rate=7.8),
            Influencer(name="Marcus Brown", email="marcus@example.com", platform="Twitter", follower_count=620000, engagement_rate=2.4),
            Influencer(name="Olivia Chen", email="olivia@example.com", platform="Instagram", follower_count=980000, engagement_rate=4.5),
            Influencer(name="Tyler Wilson", email="tyler@example.com", platform="YouTube", follower_count=2100000, engagement_rate=6.3),
            Influencer(name="Mia Davis", email="mia@example.com", platform="TikTok", follower_count=5600000, engagement_rate=9.1),
            Influencer(name="Chris Taylor", email="chris@example.com", platform="Instagram", follower_count=440000, engagement_rate=3.8),
        ]
        db.session.add_all(influencers)
        db.session.flush()

        # --- Campaigns ---
        campaigns_data = [
            {
                "title": "Summer Running Collection Launch",
                "description": "Promote Nike's new summer running shoe line across social media.",
                "budget": 50000,
                "start_date": date(2026, 3, 1),
                "end_date": date(2026, 4, 15),
                "brand_id": brands[0].id,
                "platform": "Instagram",
                "status": "active",
                "influencer_ids": [influencers[0].id, influencers[4].id, influencers[7].id],
            },
            {
                "title": "Skincare Routine Series",
                "description": "Create a 4-part video series showcasing Glossier's skincare products.",
                "budget": 25000,
                "start_date": date(2026, 2, 15),
                "end_date": date(2026, 3, 30),
                "brand_id": brands[1].id,
                "platform": "YouTube",
                "status": "active",
                "influencer_ids": [influencers[1].id, influencers[5].id],
            },
            {
                "title": "Extreme Sports Challenge",
                "description": "TikTok challenge featuring extreme sports moments powered by Red Bull.",
                "budget": 75000,
                "start_date": date(2026, 4, 1),
                "end_date": date(2026, 5, 31),
                "brand_id": brands[2].id,
                "platform": "TikTok",
                "status": "draft",
                "influencer_ids": [influencers[2].id, influencers[6].id],
            },
            {
                "title": "Discover Weekly Spotlight",
                "description": "Influencers share their Spotify Discover Weekly playlists and reactions.",
                "budget": 15000,
                "start_date": date(2026, 1, 10),
                "end_date": date(2026, 2, 10),
                "brand_id": brands[3].id,
                "platform": "Twitter",
                "status": "completed",
                "influencer_ids": [influencers[3].id],
            },
            {
                "title": "Cook-Along Campaign",
                "description": "Weekly cook-along livestreams featuring HelloFresh meal kits.",
                "budget": 35000,
                "start_date": date(2026, 3, 15),
                "end_date": date(2026, 5, 15),
                "brand_id": brands[4].id,
                "platform": "YouTube",
                "status": "active",
                "influencer_ids": [influencers[1].id, influencers[5].id, influencers[4].id],
            },
            {
                "title": "New Year Fitness Kickoff",
                "description": "Motivational fitness content for New Year's resolutions with Nike gear.",
                "budget": 40000,
                "start_date": date(2026, 1, 1),
                "end_date": date(2026, 1, 31),
                "brand_id": brands[0].id,
                "platform": "Instagram",
                "status": "completed",
                "influencer_ids": [influencers[0].id, influencers[7].id],
            },
        ]

        for data in campaigns_data:
            inf_ids = data.pop("influencer_ids")
            campaign = Campaign(**data)
            campaign.influencers = [i for i in influencers if i.id in inf_ids]
            db.session.add(campaign)

        db.session.commit()
        print("Database seeded successfully!")
        print(f"  {len(brands)} brands")
        print(f"  {len(influencers)} influencers")
        print(f"  {len(campaigns_data)} campaigns")


if __name__ == '__main__':
    seed()
