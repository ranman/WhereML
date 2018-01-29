AWS_ACCESS_KEY_ID=$(aws --profile default configure get aws_access_key_id)
AWS_SECRET_ACCESS_KEY=$(aws --profile default configure get aws_secret_access_key)
AWS_DEFAULT_REGION=us-east-1

docker build -t whereml .
docker run -it --rm \
   -p 8080:8080 \
   -v /opt/ml:/opt/ml \
   -e AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
   -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
   -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY whereml serve
