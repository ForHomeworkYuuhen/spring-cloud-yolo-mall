package com.gec.shop.order.controller;

import com.gec.shop.order.pojo.Order;
import com.gec.shop.order.service.OrderService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 订单接口。创建订单：/orders/save?pid=1&uid=1
 */
@RestController
@RequestMapping("orders")
public class OrderController {

    @Autowired
    private OrderService orderService;

    @GetMapping("/save")  // 测试方便，使用 Get 方式
    public Order order(Long pid, Long uid) {
        return orderService.createOrder(pid, uid);
    }
}
