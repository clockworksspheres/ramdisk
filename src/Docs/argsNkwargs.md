# *args **kwargs in Python

In Python, *args and **kwargs are used to allow functions to accept an arbitrary number of arguments, providing flexibility in handling a varying number of inputs. *args is used for passing positional arguments, creating a tuple from all the positional arguments passed to the function. For example, a function that adds all arguments passed to it can be written as:

``` python
def add(*args):
    return sum(args)
```

**kwargs, on the other hand, is used for passing keyword arguments, converting all the dynamic keyword arguments passed into a dictionary. For example, a function that prints keyword arguments can be written as:

``` python
def print_kwargs(**kwargs):
    for k, val in kwargs.items():
        print(k, val)
```

Both *args and **kwargs can be used in the same function to accept a mix of positional and keyword arguments. The names _args and **kwargs are conventions, but you can use any name you prefer, as long as you use the asterisk (_) and double asterisk (**) syntax, respectively.

For example, a function that handles both positional and keyword arguments can be written as:

``` python
def fun(*args, **kwargs):
    print("Positional arguments:", args)
    print("Keyword arguments:", kwargs)
```

This function can handle both types of arguments, collecting positional arguments into a tuple and keyword arguments into a dictionary.

*args and **kwargs are particularly useful when writing wrapper functions or decorators that need to accept arbitrary arguments to pass through to the wrapped function. For example, a decorator that prints the arguments and return value of the function being wrapped can be written as:

``` python
def mydecorator(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        print("Calling f", args, kwargs)
        v = f(*args, **kwargs)
        print("f returned", v)
        return v
    return wrapper
```

This decorator can accept any number of arguments and keyword arguments to pass to the wrapped function. 234+3

