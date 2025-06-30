"""Seed development data for testing and development."""

import uuid
from datetime import datetime, timedelta
from app import create_app, db
from app.models.path import Path
from app.models.request import Request


def seed_development_data():
    """Seed the database with sample data for development."""
    app = create_app('development')
    
    with app.app_context():
        print("🌱 Seeding development data...")
        
        # Create sample paths
        paths_data = [
            {'path_id': 'webhook-test-1', 'description': 'Test webhook for development'},
            {'path_id': 'api-callback', 'description': 'API callback endpoint'},
            {'path_id': 'payment-webhook', 'description': 'Payment processor webhook'},
            {'path_id': 'user-registration', 'description': 'User registration webhook'},
        ]
        
        paths = []
        for path_data in paths_data:
            existing_path = Path.find_by_path_id(path_data['path_id'])
            if not existing_path:
                path = Path.create_new_path(path_id=path_data['path_id'])
                paths.append(path)
                print(f"  ✅ Created path: {path.path_id}")
            else:
                paths.append(existing_path)
                print(f"  ⚠️  Path already exists: {existing_path.path_id}")
        
        # Create sample requests for each path
        sample_requests = [
            {
                'method': 'POST',
                'headers': {
                    'Content-Type': 'application/json',
                    'User-Agent': 'PaymentProcessor/1.0',
                    'X-Webhook-Signature': 'sha256=abc123...'
                },
                'body': '{"event": "payment.completed", "amount": 29.99, "currency": "USD"}',
                'query_params': {'source': 'stripe'},
                'ip_address': '192.168.1.100',
                'user_agent': 'PaymentProcessor/1.0'
            },
            {
                'method': 'GET',
                'headers': {
                    'Accept': 'application/json',
                    'User-Agent': 'HealthChecker/2.0'
                },
                'body': None,
                'query_params': {'check': 'health'},
                'ip_address': '10.0.0.1',
                'user_agent': 'HealthChecker/2.0'
            },
            {
                'method': 'PUT',
                'headers': {
                    'Content-Type': 'application/xml',
                    'Authorization': 'Bearer token123',
                    'User-Agent': 'APIClient/3.1'
                },
                'body': '<?xml version="1.0"?><data><status>updated</status></data>',
                'query_params': {},
                'ip_address': '203.0.113.1',
                'user_agent': 'APIClient/3.1'
            },
            {
                'method': 'DELETE',
                'headers': {
                    'User-Agent': 'DeleteBot/1.0',
                    'X-Request-ID': 'req-456'
                },
                'body': '',
                'query_params': {'confirm': 'true'},
                'ip_address': '198.51.100.1',
                'user_agent': 'DeleteBot/1.0'
            }
        ]
        
        # Create requests for each path with varying timestamps
        for i, path in enumerate(paths):
            for j, req_data in enumerate(sample_requests):
                # Create requests with different timestamps over the past week
                days_ago = (i * len(sample_requests) + j) % 7
                hours_ago = (j * 6) % 24
                timestamp = datetime.utcnow() - timedelta(days=days_ago, hours=hours_ago)
                
                request = Request(
                    path_id=path.id,
                    method=req_data['method'],
                    headers=req_data['headers'],
                    body=req_data['body'],
                    query_params=req_data['query_params'],
                    ip_address=req_data['ip_address'],
                    user_agent=req_data['user_agent'],
                    timestamp=timestamp
                )
                
                db.session.add(request)
        
        db.session.commit()
        
        # Print summary
        total_paths = Path.query.count()
        total_requests = Request.query.count()
        
        print(f"\n📊 Seeding complete!")
        print(f"   Paths: {total_paths}")
        print(f"   Requests: {total_requests}")
        print(f"\n🔗 You can now test with these webhook URLs:")
        
        for path in Path.query.all():
            print(f"   http://localhost:5000/webhook/{path.path_id}")
        
        print(f"\n📋 View logs at:")
        for path in Path.query.all():
            print(f"   http://localhost:5000/api/paths/{path.path_id}/logs")


def clear_all_data():
    """Clear all data from the database."""
    app = create_app('development')
    
    with app.app_context():
        print("🗑️  Clearing all data...")
        
        Request.query.delete()
        Path.query.delete()
        db.session.commit()
        
        print("✅ All data cleared!")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'clear':
        clear_all_data()
    else:
        seed_development_data()
