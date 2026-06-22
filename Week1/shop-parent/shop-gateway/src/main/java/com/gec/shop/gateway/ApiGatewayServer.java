package com.gec.shop.gateway;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

/**
 * Day04 API 网关启动类，端口 9000。
 */
@SpringBootApplication
@EnableDiscoveryClient
public class ApiGatewayServer {
    public static void main(String[] args) {
        SpringApplication.run(ApiGatewayServer.class, args);
    }
}
