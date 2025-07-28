FROM golang:latest as builder
ARG CGO_ENABLED=0

#ENV http_proxy="http://localhost:8080"
#ENV https_proxy="https://localhost:8080"

WORKDIR /app

#RUN apk update && apk add --no-cache git 

# Download Go modules
COPY ./golang_exporter/go.mod ./golang_exporter/go.sum ./
RUN go mod download
COPY . .

# RUN go build
# Build
# RUN CGO_ENABLED=0 GOOS=linux go build -o swagger
# RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o FN-Go-Basic-Services .
RUN go build -o FN-Go-Exporter-Services ./golang_exporter/prometheus.go

FROM golang:latest as runtime
#RUN apk --no-cache add ca-certificates

#WORKDIR /root/

# COPY --from=builder /app/FN-Go-Basic-Services .
COPY --from=builder /app/FN-Go-Exporter-Services .
# COPY --from=builder /app/config.yaml .

EXPOSE 2112

CMD ["./FN-Go-Exporter-Services"]
