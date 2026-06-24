package com.gec.shop.product;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;

/**
 * 商品微服务启动类。
 * 端口默认 8081，演示负载均衡时可再启动一个实例：-Dserver.port=8082
 */
@SpringBootApplication
@MapperScan("com.gec.shop.product.mapper")
@EnableDiscoveryClient
public class ProductServer {
    public static void main(String[] args) {
        SpringApplication.run(ProductServer.class, args);
    }

    /** 用于把上传的图片转发给算法层 AI 服务（直连，非 lb——AI 服务不在 Nacos）。 */
    @org.springframework.context.annotation.Bean
    public org.springframework.web.client.RestTemplate restTemplate() {
        return new org.springframework.web.client.RestTemplate();
    }
}
