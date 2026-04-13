pipeline {
    agent any

    stages {

        stage('Clone') {
            steps {
                echo 'Cloning repository...'
                git branch: 'main', url: 'https://github.com/KarthikPranav1162/two-tier-flask-app-cicd-deployment.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                sh 'docker build -t flask-app .'
            }
        }

        stage('Run Container') {
            steps {
                echo 'Stopping old container...'
                sh 'docker stop flask-container || true'
                sh 'docker rm flask-container || true'

                echo 'Running new container...'
                sh 'docker run -d -p 5000:5000 --name flask-container flask-app'
            }
        }
    }
}