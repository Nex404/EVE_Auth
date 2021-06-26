from EVE import app, config


if __name__=="__main__":
    app.run(debug=False, port=config.PORT, host=config.HOST)