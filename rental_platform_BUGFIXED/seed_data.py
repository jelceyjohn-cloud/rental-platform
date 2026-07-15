"""
seed_data.py — run this once to add sample properties for demo purposes.
    python seed_data.py
"""
from app import app
from models import db, Property

sample_properties = [
    dict(title="2BHK Modern Apartment", city="Coimbatore", address="RS Puram",
         price=15000, bedrooms=2, bathrooms=2,
         description="Bright, well-ventilated apartment close to schools and markets."
         ),
    dict(title="Cozy 1BHK Studio", city="Coimbatore", address="Gandhipuram",
         price=9000, bedrooms=1, bathrooms=1,
         description="Perfect for a single professional, walking distance to bus stand."
         ),
    dict(title="Spacious 3BHK Villa", city="Chennai", address="Anna Nagar",
         price=32000, bedrooms=3, bathrooms=3,
         description="Independent villa with parking and a small garden."
         ),
]

with app.app_context():
    for data in sample_properties:
        if not Property.query.filter_by(title=data['title']).first():
            db.session.add(Property(**data))
    db.session.commit()
    print(f"Seeded {len(sample_properties)} sample properties.")
