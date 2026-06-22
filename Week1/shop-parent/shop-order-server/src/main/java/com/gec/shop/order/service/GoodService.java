package com.gec.shop.order.service;

import com.alibaba.csp.sentinel.annotation.SentinelResource;
import org.springframework.stereotype.Service;

/**
 * Day03 6.8.2.3 链路流控演示。
 * 默认情况下普通方法不被 Sentinel 监控，通过 @SentinelResource 标记为受监控资源。
 */
@Service
public class GoodService {

    @SentinelResource("queryGood")
    public void queryGood() {
        System.out.println("查询商品");
    }
}
