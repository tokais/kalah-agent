package main

import (
	"crypto/tls"
	"flag"
	"fmt"
	"log"
	"net"
)

const (
	majorVersion = 1
	minorVersion = 0
	patchVersion = 0
)

var (
	port, tport uint
	defSize     uint
	defStones   uint
	warmup      uint
	timeout     uint
	key, cert   string
)

func listen(ln net.Listener) {
	log.Print("Listening on port 2671")
	for {
		conn, err := ln.Accept()
		if err != nil {
			log.Print(err)
			continue
		}

		log.Printf("New connection from %s", conn.RemoteAddr())
		go (&Client{rwc: conn}).Handle()
	}
}

func main() {
	flag.UintVar(&defSize, "size", 7, "Size of new boards")
	flag.UintVar(&defStones, "stones", 7, "Number of stones to use")
	flag.UintVar(&port, "port", 2671, "Port number of plain connections")
	flag.UintVar(&tport, "tls-port", 2672, "Port number of encrypted connections")
	flag.StringVar(&cert, "tls-cert", "", "Port number of encrypted connections")
	flag.StringVar(&key, "tls-key", "", "Port number of encrypted connections")
	flag.UintVar(&warmup, "warmup", 5, "Seconds to wait before starting game")
	flag.UintVar(&timeout, "timeout", 5, "Seconds to wait for a move to be made")
	flag.Parse()

	// open server socket
	plain, err := net.Listen("tcp", fmt.Sprintf(":%d", port))
	if err != nil {
		log.Fatal(err)
	}
	go listen(plain)

	// open encrypted server socket
	if cert != "" && key != "" {
		cer, err := tls.LoadX509KeyPair("server.crt", "server.key")
		if err != nil {
			log.Fatal(err)
		}

		conf := &tls.Config{Certificates: []tls.Certificate{cer}}
		encr, err := tls.Listen("tcp", fmt.Sprintf(":%d", tport), conf)
		if err != nil {
			log.Fatal(err)
		}

		go listen(encr)
	} else if key == "" && cert != "" {
		log.Fatal("No key for certificate")
	} else if cert == "" && key != "" {
		log.Fatal("No certificate for key")
	}

	// start match scheduler
	organizer()
}
