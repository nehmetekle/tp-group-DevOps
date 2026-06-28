pipeline {
    agent any

    environment {
        IMAGE_NAME = 'devops-task-api'
        REGISTRY = 'ghcr.io/jefsaber'
        STAGING_CONTAINER = 'devops-task-api-staging'
        IMAGE_TAG = sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                echo "Branch: ${env.BRANCH_NAME}"
                echo "Commit: ${env.GIT_COMMIT}"
                sh 'git log --oneline -5'
            }
        }

        stage('Lint') {
            steps {
                sh '''
                docker run --rm \
                  --volumes-from jenkins \
                  -w "$WORKSPACE" \
                  python:3.12-slim \
                  sh -c "pip install -q flake8 && flake8 app tests --max-line-length=100"
                '''
            }
        }

        stage('Build & Test') {
            steps {
                sh '''
                docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

                docker run --rm \
                  --volumes-from jenkins \
                  -w "$WORKSPACE" \
                  python:3.12-slim \
                  sh -c "pip install -q -r requirements.txt && pytest tests/ -v --cov=app --cov-report=xml:coverage.xml --cov-report=term-missing"

                ls -l coverage.xml
                '''
            }
        }

        stage('SonarQube Analysis') {
            steps {
                withSonarQubeEnv('sonarqube') {
                    withCredentials([string(
                        credentialsId: 'final-project-sonar-token',
                        variable: 'SONAR_AUTH_TOKEN'
                    )]) {
                        sh '''
                        docker run --rm \
                        --network cicd-network \
                        --volumes-from jenkins \
                        -w "$WORKSPACE" \
                        -e SONAR_HOST_URL="$SONAR_HOST_URL" \
                        -e SONAR_AUTH_TOKEN="$SONAR_AUTH_TOKEN" \
                        sonarsource/sonar-scanner-cli:latest \
                        sonar-scanner \
                        -Dsonar.projectKey=devops-task-api \
                        -Dsonar.projectName=DevOpsTaskAPI \
                        -Dsonar.projectBaseDir="$WORKSPACE" \
                        -Dsonar.sources=app \
                        -Dsonar.tests=tests \
                        -Dsonar.python.version=3.11 \
                        -Dsonar.python.coverage.reportPaths=coverage.xml \
                        -Dsonar.sourceEncoding=UTF-8 \
                        -Dsonar.login="$SONAR_AUTH_TOKEN" \
                        -Dsonar.scanner.metadataFilePath=$WORKSPACE/report-task.txt
                        '''
                    }
                }
            }
        }

        stage('Quality Gate') {
            steps {
                timeout(time: 15, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true, credentialsId: 'final-project-sonar-token'
                }
            }
        }

        stage('Security Scan') {
            steps {
                sh '''
                docker run --rm \
                  -v /var/run/docker.sock:/var/run/docker.sock \
                  -v trivy-cache:/root/.cache/trivy \
                  aquasec/trivy:latest image \
                  --severity HIGH,CRITICAL \
                  --ignore-unfixed \
                  --exit-code 0 \
                  --format table \
                  ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }

        stage('Push Docker Image') {
            when {
                anyOf {
                    branch 'Main'
                    branch 'main'
                    expression {
                        return env.GIT_BRANCH == 'origin/Main' ||
                            env.GIT_BRANCH == 'Main' ||
                            env.GIT_BRANCH == 'origin/main' ||
                            env.GIT_BRANCH == 'main'
                    }
                }
            }
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'final_project_github_token',
                    usernameVariable: 'REGISTRY_USER',
                    passwordVariable: 'REGISTRY_PASS'
                )]) {
                    sh '''
                    echo "$REGISTRY_PASS" | docker login ghcr.io -u "$REGISTRY_USER" --password-stdin

                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
                    docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

                    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:latest
                    docker push ${REGISTRY}/${IMAGE_NAME}:latest
                    '''
                }
            }
        }

        stage('Terraform Apply') {
            when {
                anyOf {
                    branch 'Main'
                    branch 'main'
                    expression {
                        return env.GIT_BRANCH == 'origin/Main' ||
                               env.GIT_BRANCH == 'Main' ||
                               env.GIT_BRANCH == 'origin/main' ||
                               env.GIT_BRANCH == 'main'
                    }
                }
            }
            steps {
                dir('infra') {
                    sh '''
                    terraform init -input=false

                    terraform apply -auto-approve \
                      -var="image_tag=${IMAGE_TAG}" \
                      -var="registry=${REGISTRY}" \
                      -var="docker_host=unix:///var/run/docker.sock"
                    '''
                }
            }
        }

        stage('Smoke Test') {
            when {
                anyOf {
                    branch 'Main'
                    branch 'main'
                    expression {
                        return env.GIT_BRANCH == 'origin/Main' ||
                               env.GIT_BRANCH == 'Main' ||
                               env.GIT_BRANCH == 'origin/main' ||
                               env.GIT_BRANCH == 'main'
                    }
                }
            }
            steps {
                sh '''
                echo "Waiting for staging app..."
                sleep 10

                docker run --rm \
                  --network cicd-network \
                  curlimages/curl:latest \
                  -f http://${STAGING_CONTAINER}:8000/health

                echo "Smoke test OK: /health returned 200"
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline succeeded. Image pushed: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
        }

        failure {
            echo "Pipeline failed. Check logs above."
        }
    }
}