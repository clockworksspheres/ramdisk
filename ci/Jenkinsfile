pipeline {
    agent none 
    stages {
        stage('pre-parallel') {
            steps{
                echo 'Running pre-parallel stage'
            }
        }
        stage('Parallel build Pipelines') {
            parallel {
                stage('macOS Pipeline') {
                    agent { label 'macos' }
                    stages {
                        stage('macOS Build') { 
                            steps {
                                dir('src/BuildScripts') {
                                    sh './build.macos.sh' 
                                }
                            }
                        }
                    }
                }
                stage('Rocky 10 Pipeline') {
                    agent { label 'rocky10' }
                    stages {
                        stage('rocky10 Build') { 
                            steps {
                                dir('src/BuildScripts') {
                                    sh './build.ubuntu2404.sh' 
                                } 
                            }
                        }
                    }
                }
                stage('Debian Pipeline') {
                    agent { label 'debian' }
                    stages {
                        stage('debian Build') { 
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
        stage('Parallel test pipelines') {
            parallel {
                stage('macOS Pipeline') {
                    agent { label 'macos' }
                    stages {
                        stage('macOS Test') { 
                            steps {
                                dir('src/tests') {
                                    echo '----------=====### Starting Tests ###=====----------'
                                    sh 'ls -l'
                                    sh '/opt/homebrew/bin/py.test --junit-xml test-reports/results.xml test_*.py'
                                    // sh '/Users/jenkins/.pyenv/shims/python ./test_run_commands.py'
                                    //sleep 15
                                    echo '----------=====### Finished Tests ###=====----------'
                                    junit 'test-reports/results.xml' 
                                }
                            }
                        }
                    }
                }
                stage('Rocky 10 Pipeline') {
                    agent { label 'rocky10' }
                    stages {
                        stage('Rocky10 Test') { 
                            steps {
                                dir('src/tests') {
                                    echo '----------=====### Starting Tests ###=====----------'
                                    sh 'ls -l'
                                    sh 'sudo /usr/bin/py.test --junit-xml test-reports/results.xml test_*.py'
                                    // sh '/Users/jenkins/.pyenv/shims/python ./test_run_commands.py'
                                    //sleep 15
                                    echo '----------=====### Finished Tests ###=====----------'
                                    junit 'test-reports/results.xml' 
                                }
                            }
                        }
                    }
                }
                stage('Debian Pipeline') {
                    agent { label 'debian' }
                    stages {
                        stage('Debian Test') { 
                            steps {
                                dir('src/tests') {
                                    echo '----------=====### Starting Tests ###=====----------'
                                    sh 'ls -l'
                                    sh 'sudo -E /usr/bin/py.test --junit-xml test-reports/results.xml test_*.py'
                                    // sh '/Users/jenkins/.pyenv/shims/python ./test_run_commands.py'
                                    //sleep 15
                                    echo '----------=====### Finished Tests ###=====----------'
                                    junit 'test-reports/results.xml' 
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
