from flask import Flask,request
import json
import redis
import requests


redis_client = redis.Redis("redis")
app = Flask(__name__)

@app.route('/get-gender',methods=['GET'])
def get_gender():
    args = request.args
    name_key = str(args.get('name'))
    name_gender = redis_client.get(name_key)
    if name_gender is None:
        app.logger.info("Not found in redis :( getting response from API :)")
        url = f"https://api.genderize.io/?name={name_key}"
        tmp = requests.get(url)
        response = tmp.json()
        redis_response = {'gender':response['gender'],'count':response['count'],'probability':response['probability']}
        redis_client.set(name_key,json.dumps(redis_response))
        final_result = {name_key:json.loads(redis_client.get(name_key))}
        return final_result
    else:
        app.logger.info("Found in cache, serving from redis")
        final_result = {name_key:json.loads(name_gender)}
        return final_result

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=3000,debug=True)