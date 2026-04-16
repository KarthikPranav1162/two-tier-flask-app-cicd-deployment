pipeline {
    agent any

    environment {
        IMAGE_NAME = "karthikpranav/taskvault-app"
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

        stage('Build Image') {
            steps {
                sh '''
                docker build -t $IMAGE_NAME:$IMAGE_TAG .
                docker tag $IMAGE_NAME:$IMAGE_TAG $IMAGE_NAME:latest
                '''
            }
        }

        stage('Push to DockerHub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                    echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin

                    docker push $IMAGE_NAME:$IMAGE_TAG
                    docker push $IMAGE_NAME:latest

                    docker logout
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                docker pull $IMAGE_NAME:$IMAGE_TAG

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

        stage('Cleanup Old Images') {
            steps {
                sh 'docker image prune -af || true'
            }
        }

        stage('Verify') {
            steps {
                sh '''
                sleep 5
                curl -f http://localhost:5000 || exit 1
                '''
            }
        }
    }
}