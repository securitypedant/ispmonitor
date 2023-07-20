 # Sample config for vscode for debugging.

```
"configurations": [    
        {
            "name": "Python: Flask",
            "type": "python",
            "request": "launch",
            "module": "flask",
            "env": {
                "FLASK_APP": "python/app.py",
                "FLASK_DEBUG": "1"
            },
            "args": [
                "run",
                "--no-debugger",
                "--no-reload",
                "--port=8000"
            ],
            "jinja": true,
            "justMyCode": true,
            "cwd": "${workspaceFolder}/python"
        }
```