[

![🌐](https://imgs.search.brave.com/U-eHNCapRHVNWWCVPPMTIvOofZULh0_A_FQKe8xTE4I/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvN2ZiNTU0M2Nj/MTFhZjRiYWViZDlk/MjJiMjBjMzFjMDRk/Y2IzYWI0MGI0MjVk/OGY5NzQzOGQ5NzQ5/NWJhMWI0NC93d3cu/cmVkZGl0LmNvbS8)

reddit.com

r/learnpython on Reddit: What are *args and **kwargs ?

](https://www.reddit.com/r/learnpython/comments/7dsn1s/what_are_args_and_kwargs/ "r/learnpython on Reddit: What are *args and **kwargs ?")[

![🌐](https://imgs.search.brave.com/bGE5KD5Za34la_MeOAt7584d1aXRWEQopsXEQyAALPw/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvYjBhOGQ3MmNi/ZWE5N2EwMmZjYzA1/ZTI0ZTFhMGUyMTE0/MGM0ZTBmMWZlM2Y2/Yzk2ODMxZTRhYTBi/NDdjYTE0OS93d3cu/Z2Vla3Nmb3JnZWVr/cy5vcmcv)

geeksforgeeks.org

*args and **kwargs in Python | GeeksforGeeks

](https://www.geeksforgeeks.org/args-kwargs-python/ "*args and **kwargs in Python | GeeksforGeeks")[

![🌐](https://imgs.search.brave.com/WbZ_-F1Q6lFgZIdP5ZEh1G0s3j44yw08zXWxtKjodv0/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvZTBkY2NkNmIw/MTExMmFjMjBhMTNh/NTQ3ODgxNTcxNmI4/ZGQxYmMyZTRlZWYx/MWYxNDQ0NTNhZjYz/ODRhYjczYS93d3cu/ZnJlZWNvZGVjYW1w/Lm9yZy8)

freecodecamp.org

How to Use *args and **kwargs in Python

](https://www.freecodecamp.org/news/args-and-kwargs-in-python/ "How to Use *args and **kwargs in Python")

![🌐](https://imgs.search.brave.com/D9KKNW7B_PBGo-trytMGRrRqvqMVW5Q5mDruXSPmBO4/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvYjVlMGVkZDVj/ZGMyZWRmMzAwODRi/ZDAwZGE4NWI3NmU4/MjRhNjEzOGFhZWY3/ZGViMjY1OWY2ZDYw/YTZiOGUyZS93d3cu/dzNzY2hvb2xzLmNv/bS8)

![🌐](https://imgs.search.brave.com/4WRMec_wn8Q9LO6DI43kkBvIL6wD5TYCXztC9C9kEI0/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvNWU3Zjg0ZjA1/YjQ3ZTlkNjQ1ODA1/MjAwODhiNjhjYWU0/OTc4MjM4ZDJlMTBi/ODExYmNiNTkzMjdh/YjM3MGExMS9zdGFj/a292ZXJmbG93LmNv/bS8)

![🌐](https://imgs.search.brave.com/wbvppBuVCgKKbriCKQkJam0JXslxEXTggNhrqswedV0/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvZjk5OGUzNzk1/MzNkYzgwN2VjOTg2/NzQyNzZhYTRhOWIz/OGVhOGFhZTgxMThh/YTcxYzE4NTU2MmVj/OWJmZjY2NC93d3cu/c2NhbGVyLmNvbS8)

+ 3 more

# how to sanatize input for args and kwargs

Found 9 relevant pages for: "sanitize input for *args and **kwargs in Python"

![🌐](https://imgs.search.brave.com/KqFEmRH7BxqfF48fQliyO22_lIQR7UhtzNBlI4ltCJM/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvMzZmNTVkYzNh/NzA3MTY0ZjZjMzY4/MDJiZGU2Y2E3MTk2/MWY0OWQzMjdkZTMy/MjdkYjgwYmIxZjdm/NWJlNmRiZC9ob3cu/ZGV2Lw)

![🌐](https://imgs.search.brave.com/bGE5KD5Za34la_MeOAt7584d1aXRWEQopsXEQyAALPw/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvYjBhOGQ3MmNi/ZWE5N2EwMmZjYzA1/ZTI0ZTFhMGUyMTE0/MGM0ZTBmMWZlM2Y2/Yzk2ODMxZTRhYTBi/NDdjYTE0OS93d3cu/Z2Vla3Nmb3JnZWVr/cy5vcmcv)

![🌐](https://imgs.search.brave.com/dE_vtEMxYDH3wV2HlQrtQ19g7v45wr72E9Du2m_lOYo/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvNjZmYTIzYTI3/ZTk2NjRhZjUyZTE4/YmU5OTg0ZGM2YzQ1/YjNmZGQ0YzBlNjAz/NmQ4MTFhODFkYjRj/YTRmZDA0MC93d3cu/ZGlnaXRhbG9jZWFu/LmNvbS8)

![🌐](https://imgs.search.brave.com/JQ43CVi7H9f72QglOvL-EsjUDRpEhkWaC1oTBUBouxE/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvNWNjZGM4YTE0/ZTJkY2FhMGNlOWNi/OTEyYjFlM2JmNmRk/NGY3MDk4ZmY2MzFj/ZjUyMTAwN2ZjODk2/MGIxYzAxZC9yZWFs/cHl0aG9uLmNvbS8)

+5

To sanitize input for `*args` and `**kwargs` in Python, you can use several techniques to ensure that the input is both valid and secure. Here are some methods:

## 1. **Escape Characters**

- **Description**: Use the `html.escape()` function to escape special characters in the input. This is particularly useful for preventing cross-site scripting (XSS) attacks.
    
- **Example**:
    
    ``` python
    import html
    
    def sanitize_input(input_data):
        return html.escape(input_data)
    
    user_input = "<script>alert('XSS')</script>"
    sanitized_input = sanitize_input(user_input)
    print(sanitized_input)  # Output: &lt;script&gt;alert('XSS')&lt;/script&gt;
    ```
    

## 2. **Third-Party Libraries**

- **Description**: Use libraries like `bleach` to allowlist specific HTML tags and attributes, ensuring that only safe content is rendered.
    
- **Example**:
    
    ``` python
    import bleach
    
    def sanitize_input(input_data):
        return bleach.clean(input_data, tags=['span'], attributes={'span': ['style']})
    
    user_input = "<span style='color: red;'>Hi!</span>"
    sanitized_input = sanitize_input(user_input)
    print(sanitized_input)  # Output: <span style="color: red;">Hi!</span>
    ```
    

## 3. **Regular Expressions**

- **Description**: Use the `re` module to blocklist or allowlist specific patterns in the input. This is useful for removing or validating specific types of input.
    
- **Example**:
    
    ``` python
    import re
    
    def sanitize_input(input_data):
        return re.sub(r'<script.*?>.*?</script>', '', input_data, flags=re.IGNORECASE)
    
    user_input = "Hi! <script>alert('XSS')</script>"
    sanitized_input = sanitize_input(user_input)
    print(sanitized_input)  # Output: Hi!
    ```
    

## 4. **Combining Techniques**

- **Description**: You can combine multiple techniques to ensure comprehensive sanitization. For example, you might escape all input and then allowlist specific tags using `bleach`.
    
- **Example**:
    
    ``` python
    import html
    import bleach
    
    def sanitize_input(input_data):
        escaped_data = html.escape(input_data)
        return bleach.clean(escaped_data, tags=['span'], attributes={'span': ['style']})
    
    user_input = "<span style='color: red;'>Hi!</span><script>alert('XSS')</script>"
    sanitized_input = sanitize_input(user_input)
    print(sanitized_input)  # Output: <span style="color: red;">Hi!</span>
    ```
    

## Applying Sanitization to `*args` and `**kwargs`

When using `*args` and `**kwargs`, you can apply the above techniques to each argument or keyword argument individually.

- **For `*args`**:
    
    ``` python
    def process_args(*args):
        sanitized_args = [sanitize_input(arg) for arg in args]
        return sanitized_args
    
    user_inputs = ["<script>alert('XSS')</script>", "<span style='color: red;'>Hi!</span>"]
    sanitized_inputs = process_args(*user_inputs)
    print(sanitized_inputs)  # Output: ['&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;', '&lt;span style=&#x27;color: red;&#x27;&gt;Hi!&lt;/span&gt;']
    ```
    
- **For `**kwargs`**:
    
    ``` python
    def process_kwargs(**kwargs):
        sanitized_kwargs = {key: sanitize_input(value) for key, value in kwargs.items()}
        return sanitized_kwargs
    
    user_inputs = {"name": "<script>alert('XSS')</script>", "message": "<span style='color: red;'>Hi!</span>"}
    sanitized_inputs = process_kwargs(**user_inputs)
    print(sanitized_inputs)  # Output: {'name': '&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;', 'message': '&lt;span style=&#x27;color: red;&#x27;&gt;Hi!&lt;/span&gt;'}
    ```
    

By using these techniques, you can ensure that the input passed to your functions via `*args` and `**kwargs` is both valid and secure.

# for *args and **kwargs

Certainly! When sanitizing input for `*args` and `**kwargs`, you can apply the same sanitization techniques to each argument and keyword argument. Here’s a more detailed example of how to do this:

## Sanitizing `*args`

For positional arguments (`*args`), you can iterate over each argument and apply the sanitization function.

## Sanitizing `**kwargs`

For keyword arguments (`**kwargs`), you can iterate over each key-value pair and apply the sanitization function to the values.

## Example

Let's use the `html.escape` function for sanitization as an example. You can replace it with any other sanitization function or library as needed.

``` python
import html

def sanitize_input(input_data):
    return html.escape(input_data)

def process_args_and_kwargs(*args, **kwargs):
    # Sanitize *args
    sanitized_args = [sanitize_input(arg) for arg in args]
    
    # Sanitize **kwargs
    sanitized_kwargs = {key: sanitize_input(value) for key, value in kwargs.items()}
    
    return sanitized_args, sanitized_kwargs

# Example usage
user_inputs_args = ["<script>alert('XSS')</script>", "<span style='color: red;'>Hi!</span>"]
user_inputs_kwargs = {"name": "<script>alert('XSS')</script>", "message": "<span style='color: red;'>Hi!</span>"}

sanitized_args, sanitized_kwargs = process_args_and_kwargs(*user_inputs_args, **user_inputs_kwargs)

print("Sanitized *args:", sanitized_args)
print("Sanitized **kwargs:", sanitized_kwargs)
```

## Output

``` bash
Sanitized *args: ['<script>alert('XSS')</script>', '<span style='color: red;'>Hi!</span>']
Sanitized **kwargs: {'name': '<script>alert('XSS')</script>', 'message': '<span style='color: red;'>Hi!</span>'}
```

## Explanation

1. **Sanitizing `*args`**:
    
    - We use a list comprehension to iterate over each argument in `*args` and apply the `sanitize_input` function to it.
        
    - The sanitized arguments are stored in a new list `sanitized_args`.
        
2. **Sanitizing `**kwargs`**:
    
    - We use a dictionary comprehension to iterate over each key-value pair in `**kwargs` and apply the `sanitize_input` function to the value.
        
    - The sanitized key-value pairs are stored in a new dictionary `sanitized_kwargs`.
        

## Using a Different Sanitization Function

If you need to use a different sanitization function, such as one from the `bleach` library, you can replace the `sanitize_input` function with the appropriate logic.

For example, using `bleach`:

``` python
import bleach

def sanitize_input(input_data):
    return bleach.clean(input_data, tags=[], attributes={})  # Allow no tags by default

def process_args_and_kwargs(*args, **kwargs):
    # Sanitize *args
    sanitized_args = [sanitize_input(arg) for arg in args]
    
    # Sanitize **kwargs
    sanitized_kwargs = {key: sanitize_input(value) for key, value in kwargs.items()}
    
    return sanitized_args, sanitized_kwargs

# Example usage
user_inputs_args = ["<script>alert('XSS')</script>", "<span style='color: red;'>Hi!</span>"]
user_inputs_kwargs = {"name": "<script>alert('XSS')</script>", "message": "<span style='color: red;'>Hi!</span>"}

sanitized_args, sanitized_kwargs = process_args_and_kwargs(*user_inputs_args, **user_inputs_kwargs)

print("Sanitized *args:", sanitized_args)
print("Sanitized **kwargs:", sanitized_kwargs)
```

## Output

``` bash
Sanitized *args: ['', 'Hi!']
Sanitized **kwargs: {'name': '', 'message': 'Hi!'}
```

This approach ensures that both positional and keyword arguments are sanitized, making your code more secure and robust.

AI-generated answer. Please verify critical facts.

-----

# make sure one only gets or uses specific named parameters

To ensure that only specific named parameters are used in a function, you can use a combination of Python's `**kwargs` and a whitelist of allowed parameters. This approach helps prevent the function from accepting unexpected or malicious keyword arguments.

Here’s a step-by-step guide to achieve this:

1. **Define the allowed parameters**.
    
2. **Filter the `**kwargs` to include only the allowed parameters**.
    
3. **Raise an error or handle the case where unexpected parameters are provided**.
    

## Example

Let's say you have a function that should only accept `name` and `message` as keyword arguments.

``` python
def process_input(*args, **kwargs):
    # Define the allowed parameters
    allowed_params = {'name', 'message'}
    
    # Filter the kwargs to include only the allowed parameters
    sanitized_kwargs = {k: v for k, v in kwargs.items() if k in allowed_params}
    
    # Optionally, raise an error if there are unexpected parameters
    unexpected_params = set(kwargs.keys()) - allowed_params
    if unexpected_params:
        raise ValueError(f"Unexpected parameters: {unexpected_params}")
    
    # Use the sanitized kwargs
    print("Positional arguments:", args)
    print("Sanitized keyword arguments:", sanitized_kwargs)

# Example usage
user_inputs_args = ["arg1", "arg2"]
user_inputs_kwargs = {"name": "Alice", "message": "Hello, World!", "unexpected": "This should not be here"}

try:
    process_input(*user_inputs_args, **user_inputs_kwargs)
except ValueError as e:
    print(e)
```

## Output

``` bash
Unexpected parameters: {'unexpected'}
```

## Explanation

1. **Define the allowed parameters**:
    
    - `allowed_params = {'name', 'message'}`: This set contains the names of the parameters that are allowed.
        
2. **Filter the `**kwargs`**:
    
    - `sanitized_kwargs = {k: v for k, v in kwargs.items() if k in allowed_params}`: This dictionary comprehension filters the `kwargs` to include only the keys that are in the `allowed_params` set.
        
3. **Handle unexpected parameters**:
    
    - `unexpected_params = set(kwargs.keys()) - allowed_params`: This line calculates the set of unexpected parameters by subtracting the allowed parameters from the keys in `kwargs`.
        
    - `if unexpected_params: raise ValueError(f"Unexpected parameters: {unexpected_params}")`: This checks if there are any unexpected parameters and raises a `ValueError` if there are.
        
4. **Use the sanitized kwargs**:
    
    - The function then prints the positional arguments and the sanitized keyword arguments.
        

## Alternative: Using a Decorator

If you want to apply this behavior to multiple functions, you can use a decorator to handle the sanitization and validation of keyword arguments.

``` python
def validate_kwargs(*allowed_params):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Filter the kwargs to include only the allowed parameters
            sanitized_kwargs = {k: v for k, v in kwargs.items() if k in allowed_params}
            
            # Optionally, raise an error if there are unexpected parameters
            unexpected_params = set(kwargs.keys()) - set(allowed_params)
            if unexpected_params:
                raise ValueError(f"Unexpected parameters: {unexpected_params}")
            
            # Call the original function with the sanitized kwargs
            return func(*args, **sanitized_kwargs)
        return wrapper
    return decorator

@validate_kwargs('name', 'message')
def process_input(*args, **kwargs):
    print("Positional arguments:", args)
    print("Sanitized keyword arguments:", kwargs)

# Example usage
user_inputs_args = ["arg1", "arg2"]
user_inputs_kwargs = {"name": "Alice", "message": "Hello, World!", "unexpected": "This should not be here"}

try:
    process_input(*user_inputs_args, **user_inputs_kwargs)
except ValueError as e:
    print(e)
```

## Output

```
Unexpected parameters: {'unexpected'}
```

## Explanation

1. **Define the decorator**:
    
    - `validate_kwargs(*allowed_params)`: This decorator takes a list of allowed parameter names.
        
    - `decorator(func)`: This inner function takes the function to be decorated.
        
    - `wrapper(*args, **kwargs)`: This inner function performs the sanitization and validation of the `kwargs` and then calls the original function with the sanitized `kwargs`.
        
2. **Apply the decorator**:
    
    - `@validate_kwargs('name', 'message')`: This applies the decorator to the `process_input` function, specifying that only `name` and `message` are allowed.
        
3. **Use the function**:
    
    - The function `process_input` is called with both positional and keyword arguments. The decorator ensures that only the allowed keyword arguments are passed to the function, and it raises an error if there are any unexpected parameters.
        

By using this approach,

AI-generated answer. Please verify critical facts.

-----

# can one use a **kwards function without parameters?

Yes, you can define a function that accepts `**kwargs` without specifying any parameters explicitly. This allows the function to accept any number of keyword arguments, but it does not require any specific keyword arguments to be passed. Here's how you can do it:

## Example

``` python
def process_kwargs(**kwargs):
    print("Keyword arguments:", kwargs)

# Example usage
process_kwargs(name="Alice", message="Hello, World!")
process_kwargs()
process_kwargs(age=30, city="New York")
```

## Output

``` bash
Keyword arguments: {'name': 'Alice', 'message': 'Hello, World!'}
Keyword arguments: {}
Keyword arguments: {'age': 30, 'city': 'New York'}
```

## Explanation

1. **Function Definition**:
    
    - `def process_kwargs(**kwargs)`: The function `process_kwargs` is defined to accept any number of keyword arguments using `**kwargs`.
        
2. **Function Calls**:
    
    - `process_kwargs(name="Alice", message="Hello, World!")`: This call passes two keyword arguments, `name` and `message`.
        
    - `process_kwargs()`: This call does not pass any keyword arguments.
        
    - `process_kwargs(age=30, city="New York")`: This call passes two different keyword arguments, `age` and `city`.
        
3. **Function Behavior**:
    
    - Inside the function, `kwargs` is a dictionary that contains all the keyword arguments passed to the function.
        
    - If no keyword arguments are passed, `kwargs` will be an empty dictionary.
        

## Handling Empty `kwargs`

If you want to handle the case where `kwargs` is empty, you can add a check:

``` python
def process_kwargs(**kwargs):
    if kwargs:
        print("Keyword arguments:", kwargs)
    else:
        print("No keyword arguments provided")

# Example usage
process_kwargs(name="Alice", message="Hello, World!")
process_kwargs()
process_kwargs(age=30, city="New York")
```

## Output

``` bash
Keyword arguments: {'name': 'Alice', 'message': 'Hello, World!'}
No keyword arguments provided
Keyword arguments: {'age': 30, 'city': 'New York'}
```

## Explanation

- **Check for Empty `kwargs`**:
    
    - `if kwargs:`: This checks if the `kwargs` dictionary is not empty.
        
    - If `kwargs` is empty, it prints a message indicating that no keyword arguments were provided.
        

By defining a function with `**kwargs`, you provide flexibility in accepting any number of keyword arguments, including the case where no keyword arguments are passed. This can be useful in various scenarios, such as creating flexible APIs or utility functions.

AI-generated answer. Please verify critical facts.

-----

