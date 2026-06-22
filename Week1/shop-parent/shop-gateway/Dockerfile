# syntax=docker/dockerfile:1
# ---- 构建阶段：用 Maven(JDK8) 构建网关模块及父工程（-am） ----
FROM maven:3.9-eclipse-temurin-8 AS build
WORKDIR /build
COPY . .
RUN --mount=type=cache,target=/root/.m2,sharing=locked \
    mvn -B -pl shop-gateway -am clean package -DskipTests

# ---- 运行阶段 ----
FROM eclipse-temurin:8-jre
WORKDIR /app
COPY --from=build /build/shop-gateway/target/*.jar app.jar
EXPOSE 9000
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
