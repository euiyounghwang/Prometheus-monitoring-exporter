<i> 

## Golang Setup

GoNB offers a pre-built docker, that includes JupyterLab and GoNB. To use it, go to a directory that you want to make available to the Jupyter notebook (your home directory, or a directory where to store the notebook files). It will be mounted on the host/ subdirectory in JupyterLab.

https://pkg.go.dev/github.com/janpfeifer/gonb#section-readme

Window (Docker based)
- docker pull janpfeifer/gonb_jupyterlab:latest
- docker run -it --rm -p 8888:8888 -v "${PWD}":/notebooks janpfeifer/gonb_jupyterlab:latest
- docker cp loving_greider:/notebooks .

Linux and macOS Installation Using Standard Go Tools
- go install github.com/janpfeifer/gonb@latest && \
  go install golang.org/x/tools/cmd/goimports@latest && \
  go install golang.org/x/tools/gopls@latest

- goplay : go install -v github.com/haya14busa/goplay/cmd/goplay@v1.0.0

## Golang
If you’re starting a new project, create a new module by running the following command: (https://opensearch.org/docs/latest/clients/go/)
- go mod init <mymodulename>
- go mod tidy

Prometheus has an official Go client library that you can use to instrument Go applications. In this guide, we'll create a simple Go application that exposes Prometheus metrics via HTTP.
- Prometheus (https://prometheus.io/docs/guides/go-application/)
- To expose Prometheus metrics in a Go application, you need to provide a /metrics HTTP endpoint. You can use the prometheus/promhttp library's HTTP Handler as the handler function.
- You can install the prometheus, promauto, and promhttp libraries necessary for the guide using go get: (https://medium.com/devbulls/prometheus-monitoring-with-golang-c0ec035a6e37)
```bash
go get github.com/prometheus/client_golang/prometheus
go get github.com/prometheus/client_golang/prometheus/promauto
go get github.com/prometheus/client_golang/prometheus/promhttp
```
- go run main.go
- go build
- http://localhost:2112/metrics (curl http://localhost:2112/metrics)
- compile a go file/project on windows for Linux: `env GOOS=linux go build -o ./bin/prometheus` (Run this command `chmod 755 filname` after copying to linux server)
- gopsutil(https://leapcell.medium.com/gopsutil-powerful-system-stats-for-go-developers-2a1941c40822, https://dev.to/leapcell/gopsutil-powerful-system-stats-for-go-developers-53e0) is a Golang port of the Python library psutil, which helps us conveniently obtain various system and hardware information. It masks the differences between different systems and has extremely powerful portability. With gopsutil, we don’t need to use syscall to call the corresponding system methods for different systems. 
- generate package(https://westlife0615.tistory.com/268)


Gin-Framework: Gin is a web framework written in Golang. It features a Martini-like API, but with performance up to 40 times faster than Martini. If you need performance and productivity, you will love Gin.
- go mod init gin-framework
- go get github.com/gin-gonic/gin
- go mod tidy

```bash
$ go run ./main.go 
[GIN-debug] [WARNING] Creating an Engine instance with the Logger and Recovery middleware already attached.

[GIN-debug] [WARNING] Running in "debug" mode. Switch to "release" mode in production.
 - using env:   export GIN_MODE=release
 - using code:  gin.SetMode(gin.ReleaseMode)

[GIN-debug] GET    /ping                     --> main.main.func1 (3 handlers)
[GIN-debug] [WARNING] You trusted all proxies, this is NOT safe. We recommend you to set a value.
Please check https://pkg.go.dev/github.com/gin-gonic/gin#readme-don-t-trust-all-proxies for details.
[GIN-debug] Environment variable PORT is undefined. Using port :8080 by default
[GIN-debug] Listening and serving HTTP on :8080
[GIN] 2025/07/22 - 17:12:40 | 404 |            0s |             ::1 | GET      "/"
[GIN] 2025/07/22 - 17:12:40 | 404 |            0s |             ::1 | GET      "/favicon.ico"
[GIN] 2025/07/22 - 17:12:46 | 200 |            0s |             ::1 | GET      "/ping"

$ curl http://localhost:8080/ping
{"message":"pong"}
```
- gin-framework swagger : go get github.com/swaggo/swag/cmd/swag, go get github.com/swaggo/gin-swagger, go get github.com/swaggo/files
- Once you have added the annotations to your code, you can generate the Swagger documentation by running the following command: swag init (https://lemoncode21.medium.com/how-to-add-swagger-in-golang-gin-6932e8076ec0)
- http://localhost:8080/docs/index.html


GoConvey(https://github.com/smartystreets/goconvey) supports Go's native testing package. Neither the web UI nor the DSL are required; you can use either one independently. Directly integrates with go test; Fully-automatic web UI (works with native Go tests, too)
```bash
go get github.com/smartystreets/goconvey
go install github.com/smartystreets/goconvey

cd /Users/euiyoung.hwang/go/pkg/mod/github.com/smartystreets/goconvey@v1.8.1

go-search_engine git:(master) ✗ /Users/euiyoung.hwang/go/bin/goconvey --workDir=$SCRIPTDIR/tests
go-search_engine git:(master) ✗ ./go_convey.sh                                                                                              
2023/12/27 14:07:14 goconvey.go:116: GoConvey server: 
2023/12/27 14:07:14 goconvey.go:121:   version: v1.8.1
2023/12/27 14:07:14 goconvey.go:122:   host: 127.0.0.1
2023/12/27 14:07:14 goconvey.go:123:   port: 8080
```

Elasticsearch with golang
- https://opensearch.org/docs/latest/clients/rust/

Transform tools: An online playground to convert JSON to Go Struct.
- In Go, a struct is a user-defined type that groups together fields of different types into a single unit. Structs are similar to classes in other languages, but they do not support inheritance
- https://transform.tools/json-to-go


Go Test
- Run this command `./go_convey.sh` or `goconvey --workDir=$SCRIPTDIR/tests --port=7090` or `go test -v ./tests/`
```bash
=== RUN   TestHealthCheckHandler
&{GET /metrics HTTP/1.1 1 1 map[] {} <nil> 0 [] false example.com map[] map[] <nil> map[] 192.0.2.1:1234 /metrics <nil> <nil> <nil>  {{}} <nil> [] map[]}
&{200 map[]  false <nil> map[] false}
--- PASS: TestHealthCheckHandler (0.00s)
PASS
ok      prometheus.com/tests    (cached)
```

# Docker
- docker images
- When you type docker images on your local system, you might see a list of all the Docker images on your system. Those can be “normal” ones with a proper repository name and tag or “dangling” ones, indicated via the <none> text 
- In this case, you can use the following concise command to clean up your space for none tags: `docker rmi $(docker images -f "dangling=true" -q)`
```bash
- docker rmi $(docker images -f "dangling=true" -q)
Deleted: sha256:80656b6d54a746420b701ae14afeafe0cc2127f948f8accf356ec66aa2115191
...
```