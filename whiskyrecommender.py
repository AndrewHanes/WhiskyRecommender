from whisky_recommender.api import application
import os


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    application.run(debug=False, host='0.0.0.0', port=port)


