const fs = require('fs');
const https = require('https')
const http = require('http')

const WebsocketShellServer = require('./ws')

module.exports = function( port, ssl, ssl_key, ssl_cert, script) {
 var server = http.createServer()
  if(ssl){
    server = https.createServer({
      cert: fs.readFileSync(ssl_cert, 'utf8'),
      key: fs.readFileSync(ssl_key, 'utf8')
    })
 }
  const shellServer = new WebsocketShellServer(script, server)

  server.listen(port)

  console.log('Running service on port', port)

  return {
    shellServer,
    server
  }
}
