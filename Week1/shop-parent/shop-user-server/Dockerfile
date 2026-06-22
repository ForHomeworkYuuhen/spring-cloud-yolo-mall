# syntax=docker/dockerfile:1
FROM maven:3.9-eclipse-temurin-8 AS build
WORKDIR /build
COPY . .
RUN --mount=type=cache,target=/root/.m2,sharing=locked \
    mvn -B -pl shop-user-server -am clean package -DskipTests

FROM eclipse-temurin:8-jre
WORKDIR /app
COPY --from=build /build/shop-user-server/target/*.jar app.jar
EXPOSE 8071
ENTRYPOINT ["java", "-jar", "/app/app.jar"]
