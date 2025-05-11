# Python Multiple Inheritance super

In Python, the `super()` function is used to call methods from a parent class without explicitly mentioning the parent's name, which is especially useful in multiple inheritance scenarios where the method resolution order (MRO) can be complex. When a class inherits from multiple parent classes, `super()` helps ensure that the methods are called in the correct order as defined by the MRO.

For example, consider a class hierarchy where `Child` inherits from both `Father` and `Mother`:

``` python
class Father:
    fathername = ""
    def display_father(self):
        print(self.fathername)

class Mother:
    mothername = ""
    def display_mother(self):
        print(self.mothername)

class Child(Father, Mother):
    def display_parents(self):
        super().display_father()  # Calls Father's method
        super().display_mother()   # Calls Mother's method
```

In this case, `super().display_father()` and `super().display_mother()` will correctly call the methods from the `Father` and `Mother` classes respectively, following the MRO.

Additionally, `super()` can be used to initialize attributes in the constructor of parent classes. In a child class constructor, `super().__init__()` can be used to initialize attributes defined in the parent class, reducing code duplication and making the code more reusable.

Here is an example demonstrating how to initialize parent class attributes within the constructor of a child class using `super()`:

``` python
class Parent1:
    def __init__(self):
        print("Parent1 initialized")

class Parent2:
    def __init__(self):
        print("Parent2 initialized")

class Child(Parent1, Parent2):
    def __init__(self):
        super().__init__()  # Invokes Parent2's initializer
        print("Child initialized")
```

In this example, `super().__init__()` ensures that the initializer of the next class in the MRO is called, which is `Parent2` in this case.

Python's `super()` function is crucial for managing method calls in multiple inheritance, ensuring that the correct methods are invoked based on the MRO.

