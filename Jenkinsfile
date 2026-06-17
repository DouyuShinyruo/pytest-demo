pipeline {
    agent any

    tools {
        jdk 'default-jdk'
    }

    environment {
        ALLURE_VERSION = '2.27.0'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'pip install -r requirements.txt'
                sh 'playwright install --with-deps chromium'
            }
        }

        stage('Run Tests') {
            steps {
                sh 'mkdir -p reports'
                sh 'pytest tests/ step_defs/ -v --html=reports/report.html --self-contained-html --junitxml=reports/junit.xml --cov=common --cov-report=html:reports/coverage'
            }
            post {
                always {
                    junit 'reports/junit.xml'
                    publishHTML(target: [
                        reportDir: 'reports',
                        reportFiles: 'report.html',
                        reportName: 'Test Report'
                    ])
                }
            }
        }

        stage('Allure Report') {
            steps {
                sh '''
                    if ! command -v allure >/dev/null 2>&1; then
                        apt-get update && apt-get install -y --no-install-recommends default-jre-headless ca-certificates curl
                        curl -fsSL -o /tmp/allure.tgz "https://github.com/allure-framework/allure2/releases/download/${ALLURE_VERSION}/allure-${ALLURE_VERSION}.tgz"
                        tar -xzf /tmp/allure.tgz -C /opt/
                        ln -s /opt/allure-${ALLURE_VERSION}/bin/allure /usr/local/bin/allure
                    fi
                    allure generate reports/allure-results -o reports/allure-report --clean
                '''
                publishHTML(target: [
                    reportDir: 'reports/allure-report',
                    reportFiles: 'index.html',
                    reportName: 'Allure Report'
                ])
            }
        }
    }

    post {
        always {
            cleanWs()
        }
    }
}
