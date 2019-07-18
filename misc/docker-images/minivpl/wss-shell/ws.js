#!/usr/bon/env node

const WebSocket = require('ws')
const os = require('os')
const pty = require('node-pty')

module.exports =

class WebsocketShellServer {
  constructor (shell, server) {
    if (!server) throw new TypeError('Missing http server parameter')
    const wss = new WebSocket.Server({
      server
    })

    wss.on('connection', (connection) => {
       const ptyProcess = pty.spawn('stdbuf', ['-i0', '-o0', '-e0', shell], {
        cwd: process.env.HOME,
        env: process.env
      })

      ptyProcess.on('data', (data) => {
        connection.send(data.replace('\n','\r\n'))
      })

      connection.on('message', (message) => {
        ptyProcess.write(message.replace('\r','\n'))
      })

      ptyProcess.once('close', () => {
        connection.send("connection closed")
        connection.removeAllListeners()
        connection.close()
      })

      connection.once('close', () => {
        ptyProcess.removeAllListeners()
        ptyProcess.destroy()
      })
    })

    this.wss = wss
  }
}
