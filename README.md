A convenient CLI program to compare to folders!

Uses https://github.com/AnthonyBloomer/python-cli-template for CLI argument handling.

THIS PROGRAM IS PROVIDED AS-IS, WITH POSSIBLE ERRORS. DO NOT SOLELY RELY ON ITS RESULTS.

Running:
Copy quickdiff.bat into a folder in your PATH (e.g. \ or \Users\youruser\). Edit this file, and put the location 
that this program folder is stored in place of "thisfolder". 
Then, you can run in the command line, with the extension as an argument.

```
quickdiff a b
```

This will show hashes and compare the list of all files in folders a and b (in the current directory).
The files themselves will not be compared; but will show if they've changed or not.

Information will also be shown about which files have possibly changed names (if they have exactly matching contents).

![alt text](https://i.imgur.com/6o0Sx3Y.png)