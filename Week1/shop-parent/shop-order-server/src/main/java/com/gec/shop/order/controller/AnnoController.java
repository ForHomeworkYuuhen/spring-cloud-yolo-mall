package com.gec.shop.order.controller;

import com.alibaba.csp.sentinel.annotation.SentinelResource;
import com.alibaba.csp.sentinel.slots.block.BlockException;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * Day03 6.14 @SentinelResource 用法演示。
 * blockHandler 处理限流/降级（BlockException），fallback 处理业务异常（Throwable）。
 */
@RestController
@Slf4j
public class AnnoController {

    @RequestMapping("/anno1")
    @SentinelResource(value = "anno1",
            blockHandler = "anno1BlockHandler",
            fallback = "anno1Fallback")
    public String anno1(String name) {
        if ("dafei".equals(name)) {
            throw new RuntimeException();
        }
        return "anno1";
    }

    // 被限流 / 降级时进入（参数列表与原方法一致，末尾多一个 BlockException）
    public String anno1BlockHandler(String name, BlockException ex) {
        log.error("限流或降级：{}", ex.getMessage());
        return "接口被限流或者降级了";
    }

    // 抛出业务异常（Throwable）时进入
    public String anno1Fallback(String name, Throwable throwable) {
        log.error("业务异常：{}", throwable.getMessage());
        return "接口发生异常了";
    }
}
