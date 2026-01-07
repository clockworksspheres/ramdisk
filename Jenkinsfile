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
                        stage('Test') { 
                            steps {
                                dir('src/tests') {
                                    echo '----------=====### Starting Tests ###=====----------'
                                    sh 'ls -l
                                    sh '/Users/jenkins/Library/Python/3.9/bin/py.test --junit-xml test-reports/results.xml test_run_commands.py'
                                    echo '----------=====### Finished Tests ###=====----------'
                                }
                            }
                            post {
                                always {
                                    junit 'test-reports/results.xml' 
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



