# wss-shell
Standalone and secured version of **websocket-shell-service** project

Create an SSH-like server which lets clients open shells through websockets

```
# in the cloned directory launch the following command 
npm link

# the /usr/bin/wss-shell command is added
# Start the server on the default port (8080)
wss-shell

# Start the server with a custom port / ssl information
Usage: wss-shell [options]

Options:
  --version   Show version number                                      [boolean]
  --entry     Entrypoint script to be launched
  [default: /bin/bash]
  --port      Port                                               [default: 8080]
  --ssl       SSL by default. Use --no-ssl if unsecured wanted.  [default: true]
  --ssl_key   filepath to ssl key                                [default: null]
  --ssl_cert  filepath to ssl certificate                        [default: null]
  -h, --help  Show help                                                [boolean]

```

## How it works:

- Sets up a websocket server bound to [localhost:8080](http://localhost:8080)
- Pipes incoming websocket connections to shells using [node-pty](https://github.com/Microsoft/node-pty)
