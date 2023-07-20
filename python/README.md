# Python Flask app
Note, the best way to deploy this is via the Docker image. Please see the README in the folder above.

This README containers information specific to running the Python Flask app in your own host.

FIXME: Go over the instructions for setting up the app in a host.

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
