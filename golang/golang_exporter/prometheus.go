package main

import (
	"fmt"
	"log"
	"math"
	"net"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
	"github.com/prometheus/client_golang/prometheus/promhttp"
	"prometheus.com/metrics"
	"prometheus.com/utility"

	human "github.com/dustin/go-humanize"
	"github.com/shirou/gopsutil/cpu"
	"github.com/shirou/gopsutil/disk"
	"github.com/shirou/gopsutil/host"
	"github.com/shirou/gopsutil/mem"
	traffic "github.com/shirou/gopsutil/net"
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

	bootStartTime = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "bootStartTimeGauge",
			Help: "bootStartTimeGauge",
		},
		[]string{"server_job", "hostname", "boot_time"},
	)

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
		[]string{"server_job", "hostname", "cpu_model", "cpu_cores", "cpu_physicalCnt", "cpu_logicalCnt"},
	)

	basicMemoryInfo = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "basicMemoryInfoGauge",
			Help: "basicMemoryInfo (Byte)",
		},
		[]string{"server_job", "hostname", "ram_total", "ram_available", "ram_used", "ram_used_percent"},
	)

	basicMemoryInfoGB = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "basicMemoryInfoGBGauge",
			Help: "basicMemoryInfo (GB)",
		},
		[]string{"server_job", "hostname", "ram_total", "ram_available", "ram_used", "ram_used_percent"},
	)

	basicSwapMemoryInfo = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "basicSwapMemoryInfoGauge",
			Help: "basicSwapMemoryInfo (Byte)",
		},
		[]string{"server_job", "hostname", "swap_total", "swap_available", "swap_used", "swap_used_percent"},
	)

	basicSwapMemoryInfoGB = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "basicSwapMemoryInfoGBGauge",
			Help: "basicSwapMemoryInfo (GB)",
		},
		[]string{"server_job", "hostname", "swap_total", "swap_available", "swap_used", "swap_used_percent"},
	)

	basicMemoryTotal = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "basicMemoryTotalGauge",
			Help: "basicMemoryTotal (GB)",
		},
		[]string{"server_job"},
	)

	basicMemoryUsed = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "basicMemoryUsedGauge",
			Help: "basicMemoryUsed (GB)",
		},
		[]string{"server_job"},
	)

	basicMemoryAvailable = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "basicMemoryAvailableGauge",
			Help: "basicMemoryAvailable (GB)",
		},
		[]string{"server_job"},
	)

	basicMemoryUsedPercent = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "basicMemoryUsedPercentGauge",
			Help: "basicMemoryUsedPercent (%))",
		},
		[]string{"server_job"},
	)

	basicSwapMemoryTotal = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "basicSwapMemoryTotalGauge",
			Help: "basicSwapMemoryTotal (GB)",
		},
		[]string{"server_job"},
	)

	basicSwapMemoryUsed = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "basicSwapMemoryUsedGauge",
			Help: "basicSwapMemoryUsed (GB)",
		},
		[]string{"server_job"},
	)

	basicSwapMemoryAvailable = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "basicSwapMemoryAvailableGauge",
			Help: "basicSwapMemoryAvailable (GB)",
		},
		[]string{"server_job"},
	)

	basicSwapMemoryUsedPercent = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "basicSwapMemoryUsedPercentGauge",
			Help: "basicSwapMemoryUsedPercent (%))",
		},
		[]string{"server_job"},
	)

	diskUsageGauge = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "diskUsageGauge",
			Help: "Disk Usage all drives",
		},
		[]string{"server_job", "hostname", "path", "disktotal", "diskused", "diskfree", "diskusagepercent", "ipaddress"},
	)

	diskUsagePerDiskGauge = prometheus.NewGaugeVec(
		prometheus.GaugeOpts{
			Name: "diskUsagePerDiskGauge",
			Help: "Disk Usage all drives details",
		},
		[]string{"server_job", "hostname", "path"},
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

	prometheus.MustRegister(bootStartTime)
	prometheus.MustRegister(osInfo)
	prometheus.MustRegister(processInfoCpuGauge)
	prometheus.MustRegister(processInfoMemoryGauge)
	prometheus.MustRegister(cpuUsageGauge)
	prometheus.MustRegister(diskUsageGauge)
	prometheus.MustRegister(diskUsagePerDiskGauge)
	prometheus.MustRegister(cpuModelInfo)
	prometheus.MustRegister(basicMemoryInfo)
	prometheus.MustRegister(basicMemoryInfoGB)
	prometheus.MustRegister(basicSwapMemoryInfo)
	prometheus.MustRegister(basicSwapMemoryInfoGB)
	prometheus.MustRegister(basicMemoryTotal)
	prometheus.MustRegister(basicMemoryUsed)
	prometheus.MustRegister(basicMemoryAvailable)
	prometheus.MustRegister(basicMemoryUsedPercent)
	prometheus.MustRegister(basicSwapMemoryTotal)
	prometheus.MustRegister(basicSwapMemoryUsed)
	prometheus.MustRegister(basicSwapMemoryAvailable)
	prometheus.MustRegister(basicSwapMemoryUsedPercent)
	prometheus.MustRegister(networkRxInfo)
	prometheus.MustRegister(networkTxInfo)
}

