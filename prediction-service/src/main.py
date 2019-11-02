from sanic import Sanic
from sanic.log import logger
from sanic.response import json

import entities
from default import safe_load_default
from entities import Sensor, Individual, Data

app = Sanic()
is_dev = None
if app.config.get('ENVIRONMENT', '').upper() == 'DEV':
    logger.info('ENVIRONMENT: {}'.format(app.config.get('ENVIRONMENT', 'not set')))
    safe_load_default(app.config)
    is_dev = True

entities.ExtendedModel.init_app(app)


@app.route("/api/sensor/predict/<sensor_id>", methods=['GET'])
async def test(request, sensor_id):
    sensor = await Sensor.find_one(sensor_id)
    individual = await Individual.find(sort='date_time desc', limit=1)
    data = await Data.find(sort='date_time desc', limit=1)
    predicted = None
    if sensor:
        for d, i in zip(data.objects, individual.objects):
            predicted = d.predict(sensor, i)
            if is_dev:
                logger.info({'sensorId': sensor_id, 'data': d.to_dict(), 'individual': i.to_dict()})
        if predicted:
            return json({'sensorId': sensor_id,
                         'predictedValue': predicted})
        else:
            return json({'sensorId': sensor_id,
                         'error': 'Unable to predict value. Invalid data'},
                        status=404)
    else:
        return json({'sensorId': sensor_id,
                     'error': 'Sensor with this id does not exist'},
                    status=404)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
