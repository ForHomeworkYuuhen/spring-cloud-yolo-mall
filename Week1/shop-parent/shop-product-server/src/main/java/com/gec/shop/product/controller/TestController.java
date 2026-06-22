package com.gec.shop.product.controller;

import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Day04 7.9.2 网关 Sentinel API 分组限流演示用接口。
 */
@RestController
@RequestMapping("/v1")
public class TestController {

    @RequestMapping("/test1")
    public String test1() {
        return "test1";
    }

    @RequestMapping("/test2")
    public String test2() {
        return "test2";
    }

    @RequestMapping("/test3/test")
    public String test3() {
        return "test3";
    }
}
