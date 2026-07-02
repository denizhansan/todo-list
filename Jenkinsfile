pipeline {
    agent {
        node {
            label 'todo-Jenkins-agent'
        }
    }
    enviroment {
        BUILD_NUMBER = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Build') {
            steps {
                echo 'Cloning source project..'
                sh '''
                checkout scm
                '''

                echo 'Building docker images..'
                sh '''
                docker compose build

            }
        }
        stage('Test') {
            steps {
                echo 'Testing..'
                sh '''
                echo "Running health check"
                sleep 10

                curl --fail http://localhost:8000/health

                echo "Creating test task"
                response=$(curl --fail -X POST http://localhost:8000/tasks \
                -H "Content-Type: application/json" \
                -d '{"title": "Test Task", "description": "This is a test task."}')
                
                task_id=$(echo "$response" | jq -r '._id')
                echo "Task created with ID. $task_id"

                echo "Checking if the task was created"
                task=$(curl --fail http://localhost:8000/tasks/$task_id)
                echo "Task details: $task"
                title=$(echo "$task" | jq -r '.title')
                
                if [ "$title" != "Test Task" ]; then
                    echo "Wrong title. Expected 'Test Task', got '$title'"
                    exit 1
                fi

                //Burdaki testte updated time a göre bakıyorum daha güvenilir olması için sonrasında
                //-d ile değişen title a göre bakabilirim.
                echo "Updating the task"
                old_time=$(echo "$task" | jq -r '.updated_at')
                echo "Old updated_at: $old_time"
                updated_task=$(curl --fail -X  PUT http://localhost:8000/tasks/$task_id \
                -H "Content-Type: application/json" \
                -d '{"title": "Test Task - Edited", "description": "This is a test task for editing."}')
                updated_time=$(echo "$updated_task" | jq -r '.updated_at')
                echo "New updated_at: $updated_time"

                if [ "$old_time" == "$updated_time" ]; then
                    echo "Task was not updated"
                    exit 1
                fi

                echo "Checking if the task completed"
                check=$(curl --fail -X PATCH http://localhost:8000/tasks/$task_id/complete)
                completed=$(echo "$check" | jq -r '.completed')
                
                if [ "$completed" != "true" ]; then
                    echo "Task was not completed"
                    exit 1
                fi

                echo "Checking if the task uncompleted"
                check=$(curl --fail -X PATCH http://localhost:8000/tasks/$task_id/uncomplete)
                uncompleted=$(echo "$check" | jq -r '.completed')

                if [ "$uncompleted" != "false" ]; then
                    echo "Task was not uncompleted"
                    exit 1
                fi

                echo "Deleting task"
                curl --fail -X DELETE http://localhost:8000/tasks/$task_id

                echo "Checking if task was deleted"

                status_code=$(curl -o /dev/null -s -w "%{http_code}" \
                http://localhost:8000/tasks/$task_id)

                echo "Status Code: $status_code"

                if [ "$status_code" != "404" ]; then
                    echo "Task was not deleted"
                    exit 1
                fi
                '''
            }
        }
        stage('Deploy') {
            steps {
                echo 'Deploying...'
                sh '''
                docker compose build
                '''
            }
        }
    }
}