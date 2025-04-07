package metrics

import (
	"fmt"
	"log"
	"runtime"
	"sort"

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
	PID         int32
	Name        string
	Usage       float64
	mUsage      float64
	NameContext string
}

type ByUsage []ProcInfo

/* https://rezmoss.com/blog/building-terminal-system-monitor-golang/ */
func sortByCPU(processes []ProcInfo) []ProcInfo {
	sort.Slice(processes, func(i, j int) bool {
		return processes[i].Usage > processes[j].Usage
	})
	if len(processes) > 10 {
		processes = processes[:10]
	}
	return processes
}

func Processes(hostname string, processInfoCpuGauge *prometheus.GaugeVec, processInfoMemoryGauge *prometheus.GaugeVec) {
	processes, _ := process.Processes()

	var procinfos []ProcInfo
	for _, p := range processes {
		cpu, _ := p.CPUPercent()
		memory, _ := p.MemoryPercent()
		name, _ := p.Name()
		cmdline, _ := p.Cmdline()
		// procinfos = append(procinfos, ProcInfo{n, p.Pid, a, float64(m), c})
		procinfos = append(procinfos, ProcInfo{
			PID:         p.Pid,
			Name:        name,
			Usage:       cpu,
			mUsage:      float64(memory),
			NameContext: cmdline,
		})
	}
	// sort.Sort(ByUsage(procinfos))

	procinfos = sortByCPU(procinfos)
	// for _, p := range procinfos[:5] {
	for _, p := range procinfos {
		// log.Printf("   %s -> %f", p.Name, p.Usage)
		// log.Printf("   %s -> %f %s", p.Name, p.Usage, p.NameContext)
		processInfoCpuGauge.WithLabelValues(hostname, p.Name, fmt.Sprintf("%d", p.PID), p.NameContext).Set(p.Usage)
		processInfoMemoryGauge.WithLabelValues(hostname, p.Name, fmt.Sprintf("%d", p.PID)).Set(p.mUsage)
	}

}
