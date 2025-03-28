package main

import (
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	monitor "prometheus.com/lib"

	human "github.com/dustin/go-humanize"
	"github.com/shirou/gopsutil/cpu"
	"github.com/shirou/gopsutil/disk"
	"github.com/shirou/gopsutil/host"
	"github.com/shirou/gopsutil/mem"
	"github.com/shirou/gopsutil/net"
)

var (
	// MyGauge        prometheus.Gauge
	// diskUsageGauge prometheus.GaugeVec
	// opsProcessed   prometheus.Counter

	MyGauge = promauto.NewGauge(prometheus.GaugeOpts{
		Name: "host_disk_usage",
		Help: "disk usage gauge",
	})

	// cpuUsageGauge = promauto.NewGauge(prometheus.GaugeOpts{
	// 	Name: "cpuUsage",
	// 	Help: "cpuUsage gauge",
	// })

	cpuUsageGauge = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "cpuUsage",
			Help: "cpuUsage",
		},
		[]string{"server_job"},
	)

	processInfoCpuGauge = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "processInfoCpuGauge",
			Help: "processInfoCpuGauge",
		},
		[]string{"server_job", "process_name", "pid", "cmdline"},
	)

	processInfoMemoryGauge = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "processInfoMemoryGauge",
			Help: "processInfoMemoryGauge",
		},
		[]string{"server_job", "process_name", "pid"},
	)

	osInfo = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "basicosInfoGauge",
			Help: "osInfo",
		},
		[]string{"server_job", "os", "platformversion", "os_active_process", "os_uptime"},
	)

	cpuModelInfo = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "basiccpuModelInfoGauge",
			Help: "cpuModelInfo",
		},
		[]string{"server_job", "cpu_model", "cpu_cores", "cpu_physicalCnt", "cpu_logicalCnt"},
	)

	basicMemoryInfo = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "basicMemoryInfoGauge",
			Help: "basicMemoryInfo",
		},
		[]string{"server_job", "ram_total", "ram_available", "ram_used", "ram_used_percent"},
	)

	diskUsageGauge = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "diskUsageGauge",
			Help: "Disk Usage all drives",
		},
		[]string{"server_job", "path", "disktotal", "diskused", "diskfree", "diskusagepercent"},
	)

	opsProcessed = promauto.NewCounter(prometheus.CounterOpts{
		Name: "myapp_processed_ops_total",
		Help: "The total number of processed events",
	})

	networkRxInfo = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "networkRxInfoGauge",
			Help: "networkRxInfoGauge",
		},
		[]string{"server_job"},
	)

	networkTxInfo = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "networkTxInfoGauge",
			Help: "networkTxInfoGauge",
		},
		[]string{"server_job"},
	)
)

func Init() {
	// https://github.com/prometheus/client_golang/blob/main/prometheus/examples_test.go
	// must be registered

	prometheus.MustRegister(osInfo)
	prometheus.MustRegister(processInfoCpuGauge)
	prometheus.MustRegister(processInfoMemoryGauge)
	prometheus.MustRegister(cpuUsageGauge)
	prometheus.MustRegister(diskUsageGauge)
	prometheus.MustRegister(cpuModelInfo)
	prometheus.MustRegister(basicMemoryInfo)
	prometheus.MustRegister(networkRxInfo)
	prometheus.MustRegister(networkTxInfo)
}

func metrics_reset() {
	// log.Printf("resetting.")
	osInfo.MetricVec.Reset()
	cpuUsageGauge.MetricVec.Reset()
	cpuModelInfo.MetricVec.Reset()
	diskUsageGauge.MetricVec.Reset()
	basicMemoryInfo.MetricVec.Reset()
}

func get_disk_usage(hostname string) {
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

		diskUsageGauge.WithLabelValues(hostname, p.Mountpoint, human.Bytes(s.Total), human.Bytes(s.Used), human.Bytes(s.Free), percent).Set(1)

		// diskUsageGauge.With(prometheus.Labels{
		// 	"path":               "/apps",
		// 	"disk_usage_percent": percent,
		// })
	}

}

