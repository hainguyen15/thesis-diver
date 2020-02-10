from app import factory
import app

app = factory.create_app(celery=app.celery)
# app.run(port=5000)
# if __name__ == "__main__":
