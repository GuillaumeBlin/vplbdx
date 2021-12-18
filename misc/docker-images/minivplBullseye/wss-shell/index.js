#!/usr/bin/env node
const yargs = require('yargs')

var argv = yargs
        .usage('Usage: $0 [options]')
        .option('port',{
	    default: 8080,
	    description : 'Port'
	})
	.option('entry',{
	    default: "/bin/bash",
	    description : 'Entrypoint script to be launched'
	})
	.option('ssl', {
            default: true,
            description: 'SSL by default. Use --no-ssl if unsecured wanted.'
        })
        .implies('ssl', 'ssl_cert')
        .implies('ssl_cert', 'ssl_key')
        .option('ssl_key', {default:null, description:'filepath to ssl key'})
        .option('ssl_cert', {default:null, description:'filepath to ssl certificate'})
        .help()
        .alias('h', 'help')
        .argv;

require('./run')(argv.port, argv.ssl, argv.ssl_key, argv.ssl_cert, argv.entry)
