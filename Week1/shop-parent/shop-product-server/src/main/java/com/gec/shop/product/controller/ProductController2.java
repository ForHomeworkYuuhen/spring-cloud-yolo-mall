package com.gec.shop.product.controller;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Day04 网关演示用控制器，统一前缀 /product
 */
@Slf4j
@RestController
@RequestMapping("/product")
public class ProductController2 {

    @Value("${server.port}")
    private String myport;

    @GetMapping("/hello")
    public String hello() {
        log.info("hello方法被执行了 {}", "hello------------------");
        return "hello";
    }

    @GetMapping("/hello2/hello3/hello4")
    public String hello2() {
        log.info("hello2方法被执行了 {}", "hello2------------------");
        return "hello2";
    }

    @RequestMapping("/hello3")
    public String hello3() {
        log.info("hello3方法被执行了 {}", "hello3------------------");
        return "hello3" + myport;
    }
}
