package com.gec.shop.order;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cloud.client.discovery.EnableDiscoveryClient;
import org.springframework.cloud.client.loadbalancer.LoadBalanced;
import org.springframework.cloud.openfeign.EnableFeignClients;
import org.springframework.context.annotation.Bean;
import org.springframework.web.client.RestTemplate;

/**
 * 订单微服务启动类，端口 8091。
 * <ul>
 *   <li>{@code @EnableDiscoveryClient} 注册到 Nacos（Day01）</li>
 *   <li>{@code @EnableFeignClients} 开启 Feign 声明式调用（Day02）</li>
 *   <li>{@code @LoadBalanced} 让 RestTemplate 具备 Ribbon 负载均衡能力（Day02）</li>
 * </ul>
 */
@SpringBootApplication
@MapperScan("com.gec.shop.order.mapper")
@EnableDiscoveryClient
@EnableFeignClients
public class OrderServer {

    public static void main(String[] args) {
        SpringApplication.run(OrderServer.class, args);
    }

    @Bean
    @LoadBalanced
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
