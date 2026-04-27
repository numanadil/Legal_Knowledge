bind = "127.0.0.1:8002"
workers = 3
accesslog = "logs/gunicorn_access.log"
errorlog = "logs/gunicorn_error.log"
loglevel = "debug"
timeout = 900
