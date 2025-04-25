from tasks import celery

# This starts the worker when run directly
if __name__ == "__main__":
    celery.worker_main()
