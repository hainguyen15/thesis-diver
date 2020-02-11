
docker run -d --name mongo_img --expose 27017 mongo
echo "Run mongo container"

PubIP="$(dig +short myip.opendns.com @resolver1.opendns.com)"
echo $PubIP
docker run -d --name diver_vis --expose 5000 --link mongo_img \
-e IMAGE_DB=mongodb://mongo_img:27017/diver_img \
-e BASE_URL=http://${PubIP}/ \
-v /home/hainq/diver_data/projects/:/usr/diver/projects \
hainq15/diver_vis
echo "Run Visualization"

docker run -d --name diver_cache --expose 6379 redis
echo "Run Cache"

docker run -d --name celery_worker --gpus 0 \
--link diver_cache --link diver_vis \
-e REDIS_URI=redis://diver_cache:6379 \
-e VIS_HOST=diver_vis:5000 \
-e MODEL_PATH=/usr/diver/model/wsi.pth \
-v /home/hainq/diver_data:/usr/diver/model \
-v /home/hainq/diver_data/projects/:/usr/diver/projects \
hainq15/diver_task celery worker -A celery_worker.celery -l info --pool gevent
echo "Run Celery worker"

docker run -d --name diver_task --gpus 0 --link diver_cache \
-e REDIS_URI=redis://diver_cache:6379 \
-e MODEL_PATH=/usr/diver/model/wsi.pth \
-v /home/hainq/diver_data:/usr/diver/model \
-v /home/hainq/diver_data/projects/:/usr/diver/projects \
--expose 5001 hainq15/diver_task gunicorn -b 0.0.0.0:5001 run:app
echo "Run Task handler"

docker run -d --name diver_nginx \
-p 80:5000 -p 5001:5001 \
--link diver_vis --link diver_task \
-v /home/hainq/diver_data/projects/:/usr/diver/projects:ro \
hainq15/diver_nginx