func get_local_ip_addr() string {
	addrs, err := net.InterfaceAddrs()
	if err != nil {
		os.Stderr.WriteString("Oops: " + err.Error() + "\n")
		os.Exit(1)
	}

	var local_ip_address string
	for _, a := range addrs {
		if ipnet, ok := a.(*net.IPNet); ok && !ipnet.IP.IsLoopback() {
			if ipnet.IP.To4() != nil {
				// os.Stdout.WriteString(ipnet.IP.String() + "\n")
				local_ip_address = ipnet.IP.String()
				break
			}
		}
	}

	return local_ip_address
}

func get_disk_usage(hostname string) {
	// formatter := "%-14s %7s %7s %7s %4s %s\n"
	// fmt.Printf(formatter, "Filesystem", "Size", "Used", "Avail", "Use%", "Mounted on")

	// IP Address
	local_ip_address := get_local_ip_addr()
	// fmt.Println((local_ip_address))

	// reset
	diskUsageGauge.MetricVec.Reset()
	diskUsagePerDiskGauge.MetricVec.Reset()

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

		// set
		diskUsageGauge.WithLabelValues(hostname, hostname, p.Mountpoint, human.Bytes(s.Total), human.Bytes(s.Used), human.Bytes(s.Free), percent, local_ip_address).Set(1)
		// set
		diskUsagePerDiskGauge.WithLabelValues(hostname, hostname, p.Mountpoint).Set(math.Round(s.UsedPercent))
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
	// reset
	osInfo.MetricVec.Reset()
	// set
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

	// reset
	cpuModelInfo.MetricVec.Reset()
	// set
	// grep -c processor /proc/cpuinfo
	cpuModelInfo.WithLabelValues(hostname, hostname, c[0].ModelName, fmt.Sprintf("%d", c[0].Cores), fmt.Sprintf("%d", physicalCnt), fmt.Sprintf("%d", logicalCnt)).Set(1)

	m, err := mem.VirtualMemory()
	if err != nil {
		fmt.Println("Could not retrieve RAM details.")
		log.Fatal(err)
	}

	float_totalPercent, err = strconv.ParseFloat(s_totalPercent, 64)
	if err != nil {
		log.Fatal(err)
	}
	// reset
	cpuUsageGauge.MetricVec.Reset()
	// set
	cpuUsageGauge.WithLabelValues(hostname).Set(float_totalPercent)

	// fmt.Printf("* RAM Total: %v, RAM Available: %v, RAM Used: %v, RAM Used Percent:%f%%\n", m.Total, m.Available, m.Used, m.UsedPercent)
	// reset
	basicMemoryInfo.MetricVec.Reset()
	// set
	basicMemoryInfo.WithLabelValues(hostname, hostname, fmt.Sprintf("%d", m.Total), fmt.Sprintf("%d", m.Available), fmt.Sprintf("%d", m.Used), fmt.Sprintf("%0.2f%%", m.UsedPercent)).Set(1)

	// reset
	basicMemoryInfoGB.MetricVec.Reset()
	// set
	basicMemoryInfoGB.WithLabelValues(hostname, hostname, fmt.Sprintf("%d GB", m.Total/1024/1024/1024), fmt.Sprintf("%d GB", m.Available/1024/1024/1024), fmt.Sprintf("%d GB", m.Used/1024/1024/1024), fmt.Sprintf("%0.2f%%", m.UsedPercent)).Set(1)

	swapMemory, _ := mem.SwapMemory()
	// fmt.Println(swapMemory)
	// fmt.Println(swapMemory.Total)
	// data, _ := json.MarshalIndent(swapMemory, "", " ")
	// fmt.Println(string(data))

	//reset
	basicSwapMemoryInfo.MetricVec.Reset()
	basicSwapMemoryInfo.WithLabelValues(hostname, hostname, fmt.Sprintf("%d", swapMemory.Total), fmt.Sprintf("%d", swapMemory.Free), fmt.Sprintf("%d", swapMemory.Used), fmt.Sprintf("%0.2f%%", swapMemory.UsedPercent)).Set(1)

	// reset
	basicSwapMemoryInfoGB.MetricVec.Reset()
	// set
	basicSwapMemoryInfoGB.WithLabelValues(hostname, hostname, fmt.Sprintf("%d GB", swapMemory.Total/1024/1024/1024), fmt.Sprintf("%d GB", swapMemory.Free/1024/1024/1024), fmt.Sprintf("%d GB", swapMemory.Used/1024/1024/1024), fmt.Sprintf("%0.2f%%", swapMemory.UsedPercent)).Set(1)

	// reset
	basicMemoryTotal.MetricVec.Reset()
	// set
	/* Memeroy Total */
	basicMemoryTotal.WithLabelValues(hostname).Set(utility.String_to_float_giga(m.Total))

	// reset
	basicMemoryUsed.MetricVec.Reset()
	// set
	/* Memeroy Used */
	basicMemoryUsed.WithLabelValues(hostname).Set(utility.String_to_float_giga(m.Used))

	// reset
	basicMemoryAvailable.MetricVec.Reset()
	// set
	/* Memeroy Available */
	basicMemoryAvailable.WithLabelValues(hostname).Set(utility.String_to_float_giga(m.Available))

	// reset
	basicMemoryUsedPercent.MetricVec.Reset()
	// set
	/* Memeroy Used Percent */
	basicMemoryUsedPercent.WithLabelValues(hostname).Set(m.UsedPercent)

	// reset
	basicSwapMemoryTotal.MetricVec.Reset()
	// set
	/* Memeroy Total */
	basicSwapMemoryTotal.WithLabelValues(hostname).Set(utility.String_to_float_giga(swapMemory.Total))

	// reset
	basicSwapMemoryUsed.MetricVec.Reset()
	// set
	/* Memeroy Used */
	basicSwapMemoryUsed.WithLabelValues(hostname).Set(utility.String_to_float_giga(swapMemory.Used))

	// reset
	basicMemoryAvailable.MetricVec.Reset()
	// set
	/* Memeroy Available */
	basicSwapMemoryAvailable.WithLabelValues(hostname).Set(utility.String_to_float_giga(swapMemory.Used))

	// reset
	basicSwapMemoryUsedPercent.MetricVec.Reset()
	// set
	/* Memeroy Used Percent */
	basicSwapMemoryUsedPercent.WithLabelValues(hostname).Set(swapMemory.UsedPercent)

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
	n, _ := traffic.IOCounters(false)
	// fmt.Printf("Network - Received: %.2fMB (%d pkts) Sent: %.2fMB (%d pkts)\n",
	// 	float64(n[0].BytesRecv)/1024/1024,
	// 	n[0].PacketsRecv,
	// 	float64(n[0].BytesSent)/1024/1024,
	// 	n[0].PacketsSent)

	// reset
	networkRxInfo.MetricVec.Reset()
	networkTxInfo.MetricVec.Reset()
	// set
	networkRxInfo.WithLabelValues(hostname).Set(float64(n[0].BytesRecv) / 1024 / 1024)
	networkTxInfo.WithLabelValues(hostname).Set(float64(n[0].BytesSent) / 1024 / 1024)

	// fmt.Printf("Type = %T\n", cpuUsageGauge)
	go metrics.Processes(hostname, processInfoCpuGauge, processInfoMemoryGauge)

}

func get_basic_metrics(hostname string) {
	// host.BootTime() returns the timestamp of the host's boot time
	timestamp, _ := host.BootTime()
	t := time.Unix(int64(timestamp), 0)
	// fmt.Println(t.Local().Format("2006-01-02 15:04:05"))

	// reset
	bootStartTime.MetricVec.Reset()
	// set
	bootStartTime.WithLabelValues(hostname, hostname, t.Local().Format("2006-01-02 15:04:05")).Set(1)
}

func get_metrics_all() {
	go func() {
		hostname, err := os.Hostname()
		if err != nil {
			panic(err)
		}

		for {

			go get_basic_metrics(hostname)

			go get_disk_usage(hostname)
			// recordMetrics()
			opsProcessed.Inc()

			go basic_resource(hostname)

			time.Sleep(30 * time.Second)
		}
	}()
}

func serveFiles(w http.ResponseWriter, r *http.Request) {
	// fmt.Println(r.URL.Path)
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