func basic_resource(hostname string) {
	// https://rebeccabilbro.github.io/doctor-go/
	/*
		The fmt.Sprintf() function in Go language formats according to a format specifier and returns the resulting string
	*/

	o, err := host.Info()
	if err != nil {
		fmt.Println("Could not retrieve OS details.")
		log.Fatal(err)
	}
	// fmt.Printf("* OS: %v Version %v, OS Active Processes: %v, OS Uptime: %v\n", o.OS, o.PlatformVersion, o.Procs, o.Uptime)
	osInfo.WithLabelValues(hostname, o.OS, o.PlatformVersion, fmt.Sprintf("%d", o.Procs), fmt.Sprintf("%d", o.Uptime)).Set(1)

	c, err := cpu.Info()
	if err != nil {
		fmt.Println("Could not retrieve CPU details.")
		log.Fatal(err)
	}
	// fmt.Printf("* CPU Model: %v, CPU Cores: %v \n", c[0].ModelName, c[0].Cores)

	physicalCnt, _ := cpu.Counts(false)
	logicalCnt, _ := cpu.Counts(true)
	// fmt.Printf("* CPU physicalCnt: %v, CPU logicalCnt: %v \n", physicalCnt, logicalCnt)

	totalPercent, _ := cpu.Percent(3*time.Second, false)
	// perPercents, _ := cpu.Percent(3*time.Second, true)
	// fmt.Printf("var1 = %T\n", totalPercent)

	var s_totalPercent string
	var float_totalPercent float64
	for _, v := range totalPercent {
		// fmt.Printf("var1 = %f, var2 = %T\n", v, v)
		s_totalPercent = fmt.Sprintf("%f", v)
	}

	// perPercents = fmt.Sprintf("%f", perPercents)
	// perPercents = strings.Replace(perPercents, "[", ",", -1)
	// perPercents = strings.Replace(perPercents, "]", ",", -1)

	cpuModelInfo.WithLabelValues(hostname, c[0].ModelName, fmt.Sprintf("%d", c[0].Cores), fmt.Sprintf("%d", physicalCnt), fmt.Sprintf("%d", logicalCnt)).Set(1)

	m, err := mem.VirtualMemory()
	if err != nil {
		fmt.Println("Could not retrieve RAM details.")
		log.Fatal(err)
	}

	float_totalPercent, err = strconv.ParseFloat(s_totalPercent, 64)
	if err != nil {
		log.Fatal(err)
	}
	// cpuUsageGauge.Set(float_totalPercent)
	cpuUsageGauge.WithLabelValues(hostname).Set(float_totalPercent)

	// fmt.Printf("* RAM Total: %v, RAM Available: %v, RAM Used: %v, RAM Used Percent:%f%%\n", m.Total, m.Available, m.Used, m.UsedPercent)
	basicMemoryInfo.WithLabelValues(hostname, fmt.Sprintf("%d", m.Total), fmt.Sprintf("%d", m.Available), fmt.Sprintf("%d", m.Used), fmt.Sprintf("%f", m.UsedPercent)).Set(1)
	// basicMemoryInfo.MetricVec.Reset()
	/*
		d, err := disk.Usage("/")
		if err != nil {
			fmt.Println("Could not retrieve disk details.")
			log.Fatal(err)
		}
		fmt.Printf("* Disk Total: %v , Disk Available: %v, Disk Used: %v, Disk Used Percent:%f%%\n", d.Total, d.Free, d.Used, d.UsedPercent)
	*/

	// call package monitor.go
	// monitor.System()

	// Get and display network stats
	n, _ := net.IOCounters(false)
	// fmt.Printf("Network - Received: %.2fMB (%d pkts) Sent: %.2fMB (%d pkts)\n",
	// 	float64(n[0].BytesRecv)/1024/1024,
	// 	n[0].PacketsRecv,
	// 	float64(n[0].BytesSent)/1024/1024,
	// 	n[0].PacketsSent)

	networkRxInfo.WithLabelValues(hostname).Set(float64(n[0].BytesRecv) / 1024 / 1024)
	networkTxInfo.WithLabelValues(hostname).Set(float64(n[0].BytesSent) / 1024 / 1024)

	// fmt.Printf("Type = %T\n", cpuUsageGauge)
	go monitor.Processes(hostname, processInfoCpuGauge, processInfoMemoryGauge)

}

func get_metrics_all() {
	go func() {
		hostname, err := os.Hostname()
		if err != nil {
			panic(err)
		}

		for {
			// Reset metrics
			metrics_reset()

			get_disk_usage(hostname)
			// recordMetrics()
			opsProcessed.Inc()

			basic_resource(hostname)

			time.Sleep(30 * time.Second)
		}
	}()
}

func serveFiles(w http.ResponseWriter, r *http.Request) {
	fmt.Println(r.URL.Path)
	p := "." + r.URL.Path
	if p == "./" {
		p = "./bind.html"
	}
	http.ServeFile(w, r, p)
}

/* http://localhost:2112/metrics */
func main() {
	port := 2112
	log.Printf("Starting Prometheus HTTP Handler [Port: %d]", port)

	// ''' initialize '''
	Init()
	// ''' update metrics '''
	get_metrics_all()

	// http.Handle("/metrics", promhttp.Handler())
	// http.ListenAndServe(":2112", nil)

	// https://medium.com/devbulls/prometheus-monitoring-with-golang-c0ec035a6e37
	// https://github.com/prometheus/client_golang/blob/main/prometheus/examples_test.go
	srv := http.NewServeMux()
	srv.HandleFunc("/", serveFiles)
	srv.Handle("/metrics", promhttp.Handler())

	// Prometheus collects metrics by scraping a /metrics HTTP endpoint
	if err := http.ListenAndServe(fmt.Sprintf(":%d", port), srv); err != nil {
		log.Fatalf("unable to start server: %v", err)
	}

}
