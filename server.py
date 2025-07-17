#!/usr/bin/env python3
"""
Development server runner for BigShot API
"""

import os
from app import create_app

if __name__ == '__main__':
    # Set development environment
    os.environ['FLASK_ENV'] = 'development'
    
    # Create app
    app = create_app()
    
    # Run development server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )