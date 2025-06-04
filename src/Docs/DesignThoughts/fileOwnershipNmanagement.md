# File ownership and management discussion

Functionality likely to be implemented with a modified factory pattern.

* Nix that can be managed with programming language - ie. os.chown, os.chmod in python.  Extending the idea of ownership and permissions, a basic model could look like:

``` plantuml
@startuml
interface WorkerInterface
class SpawningController
class Worker

Worker : changeOwnership()
Worker : changePermissions()

WorkerInterface : changeOwnership()
WorkerInterface : changePermissions()

SpawningController : workerBasedOnOS()
SpawningController : workerBasedOnUser()
SpawningController : workerBasedOnCloud()
SpawningController : spawnSpawningController()

SpawningController --|> WorkerInterface
SpawningController --|> Worker
SpawningController --|> SpawningController

@enduml
```

All workers based on a specific target should have the same methods.  

A Spawining Controller should control only one worker type.

A meta Spawning Controller can spawn other Spawning Controllers.

All workers must implement the work their interface requires, or it is not considered production ready and does not go into production.  The workers may have protected or private methods that do not conform to specific interface methods, but only to support of the interface. 

