
If in macos:

``` bash
brew install plantuml
plantuml -picoweb:8080
```

http://localhost:8080

https://www.plantuml.com/plantuml

# MacOS PlantUML Command Line

To install PlantUML on macOS, you can use Homebrew or MacPorts. Using Homebrew, you can install PlantUML by running the following command in the terminal:

``` bash
brew install plantuml
```

Alternatively, you can use MacPorts to install PlantUML:

``` bash
sudo port install plantuml
```


# with the picoweb switch

If you are looking to use PlantUML with the `picoweb` switch, this is typically done to generate HTML files that include the UML diagrams. The `picoweb` switch is used to create a small web server that serves the generated diagrams.

Here’s how you can use PlantUML with the `picoweb` switch:

1. **Install PlantUML**: If you haven't already installed PlantUML, you can do so using Homebrew:
    
    ```
    brew install plantuml
    ```
    
2. **Run PlantUML with the `picoweb` switch**: Use the following command to start the `picoweb` server. This will generate HTML files and serve them on a local web server:
    
    ```
    plantuml -picoweb /path/to/your/diagrams
    ```
    
    Replace `/path/to/your/diagrams` with the directory containing your PlantUML files.
    
3. **Access the diagrams**: After running the command, PlantUML will start a local web server. You can access the generated diagrams by opening a web browser and navigating to the URL provided by the server, typically `http://localhost:8080`.
    

# Example

Suppose you have a directory named `diagrams` containing your PlantUML files. You can run the following command:

```
plantuml -picoweb diagrams
```

This will generate HTML files for each PlantUML file in the `diagrams` directory and start a web server. You can then open a web browser and navigate to `http://localhost:8080` to view the diagrams.

# Additional Options

- **Custom Port**: If you want to use a different port, you can specify it using the `-Dplantuml.port` option:
    
    ```
    plantuml -picoweb diagrams -Dplantuml.port=8081
    ```
    
- **Verbose Output**: To see more detailed output, you can use the `-verbose` option:
    
    ```
    plantuml -picoweb diagrams -verbose
    ```
    

This setup is useful for quickly viewing and sharing UML diagrams in a web browser.

AI-generated answer. Please verify critical facts.