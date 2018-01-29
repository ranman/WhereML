import flask
from flask import request, jsonify
import predict

app = flask.Flask("WhereML")


@app.route("/ping")
def ping():
    return "", 200


@app.route("/invocations", methods=["POST"])
def invoke():
    data = request.get_json(force=True)
    result = predict.download_and_predict(data['url'], int(data.get('max_predictions', 3)))
    if data.get('rich', False):
        result = predict.enrich(result)
    return jsonify(result)


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=8080)
