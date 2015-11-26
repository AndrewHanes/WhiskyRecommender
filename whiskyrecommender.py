from whisky_recommender.api import application
import whisky_recommender.config
import os


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    application.run(debug=whisky_recommender.config.DEBUG, host='0.0.0.0', port=port)


