pipeline {
    agent none 
    stages {
        stage('pre-parallel') {
            steps{
                echo 'Running pre-parallel stage'
            }
        }
        stage('Parallel Pipelines') {
            parallel {
                stage('macOS Pipeline') {
                    agent { label 'macos' }
                    stages {
                        stage('Build') { 
                            steps {
                                dir('src/BuildScripts') {
                                    sh './build.macos.sh' 
                                }
                            }
                        }
                    }
                }
                stage('Debian Pipeline') {
                    agent { label 'debian' }
                    stages {
                        stage('Build') { 
                            steps {
                                dir('src/BuildScripts') {
                                    sh './build.ubuntu2404.sh' 
                                } 
                            }
                        }
                    }
                }
            }
        }
        stage('post-parallel') {
            steps {
                echo 'Running post-parallel stage'
            }
        }
    }
}



