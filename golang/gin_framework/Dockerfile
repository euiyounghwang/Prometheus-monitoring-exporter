
# https://brendanr.net/blog/go-docker-https/


FROM golang:1.23.1-alpine as builder
ARG CGO_ENABLED=0

#ENV http_proxy="http://localhost:8080"
#ENV https_proxy="https://localhost:8080"

WORKDIR /app

# RUN apk add --no-cache ca-certificates git

# Download Go modules
COPY ./go.mod ./go.sum ./
RUN go mod download
COPY . .

# RUN go build
# Build
# RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o FN-Go-Swagger-Services .
RUN go build -o FN-Go-Swagger-Services ./main.go

FROM golang:latest as runtime
#RUN apk --no-cache add ca-certificates

WORKDIR /root/

COPY --from=builder /app/FN-Go-Swagger-Services .
# COPY --from=builder /app/config.yaml .
# COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/

EXPOSE 8080

CMD ["./FN-Go-Swagger-Services"]
