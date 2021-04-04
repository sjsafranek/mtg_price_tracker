package main

import (
	"net/http"
	"time"
)

/*=======================================*/
// Defaults and Settings
/*=======================================*/
const (
	DEFAULT_MAX_CONCURRENT_JOBS uint64 = 10
	DEFAULT_MAX_BATCH_SIZE      uint64 = 40
	DEFAULT_MAX_PUSH_ATTEMPT           = 1
	DEFAULT_MAX_PENDING                = 50
)

var (
	httpClient        *http.Client
	httpTransporter   *http.Transport
	MaxConcurrentJobs uint64 = DEFAULT_MAX_CONCURRENT_JOBS
	MaxBatchSize      uint64 = DEFAULT_MAX_BATCH_SIZE
	MaxPushAttempt           = DEFAULT_MAX_PUSH_ATTEMPT
	MaxPending        int    = DEFAULT_MAX_PENDING
)

func init() {
	httpTransporter = &http.Transport{
		MaxIdleConnsPerHost: int(MaxConcurrentJobs),
		// http://craigwickesser.com/2015/01/golang-http-to-many-open-files/
		// Dial: (&net.Dialer{
		// 	Timeout: 5 * time.Second,
		// }).Dial,
		TLSHandshakeTimeout: 15 * time.Second,
		IdleConnTimeout:     60 * time.Second,

		// https://golang.org/pkg/net/http/#Transport
		// https://stackoverflow.com/questions/39813587/go-client-program-generates-a-lot-a-sockets-in-time-wait-state?utm_medium=organic&utm_source=google_rich_qa&utm_campaign=google_rich_qa
		MaxIdleConns: int(MaxConcurrentJobs),
		// ExpectContinueTimeout: 1 * time.Second,
		// ResponseHeaderTimeout: 5 * time.Second,
	}

	httpClient = &http.Client{
		// The default is 2, which is generally too low for our request concurrency
		// in this program, resulting in unboundded growth and eventual exhaustion
		// of all available ports. This should keep the number of detatched TIME_WAIT
		// sockets to a minimum that matches our concurrency configuration.
		Transport: httpTransporter,
	}

	go closeConnectionLoop()
}

func closeConnectionLoop() {
	// https://golang.org/pkg/net/http/#Transport.CloseIdleConnections
	httpTransporter.CloseIdleConnections()
	time.Sleep(30 * time.Second)
	closeConnectionLoop()
}
