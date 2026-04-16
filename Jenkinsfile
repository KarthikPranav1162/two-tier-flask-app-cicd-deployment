pipeline {
    agent any

    environment {
        IMAGE_NAME = "flask-app"
        IMAGE_TAG = "${BUILD_NUMBER}"
        DB_HOST = 'taskvault-db.cwjcioaa0cfn.us-east-1.rds.amazonaws.com'
        DB_USER = 'admin'
        DB_NAME = 'taskmanager'
        DB_PASSWORD = credentials('db-password')
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t $IMAGE_NAME:$IMAGE_TAG ."
            }
        }

        stage('Run Container') {
            steps {
                sh '''
                docker stop flask-container || true
                docker rm flask-container || true

                docker run -d -p 5000:5000 \
                  --name flask-container \
                  --restart always \
                  -e DB_HOST=$DB_HOST \
                  -e DB_USER=$DB_USER \
                  -e DB_PASSWORD=$DB_PASSWORD \
                  -e DB_NAME=$DB_NAME \
                  $IMAGE_NAME:$IMAGE_TAG
                '''
            }
        }
    }
}