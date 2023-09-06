
<!-- Main header -->
<p align = "center">
    <picture>
        <source media = "(prefers-color-scheme: dark)" srcset = "/docs/assets/logo_dark.png">
        <source media = "(prefers-color-scheme: light)" srcset = "/docs/assets/logo_light.png">
        <img alt = "English logo" src = "/docs/assets/logo_light.png">
    </picture>
    <hr>
</p>

<!-- Quick description -->
English: an expressive, easy to learn, and minimal language.  
Additionally designed as a much simpler replacement to [xpp](https://github.com/iiPythonx/xpp).

<!-- About -->
<h2 align = "center">About</h2>

English is a high-level, interpreted language implemented in Python 3; it has relatively high-level syntax, inspired by languages such as [Calcium (work-in-progress)](https://github.com/DmmDGM/calcium).  

Despite having a minimal footprint, English has:
- An easily extendable "built-in" system
- Full Unicode and escape sequence support
- "Chapter" system (similar to Assembly's pointers)
- Type casting and auto type inference
- Syntax that makes sense to read

<!-- Installing -->
<h2 align = "center">Installation</h2>

Before downloading English, ensure you have *at least* [Python 3.10](https://www.python.org/downloads/release/python-3100/) or greater (HOWEVER it is **recommended** to use [Python 3.11](https://www.python.org/downloads/release/python-3110/) for major performance gains).  

To install English, perform the following:
1. Fetch the source code
    1. If you have [git](https://git-scm.com) installed, it should be as simple as:
    ```sh
    git clone https://github.com/gooslol/english
    ```
    2. If you prefer using [pip](https://pypi.org/project/pip/) (still requires git):
    ```sh
    pip install git+https://github.com/gooslol/english
    ```
    3. Alternatively, you can [Download the ZIP](https://github.com/gooslol/english/archive/refs/heads/main.zip) and extract manually.

2. Setup your IDE (Visual Studio Code) (**Coming Soon**)
    - Install the [English Highlighting](#) extension for full English syntax highlighting support.

3. Perform a CLI test (optional)

    **Note: on NT-based systems (windows), replace `python3` with `py` or your appropriate launcher.**

    ```sh
    python3 -m english
    ```
    The command output should state the English version you are running.

<!-- Temp -->
<h2 align = "center">More Info</h2>

English is in very early stages of development, thus there is little documentation or anything else of use.  
\* Work on this is happening inside the [docs](https://github.com/gooslol/english/tree/docs) branch.  

We hope you enjoy using English regardless.  
This README will be updated as things change (as they inevitably will).
