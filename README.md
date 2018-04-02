# Google Trends Crawler

## Getting Started

1. Install python 3.5+, MongoDB
1. `pip install -r requirements.txt`
1. Change dev.env to your env var, MONGO_HOST...etc
1. `python google_trends.py`
1. `celery -A google_trends_worker worker --loglevel=info`
