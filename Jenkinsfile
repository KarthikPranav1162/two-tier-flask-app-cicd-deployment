pipeline {
    agent any

    stages {

        stage('Clone') {
            steps {
                echo 'Cloning repository...'
                git 'https://github.com/KarthikPranav1162/two-tier-flask-app-cicd-deployment.git'
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
                echo 'Running container...'
                sh 'docker run -d -p 5000:5000 flask-app'
            }
        }
    }
}