package main

import (
	"gin_framework/docs"
	"net/http"

	"github.com/gin-gonic/gin"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
)

/*
- gin-framework swagger :
go get github.com/swaggo/swag/cmd/swag
# 1.16 or newer
go install github.com/swaggo/swag/cmd/swag@latest

go get github.com/swaggo/gin-swagger
go get github.com/swaggo/files
swag init
*/

// @title Swagger Example API
// @version 1.0
// @description This is a sample server.
// @termsOfService http://swagger.io/terms/

// @contact.name API Support
// @contact.url http://www.swagger.io/support
// @contact.email support@swagger.io

// @license.name Apache 2.0
// @license.url http://www.apache.org/licenses/LICENSE-2.0.html

// @host localhost:8080
// @BasePath /
func main() {
	r := gin.Default()

	//코드로 SwaggerInfo 속성을 지정해지만 doc.json 정상적으로 조회된다.
	docs.SwaggerInfo.Title = "Golang Swagger API"

	// 127.0.0.1:8080/docs/index.html 주로 swagger로 생성된 문서를 확인 수 있다.
	r.GET("/docs/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))

	v1Group := r.Group("/")
	{
		v1Group.GET("/", defaultHandler)
	}

	v2Group := r.Group("/api/v1")
	{
		v2Group.GET("/hello/:name", HelloHandler)
	}
	r.Run(":8080")
}

type User struct {
	Id   int    `json:"id" example:"1"`
	Name string `json:"name" example:"John"`
	Age  int    `json:"age" example:"10"`
}

// defaultHandler godoc
// @Summary test swagger api
// @Description test swagger api
// @name get-string-by-int
// @Accept  json
// @Produce  json
// @Router / [get]
// @Success 200
// @Failure 400
func defaultHandler(c *gin.Context) {
	defalut_map := map[string]string{"message": "hello world!"}
	// c.JSON(http.StatusOK, gin.H{"message": "hello world!"})
	c.JSON(http.StatusOK, defalut_map)
}

/* swagger doc */
// @tags API
// HelloHandler godoc
// @Summary
// @Description
// @name get-string-by-int
// @Accept  json
// @Produce  json
// @Param name path string true "User name"
// @Router /api/v1/hello/{name} [get]
// @Success 200 {object} User
// @Failure 400
func HelloHandler(c *gin.Context) {
	name := c.Param("name")
	if name == "" {
		c.JSON(http.StatusBadRequest, gin.H{"user": ""})
	} else {
		user := User{Id: 1, Name: name, Age: 20}
		c.JSON(http.StatusOK, gin.H{"user": user})
	}
}