[

![🌐](https://imgs.search.brave.com/_u2wtU6bOIAscdllAGUiT_rMLNOBT91-4a6WufN36f0/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvYjcyYjAzYmVl/ODU4MzZiMjJiYTFh/MjJhZDNmNWE4YzA5/MDgyYTZhMDg3NTYw/M2NiY2NiZTUxN2I5/MjU1MWFmMS93d3cu/dHV0b3JpYWxzcG9p/bnQuY29tLw)

tutorialspoint.com

How does Python's super() work with multiple inheritance?

](https://www.tutorialspoint.com/how-does-python-s-super-work-with-multiple-inheritance "How does Python's super() work with multiple inheritance?")[

![🌐](https://imgs.search.brave.com/4WRMec_wn8Q9LO6DI43kkBvIL6wD5TYCXztC9C9kEI0/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvNWU3Zjg0ZjA1/YjQ3ZTlkNjQ1ODA1/MjAwODhiNjhjYWU0/OTc4MjM4ZDJlMTBi/ODExYmNiNTkzMjdh/YjM3MGExMS9zdGFj/a292ZXJmbG93LmNv/bS8)

stackoverflow.com

How does Python's super() work with multiple inheritance? - Stack Overflow

](https://stackoverflow.com/questions/3277367/how-does-pythons-super-work-with-multiple-inheritance "How does Python's super() work with multiple inheritance? - Stack Overflow")[

![🌐](https://imgs.search.brave.com/bGE5KD5Za34la_MeOAt7584d1aXRWEQopsXEQyAALPw/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvYjBhOGQ3MmNi/ZWE5N2EwMmZjYzA1/ZTI0ZTFhMGUyMTE0/MGM0ZTBmMWZlM2Y2/Yzk2ODMxZTRhYTBi/NDdjYTE0OS93d3cu/Z2Vla3Nmb3JnZWVr/cy5vcmcv)

geeksforgeeks.org

Python Multiple Inheritance With super() Function | GeeksforGeeks

](https://www.geeksforgeeks.org/python-multiple-inheritance-with-super-function/ "Python Multiple Inheritance With super() Function | GeeksforGeeks")

![🌐](https://imgs.search.brave.com/Wg4wjE5SHAargkzePU3eSLmWgVz84BEZk1SjSglJK_U/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvOTkyZTZiMWU3/YzU3Nzc5YjExYzUy/N2VhZTIxOWNlYjM5/ZGVjN2MyZDY4Nzdh/ZDYzMTYxNmI5N2Rk/Y2Q3N2FkNy93d3cu/eW91dHViZS5jb20v)

![🌐](https://imgs.search.brave.com/bGE5KD5Za34la_MeOAt7584d1aXRWEQopsXEQyAALPw/rs:fit:32:32:1:0/g:ce/aHR0cDovL2Zhdmlj/b25zLnNlYXJjaC5i/cmF2ZS5jb20vaWNv/bnMvYjBhOGQ3MmNi/ZWE5N2EwMmZjYzA1/ZTI0ZTFhMGUyMTE0/MGM0ZTBmMWZlM2Y2/Yzk2ODMxZTRhYTBi/NDdjYTE0OS93d3cu/Z2Vla3Nmb3JnZWVr/cy5vcmcv)

+ 3 more

# both

Certainly! Let's dive into how `super()` works in Python with multiple inheritance, and provide a more comprehensive example that covers both method calls and initializer calls.

## Method Calls with `super()`

When a class inherits from multiple parent classes, `super()` helps manage the method resolution order (MRO). The MRO is the order in which base classes are searched when executing a method. Python uses the C3 linearization algorithm to determine the MRO.

Here's an example to illustrate method calls with `super()`:

``` python
class Father:
    def __init__(self):
        self.fathername = "John"
        print("Father initialized")

    def display_father(self):
        print(f"Father: {self.fathername}")

class Mother:
    def __init__(self):
        self.mothername = "Jane"
        print("Mother initialized")

    def display_mother(self):
        print(f"Mother: {self.mothername}")

class Child(Father, Mother):
    def __init__(self):
        super().__init__()  # Calls Father's initializer first
        print("Child initialized")

    def display_parents(self):
        super().display_father()  # Calls Father's method
        super().display_mother()  # Calls Mother's method

# Create an instance of Child
child = Child()
child.display_parents()
```

## Explanation

1. **Initialization**:
    
    - When `Child` is instantiated, `super().__init__()` in the `Child` class calls the initializer of `Father` first, as `Father` is listed before `Mother` in the class definition.
        
    - `Father` initializes its `fathername` attribute and prints "Father initialized".
        
    - The `Child` class then prints "Child initialized".
        
2. **Method Calls**:
    
    - `child.display_parents()` calls `super().display_father()`, which resolves to `Father.display_father()`.
        
    - `Father.display_father()` prints "Father: John".
        
    - `child.display_parents()` then calls `super().display_mother()`, which resolves to `Mother.display_mother()`.
        
    - `Mother.display_mother()` prints "Mother: Jane".
        

## MRO and `super()`

To understand the MRO, you can use the `mro()` method:

``` python
print(Child.mro())
```

This will output the MRO for the `Child` class:

``` bash
[, , , ]
```

## Initializing Multiple Parents

If you need to initialize both parent classes, you can use `super()` in a more controlled way:

``` python
class Child(Father, Mother):
    def __init__(self):
        super(Child, self).__init__()  # Calls Father's initializer
        super(Father, self).__init__()  # Calls Mother's initializer
        print("Child initialized")

# Create an instance of Child
child = Child()
```

## Explanation

1. **Initialization**:
    
    - `super(Child, self).__init__()` calls `Father`'s initializer.
        
    - `super(Father, self).__init__()` calls `Mother`'s initializer.
        
    - The `Child` class then prints "Child initialized".
        

## Full Example

Here's the full example with both method calls and initializer calls:

``` python
class Father:
    def __init__(self):
        self.fathername = "John"
        print("Father initialized")

    def display_father(self):
        print(f"Father: {self.fathername}")

class Mother:
    def __init__(self):
        self.mothername = "Jane"
        print("Mother initialized")

    def display_mother(self):
        print(f"Mother: {self.mothername}")

class Child(Father, Mother):
    def __init__(self):
        super(Child, self).__init__()  # Calls Father's initializer
        super(Father, self).__init__()  # Calls Mother's initializer
        print("Child initialized")

    def display_parents(self):
        super().display_father()  # Calls Father's method
        super().display_mother()  # Calls Mother's method

# Create an instance of Child
child = Child()
child.display_parents()
```

## Output

``` bash
Father initialized
Mother initialized
Child initialized
Father: John
Mother: Jane
```

This example demonstrates how to use `super()` effectively in multiple inheritance to manage both initializer calls and method calls.

# python3

Certainly! In Python 3, the `super()` function is even more powerful and easier to use, especially in the context of multiple inheritance. Here's a detailed explanation and example demonstrating how `super()` works with multiple inheritance in Python 3.

## Method Calls with `super()`

In Python 3, you can use `super()` without explicitly passing the class and instance, which makes the code cleaner and more readable. The `super()` function automatically handles the method resolution order (MRO) based on the C3 linearization algorithm.

Here's an example:

``` python
class Father:
    def __init__(self):
        self.fathername = "John"
        print("Father initialized")

    def display_father(self):
        print(f"Father: {self.fathername}")

class Mother:
    def __init__(self):
        self.mothername = "Jane"
        print("Mother initialized")

    def display_mother(self):
        print(f"Mother: {self.mothername}")

class Child(Father, Mother):
    def __init__(self):
        super().__init__()  # Calls Father's initializer first
        super(Father, self).__init__()  # Calls Mother's initializer
        print("Child initialized")

    def display_parents(self):
        super().display_father()  # Calls Father's method
        super().display_mother()  # Calls Mother's method

# Create an instance of Child
child = Child()
child.display_parents()
```

## Explanation

1. **Initialization**:
    
    - `super().__init__()` in the `Child` class calls the initializer of `Father` first, as `Father` is listed before `Mother` in the class definition.
        
    - `Father` initializes its `fathername` attribute and prints "Father initialized".
        
    - `super(Father, self).__init__()` calls the initializer of `Mother`.
        
    - `Mother` initializes its `mothername` attribute and prints "Mother initialized".
        
    - The `Child` class then prints "Child initialized".
        
2. **Method Calls**:
    
    - `child.display_parents()` calls `super().display_father()`, which resolves to `Father.display_father()`.
        
    - `Father.display_father()` prints "Father: John".
        
    - `child.display_parents()` then calls `super().display_mother()`, which resolves to `Mother.display_mother()`.
        
    - `Mother.display_mother()` prints "Mother: Jane".
        

## MRO and `super()`

To understand the MRO, you can use the `mro()` method:

``` python
print(Child.mro())
```

This will output the MRO for the `Child` class:

``` bash
[, , , ]
```

## Full Example

Here's the full example with both method calls and initializer calls:

``` python
class Father:
    def __init__(self):
        self.fathername = "John"
        print("Father initialized")

    def display_father(self):
        print(f"Father: {self.fathername}")

class Mother:
    def __init__(self):
        self.mothername = "Jane"
        print("Mother initialized")

    def display_mother(self):
        print(f"Mother: {self.mothername}")

class Child(Father, Mother):
    def __init__(self):
        super().__init__()  # Calls Father's initializer
        super(Father, self).__init__()  # Calls Mother's initializer
        print("Child initialized")

    def display_parents(self):
        super().display_father()  # Calls Father's method
        super().display_mother()  # Calls Mother's method

# Create an instance of Child
child = Child()
child.display_parents()
```

## Output

``` bash
Father initialized
Mother initialized
Child initialized
Father: John
Mother: Jane
```

## Explanation of `super()` in Multiple Inheritance

- **Single `super()` Call**: When you use `super()` without arguments, it automatically uses the current class and instance. This is useful for calling methods in the MRO order.
    
- **Multiple `super()` Calls**: When you need to call a specific parent class's method, you can use `super(ParentClass, self)`. This is useful for initializing multiple parent classes in a controlled manner.
    

By using `super()` effectively, you can manage multiple inheritance in Python 3 in a clean and maintainable way.

AI-generated answer. Please verify critical facts.

-----

# call specific parent class method

Certainly! In Python, you can call a specific parent class method using `super()` or by directly calling the method on the parent class. Here are both approaches:

## Using `super()`

To call a specific parent class method using `super()`, you need to specify the parent class and the instance. This is useful when you have multiple parent classes and you want to ensure that a specific parent class's method is called.

## Example with `super()`

``` python
class Father:
    def __init__(self):
        self.fathername = "John"
        print("Father initialized")

    def display_father(self):
        print(f"Father: {self.fathername}")

class Mother:
    def __init__(self):
        self.mothername = "Jane"
        print("Mother initialized")

    def display_mother(self):
        print(f"Mother: {self.mothername}")

class Child(Father, Mother):
    def __init__(self):
        super().__init__()  # Calls Father's initializer
        super(Father, self).__init__()  # Calls Mother's initializer
        print("Child initialized")

    def display_father(self):
        super().display_father()  # Calls Father's method

    def display_mother(self):
        super(Father, self).display_mother()  # Calls Mother's method

# Create an instance of Child
child = Child()
child.display_father()
child.display_mother()
```

## Explanation

1. **Initialization**:
    
    - `super().__init__()` in the `Child` class calls the initializer of `Father` first.
        
    - `super(Father, self).__init__()` calls the initializer of `Mother`.
        
    - The `Child` class then prints "Child initialized".
        
2. **Method Calls**:
    
    - `child.display_father()` calls `super().display_father()`, which resolves to `Father.display_father()`.
        
    - `Father.display_father()` prints "Father: John".
        
    - `child.display_mother()` calls `super(Father, self).display_mother()`, which resolves to `Mother.display_mother()`.
        
    - `Mother.display_mother()` prints "Mother: Jane".
        

## Using Direct Method Calls

You can also call a specific parent class method directly by using the parent class name. This approach is straightforward and sometimes more readable, especially for simple cases.

## Example with Direct Method Calls

``` python
class Father:
    def __init__(self):
        self.fathername = "John"
        print("Father initialized")

    def display_father(self):
        print(f"Father: {self.fathername}")

class Mother:
    def __init__(self):
        self.mothername = "Jane"
        print("Mother initialized")

    def display_mother(self):
        print(f"Mother: {self.mothername}")

class Child(Father, Mother):
    def __init__(self):
        Father.__init__(self)  # Calls Father's initializer
        Mother.__init__(self)  # Calls Mother's initializer
        print("Child initialized")

    def display_father(self):
        Father.display_father(self)  # Calls Father's method

    def display_mother(self):
        Mother.display_mother(self)  # Calls Mother's method

# Create an instance of Child
child = Child()
child.display_father()
child.display_mother()
```

## Explanation

1. **Initialization**:
    
    - `Father.__init__(self)` in the `Child` class calls the initializer of `Father`.
        
    - `Mother.__init__(self)` calls the initializer of `Mother`.
        
    - The `Child` class then prints "Child initialized".
        
2. **Method Calls**:
    
    - `child.display_father()` calls `Father.display_father(self)`, which prints "Father: John".
        
    - `child.display_mother()` calls `Mother.display_mother(self)`, which prints "Mother: Jane".
        

## Output

For both examples, the output will be:

``` bash
Father initialized
Mother initialized
Child initialized
Father: John
Mother: Jane
```

## Summary

- **Using `super()`**: Useful for maintaining the method resolution order (MRO) and ensuring that the correct methods are called in a complex inheritance hierarchy.
    
- **Using Direct Method Calls**: Useful for simple cases where you want to explicitly call a specific parent class method.
    

Choose the approach that best fits your use case and makes your code more readable and maintainable.

AI-generated answer. Please verify critical facts.

-----

# unittest.TestCase with multiple inheritance

When using `unittest.TestCase` with multiple inheritance, you can create a test class that inherits from `unittest.TestCase` and one or more additional classes. This can be useful for reusing common test setup and teardown methods, or for combining different testing behaviors.

Here's a step-by-step guide to creating a test class with multiple inheritance:

## Example with Multiple Inheritance

1. **Define the Base Classes**:
    
    - `BaseSetup`: A base class for common setup and teardown methods.
        
    - `CustomAssertions`: A base class for custom assertion methods.
        
2. **Create the Test Class**:
    
    - `MyTest`: A test class that inherits from `unittest.TestCase`, `BaseSetup`, and `CustomAssertions`.
        

## Example Code

``` python
import unittest

# Base class for common setup and teardown methods
class BaseSetup:
    def setUp(self):
        print("BaseSetup setUp")
        self.common_resource = "Common Resource"

    def tearDown(self):
        print("BaseSetup tearDown")
        self.common_resource = None

# Base class for custom assertion methods
class CustomAssertions:
    def assertPositive(self, value):
        self.assertGreater(value, 0, "Value is not positive")

# Test class inheriting from unittest.TestCase and the base classes
class MyTest(unittest.TestCase, BaseSetup, CustomAssertions):
    def setUp(self):
        super().setUp()  # Calls BaseSetup's setUp
        print("MyTest setUp")
        self.test_resource = "Test Resource"

    def tearDown(self):
        super().tearDown()  # Calls BaseSetup's tearDown
        print("MyTest tearDown")
        self.test_resource = None

    def test_example(self):
        print("Running test_example")
        self.assertEqual(self.common_resource, "Common Resource")
        self.assertEqual(self.test_resource, "Test Resource")
        self.assertPositive(10)

if __name__ == '__main__':
    unittest.main()
```

## Explanation

1. **Base Classes**:
    
    - `BaseSetup` provides common setup and teardown methods.
        
    - `CustomAssertions` provides custom assertion methods.
        
2. **Test Class**:
    
    - `MyTest` inherits from `unittest.TestCase`, `BaseSetup`, and `CustomAssertions`.
        
    - The `setUp` method in `MyTest` calls `super().setUp()` to ensure that the `setUp`method from `BaseSetup` is called first.
        
    - The `tearDown` method in `MyTest` calls `super().tearDown()` to ensure that the `tearDown` method from `BaseSetup` is called first.
        
    - The `test_example` method uses both the common resources and custom assertions.
        

## Method Resolution Order (MRO)

The MRO determines the order in which base classes are searched when executing a method. You can check the MRO using the `mro()` method:

``` python
print(MyTest.mro())
```

This will output the MRO for the `MyTest` class:

``` bash
[, , , , ]
```

## Running the Tests

To run the tests, you can use the `unittest` module directly:

``` python
if __name__ == '__main__':
    unittest.main()
```

## Output

When you run the test, you should see the following output:

``` bash
BaseSetup setUp
MyTest setUp
Running test_example
BaseSetup tearDown
MyTest tearDown
.
----------------------------------------------------------------------
Ran 1 test in 0.001s

OK
```

## Summary

- **Multiple Inheritance**: You can create a test class that inherits from `unittest.TestCase`and one or more additional base classes.
    
- **Method Resolution Order (MRO)**: Use `super()` to ensure that methods from base classes are called in the correct order.
    
- **Custom Assertions**: Define custom assertion methods in a separate base class to keep your test code clean and reusable.
    

This approach allows you to leverage the power of multiple inheritance to create more modular and maintainable test classes.

AI-generated answer. Please verify critical facts.

-----

# what is MRO

Method Resolution Order (MRO) is a fundamental concept in Python's class inheritance, particularly in the context of multiple inheritance. It determines the order in which methods and attributes are resolved in a class hierarchy. Python uses the C3 linearization algorithm to compute the MRO, which ensures a consistent and predictable order for method resolution.

## Understanding MRO

1. **Single Inheritance**:
    
    - In single inheritance, the MRO is straightforward. The method resolution order is simply the class itself followed by its base class.
        
2. **Multiple Inheritance**:
    
    - In multiple inheritance, a class can inherit from multiple base classes. The MRO determines the order in which these base classes are searched for methods and attributes.
        

## C3 Linearization

The C3 linearization algorithm ensures that the MRO is monotonic, consistent, and preserves the local precedence ordering. Here's a breakdown of the C3 linearization process:

1. **Local Precedence**: A class's own methods and attributes take precedence over those of its base classes.
    
2. **Depth-First**: The algorithm starts with the class itself and then recursively includes the MROs of its base classes.
    
3. **Monotonicity**: The order of base classes in the MRO should be consistent with the order in which they are specified in the class definition.
    

## Example of MRO

Consider the following class hierarchy:

``` python
class A:
    def method(self):
        print("A.method")

class B(A):
    def method(self):
        print("B.method")

class C(A):
    def method(self):
        print("C.method")

class D(B, C):
    def method(self):
        print("D.method")
```

In this hierarchy:

- `D` inherits from `B` and `C`.
    
- `B` and `C` both inherit from `A`.
    

To determine the MRO for `D`, you can use the `mro()` method:

``` python
print(D.mro())
```

The output will be:

``` bash
[, , , , ]
```

## Explanation of the MRO

1. **Class `D`**: The MRO starts with `D` itself.
    
2. **Class `B`**: Next, it includes `B` because `B` is the first base class specified in the class definition of `D`.
    
3. **Class `C`**: Then, it includes `C` because `C` is the second base class specified in the class definition of `D`.
    
4. **Class `A`**: Both `B` and `C` inherit from `A`, so `A` is included next.
    
5. **Class `object`**: Finally, `object` is included, as it is the base class of all classes in Python.
    

## Using `super()`

The `super()` function in Python uses the MRO to determine which method to call. For example, if you call `super().method()` in `D`, it will call the `method` from `B` because `B` is the next class in the MRO after `D`.

## Example with `super()`

``` python
class A:
    def method(self):
        print("A.method")

class B(A):
    def method(self):
        print("B.method")
        super().method()

class C(A):
    def method(self):
        print("C.method")
        super().method()

class D(B, C):
    def method(self):
        print("D.method")
        super().method()

# Create an instance of D
d = D()
d.method()
```

## Output

``` bash
D.method
B.method
C.method
A.method
```

## Explanation

1. **`D.method()`**: The `method` in `D` is called first.
    
2. **`B.method()`**: `super().method()` in `D` calls the `method` in `B`.
    
3. **`C.method()`**: `super().method()` in `B` calls the `method` in `C`.
    
4. **`A.method()`**: `super().method()` in `C` calls the `method` in `A`.
    

## Summary

- **MRO**: Method Resolution Order determines the order in which methods and attributes are resolved in a class hierarchy.
    
- **C3 Linearization**: Python uses the C3 linearization algorithm to compute the MRO, ensuring a consistent and predictable order.
    
- **`super()`**: The `super()` function uses the MRO to determine which method to call, making it a powerful tool for managing method calls in multiple inheritance.
    

Understanding MRO is crucial for working with complex class hierarchies and ensuring that your code behaves as expected.

AI-generated answer. Please verify critical facts.