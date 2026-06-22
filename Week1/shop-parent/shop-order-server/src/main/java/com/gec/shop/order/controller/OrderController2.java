package com.gec.shop.order.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Day04 网关演示用控制器，统一前缀 /order
 */
@RestController
@RequestMapping("/order")
public class OrderController2 {

    @GetMapping("/hi")
    public String hi() {
        return "hi";
    }

    @GetMapping("/hi2")
    public String hi2() {
        return "hi2";
    }
}
