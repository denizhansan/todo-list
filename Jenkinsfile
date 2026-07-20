pipeline {
    agent {
        node {
            label 'todo-jenkins-agent'
        }
    }
    environment {
        BUILD_NUMBER = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Check Branch') {
            steps {
                script {
                    if (env.GIT_BRANCH != 'origin/main' && env.GIT_BRANCH != 'origin/devops') {
                        currentBuild.result = 'ABORTED'
                        error("Hatalı branch. Gelen branch: ${env.GIT_BRANCH}")
                    }
                }
            }
        }
        stage('Create .env') {
            steps {
                echo 'Creating .env file..'
                sh '''
                cat > .env <<EOF
                MONGODB_URI=mongodb://admin:password@todo-mongo:27017/?authSource=admin
                DATABASE_NAME=todo_app
                COLLECTION_NAME=tasks
                API_HOST=0.0.0.0
                API_PORT=8000
                ALLOWED_ORIGINS=http://localhost
                EOF
                '''
            }
        }
        stage('Build') {
            steps {
                echo 'Cloning source project..'
                checkout scm

                echo 'Building docker images..'
                sh '''
                docker compose -f jenkins-docker.compose.yaml build
                docker compose -f jenkins-docker.compose.yaml up -d
                '''
            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
                sh '''
                set -e

                echo "Running health check"
                sleep 10
                curl --fail http://todo-backend-container:8000/health

                echo "Creating test task"
                response=$(curl --fail -X POST http://todo-backend-container:8000/tasks \
                    -H "Content-Type: application/json" \
                    -d '{"title": "Test Task", "description": "This is a test task."}')
                task_id=$(echo "$response" | jq -r '._id')
                echo "Task created with ID: $task_id"

                echo "Checking if the task was created"
                task=$(curl --fail http://todo-backend-container:8000/tasks/$task_id)
                echo "Task details: $task"

                title=$(echo "$task" | jq -r '.title')
                if [ "$title" != "Test Task" ]; then
                    echo "Wrong title. Expected 'Test Task', got '$title'"
                    exit 1
                fi

                # Burdaki testte updated_at a göre bakıyorum daha güvenilir olması için
                # sonrasında -d ile değişen title a göre de bakabilirim.
                echo "Updating the task"
                old_time=$(echo "$task" | jq -r '.updated_at')
                echo "Old updated_at: $old_time"

                updated_task=$(curl --fail -X PUT http://todo-backend-container:8000/tasks/$task_id \
                    -H "Content-Type: application/json" \
                    -d '{"title": "Test Task - Edited", "description": "This is a test task for editing."}')
                updated_time=$(echo "$updated_task" | jq -r '.updated_at')
                echo "New updated_at: $updated_time"

                if [ "$old_time" == "$updated_time" ]; then
                    echo "Task was not updated"
                    exit 1
                fi

                echo "Checking if the task completed"
                check=$(curl --fail -X PATCH http://todo-backend-container:8000/tasks/$task_id/complete)
                completed=$(echo "$check" | jq -r '.completed')
                if [ "$completed" != "true" ]; then
                    echo "Task was not completed"
                    exit 1
                fi

                echo "Checking if the task uncompleted"
                check=$(curl --fail -X PATCH http://todo-backend-container:8000/tasks/$task_id/uncomplete)
                uncompleted=$(echo "$check" | jq -r '.completed')
                if [ "$uncompleted" != "false" ]; then
                    echo "Task was not uncompleted"
                    exit 1
                fi

                echo "Deleting task"
                curl --fail -X DELETE http://todo-backend-container:8000/tasks/$task_id

                echo "Checking if task was deleted"
                status_code=$(curl -o /dev/null -s -w "%{http_code}" \
                    http://todo-backend-container:8000/tasks/$task_id)
                echo "Status Code: $status_code"
                if [ "$status_code" != "404" ]; then
                    echo "Task was not deleted"
                    exit 1
                fi
                '''
            }
        }
          }
        stage('SonarQube Analysis') {
            def mvn = tool 'Default Maven';
             withSonarQubeEnv() {
                sh "${mvn}/bin/mvn clean verify sonar:sonar -Dsonar.projectKey=Todo-App"
    }
  }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
                echo 'İlerki aşamalarda deploy işlemleri yapılacak.'
            }
        }
    }
}