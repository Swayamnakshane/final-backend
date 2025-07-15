pipeline {
    agent any
    environment {
        SONAR_HOME = tool "sonar"
    }
    stages {
        stage("code") {
            steps {
                git url: "https://github.com/Swayamnakshane/final-backend.git", branch: "new3back"
            }
        }
//         stage("SonarQube Analysis") {
//     steps {
//         withSonarQubeEnv("sonar") {
//             script {
//                 try {
//                     sh """
//                         ${SONAR_HOME}/bin/sonar-scanner \
//                         -Dsonar.projectName=myfront3 \
//                         -Dsonar.projectKey=myfront3 \
//                         -X
//                     """
//                 } catch (e) {
//                     echo "⚠️ SonarQube scan failed. See logs above for details."
//                     // You can choose to fail the build here if it's critical:
//                     // error("SonarQube analysis failed")
//                 }
//             }
//         }
//     }
// }

        stage("build") {
            steps {
                dir('backend') {
                    sh "docker build -t myback2:latest ."
                }
            }
        }
        stage("trivy") {
            steps {
                sh "trivy fs --format table -o trivy-fs-report.html ."
            }
        }
        stage("dockerhub push") {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: "dockerhubcred",
                    usernameVariable: "dockerHubUser",
                    passwordVariable: "dockerHubPass"
                )]) {
                    sh "docker login -u $dockerHubUser -p $dockerHubPass"
                    sh "docker tag myback2 $dockerHubUser/myback2:latest"
                    sh "docker push $dockerHubUser/myback2:latest"
                }
            }
        }
    }
}
