package monitor

import (
	"log"
	"runtime"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/shirou/gopsutil/process"
)

// Print system resource usage every 2 seconds.
func System() {
	mem := &runtime.MemStats{}

	cpu := runtime.NumCPU()
	log.Println("CPU:", cpu)

	rot := runtime.NumGoroutine()
	log.Println("Goroutine:", rot)

	// Byte
	runtime.ReadMemStats(mem)
	log.Println("Memory:", mem.Alloc)

	log.Println("Memory:", mem.Frees)

	// time.Sleep(2 * time.Second)
	log.Println("-------")

	// return cpu, rot, mem.Alloc
}

type ProcInfo struct {
	Name   string
	Usage  float64
	mUsage float32
}

type ByUsage []ProcInfo

func Processes(hostname string, processInfoCpuGauge *prometheus.GaugeVec, processInfoMemoryGauge *prometheus.GaugeVec) {
	processes, _ := process.Processes()

	var procinfos []ProcInfo
	for _, p := range processes {
		a, _ := p.CPUPercent()
		m, _ := p.MemoryPercent()
		n, _ := p.Name()
		procinfos = append(procinfos, ProcInfo{n, a, m})
	}
	// sort.Sort(ByUsage(procinfos))

	for _, p := range procinfos[:5] {
		// for _, p := range procinfos {
		// log.Printf("   %s -> %f", p.Name, p.Usage)
		processInfoCpuGauge.WithLabelValues(hostname, p.Name).Set(p.Usage)
		processInfoMemoryGauge.WithLabelValues(hostname, p.Name).Set(float64(p.mUsage))
	}

}
