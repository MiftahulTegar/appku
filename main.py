# from website import create_app

# app = create_app()

# if __name__ == '__main__':
#     app.run(debug=True, host='0.0.0.0', port=5506, threaded=True)

from website import create_app

app = create_app()

application = app
