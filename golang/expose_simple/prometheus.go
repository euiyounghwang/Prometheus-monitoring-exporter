package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"

	human "github.com/dustin/go-humanize"
	"github.com/shirou/gopsutil/disk"
)

var (
	MyGauge        prometheus.Gauge
	diskUsageGauge prometheus.GaugeVec
	opsProcessed   prometheus.Counter
)

func Init() {
	MyGauge = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "host_disk_usage",
		Help: "disk usage gauge",
	})

	diskUsageGauge = *prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "diskUsageGauge",
			Help: "Disk Usage all drives",
		},
		[]string{"hostname", "path", "disktotal", "diskused", "diskfree", "diskusagepercent"},
	)

	// diskUsageGauge = prometheus.NewGaugeVec(prometheus.GaugeOpts{
	// 	Namespace: "MyExporter",
	// 	Name:      "CpuPercentValue",
	// 	Help:      "CpuPercentValue",
	// },
	// 	[]string{
	// 		"disk",
	// 	},
	// )

	opsProcessed = promauto.NewCounter(prometheus.CounterOpts{
		Name: "myapp_processed_ops_total",
		Help: "The total number of processed events",
	})

	// https://github.com/prometheus/client_golang/blob/main/prometheus/examples_test.go
	// must be registered
	prometheus.MustRegister(diskUsageGauge)
}

func recordMetrics() {
	go func() {
		for {
			opsProcessed.Inc()
			time.Sleep(2 * time.Second)
		}
	}()
}

func get_disk_usage() {
	// formatter := "%-14s %7s %7s %7s %4s %s\n"
	// fmt.Printf(formatter, "Filesystem", "Size", "Used", "Avail", "Use%", "Mounted on")

	parts, _ := disk.Partitions(true)
	for _, p := range parts {
		device := p.Mountpoint
		s, _ := disk.Usage(device)

		if s.Total == 0 {
			continue
		}

		percent := fmt.Sprintf("%2.f%%", s.UsedPercent)

		// fmt.Printf(formatter,
		// 	s.Fstype,
		// 	human.Bytes(s.Total),
		// 	human.Bytes(s.Used),
		// 	human.Bytes(s.Free),
		// 	percent,
		// 	p.Mountpoint,
		// )

		MyGauge.Set(11)

		hostname, err := os.Hostname()
		if err != nil {
			panic(err)
		}

		diskUsageGauge.WithLabelValues(hostname, p.Mountpoint, human.Bytes(s.Total), human.Bytes(s.Used), human.Bytes(s.Free), percent).Add(1)

		// diskUsageGauge.With(prometheus.Labels{
		// 	"path":               "/apps",
		// 	"disk_usage_percent": percent,
		// })
	}

}

/* http://localhost:2112/metrics */
func main() {

	Init()

	go get_disk_usage()

	go recordMetrics()

	log.Println("Starting Prometheus..")
	// http.Handle("/metrics", promhttp.Handler())
	// http.ListenAndServe(":2112", nil)

	// https://medium.com/devbulls/prometheus-monitoring-with-golang-c0ec035a6e37
	// https://github.com/prometheus/client_golang/blob/main/prometheus/examples_test.go
	srv := http.NewServeMux()
	srv.Handle("/metrics", promhttp.Handler())

	// Prometheus collects metrics by scraping a /metrics HTTP endpoint
	if err := http.ListenAndServe(":2112", srv); err != nil {
		log.Fatalf("unable to start server: %v", err)
	}

}
