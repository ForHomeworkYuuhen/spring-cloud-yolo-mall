package com.gec.shop.order.controller;

import com.gec.shop.order.service.GoodService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.concurrent.TimeUnit;

/**
 * Day03 Sentinel 流控演示控制器。
 * 涵盖：高并发雪崩雏形（6.1）、关联流控（6.8.2.2）、链路流控（6.8.2.3）。
 */
@RestController
public class SentinelController {

    @Autowired
    private GoodService goodService;

    // ---------- 6.1 模拟高并发 ----------
    @RequestMapping("/sentinel1")
    public String sentinel1() {
        // 模拟一次网络延时
        try {
            TimeUnit.SECONDS.sleep(1);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return "sentinel1";
    }

    @RequestMapping("/sentinel2")
    public String sentinel2() {
        return "测试高并发下的问题";
    }

    // ---------- 6.8.2.2 关联流控 ----------
    @RequestMapping("/sentinel-read")
    public String readReq() {
        return "读请求";
    }

    @RequestMapping("/sentinel-write")
    public String writeReq() {
        return "写请求";
    }

    // ---------- 6.8.2.3 链路流控 ----------
    @RequestMapping("/queryOrder")
    public String queryOrder() {
        goodService.queryGood();
        return "查询订单";
    }

    @RequestMapping("/createOrder")
    public String createOrder() {
        goodService.queryGood();
        return "创建订单";
    }
}
