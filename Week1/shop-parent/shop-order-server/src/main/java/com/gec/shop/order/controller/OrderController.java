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

    @GetMapping("/save")  // 下单：前端结算时按商品逐个调用
    public Order order(Long pid, String username, Integer number) {
        return orderService.createOrder(pid, username, number);
    }

    @GetMapping("/list")  // 我的订单：按用户名查询
    public java.util.List<Order> list(String username) {
        return orderService.listByUser(username);
    }
}
