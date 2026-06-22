# syntax=docker/dockerfile:1
# ---- 构建阶段：用 Maven(JDK8) 构建该模块及其依赖模块（-am） ----
FROM maven:3.9-eclipse-temurin-8 AS build
WORKDIR /build
COPY . .
RUN --mount=type=cache,target=/root/.m2,sharing=locked \
    mvn -B -pl shop-product-server -am clean package -DskipTests

# ---- 运行阶段 ----
FROM eclipse-temurin:8-jre
WORKDIR /app
COPY --from=build /build/shop-product-server/target/*.jar app.jar
EXPOSE 8081
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
