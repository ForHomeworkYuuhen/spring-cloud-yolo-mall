package com.gec.shop.order.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.gec.shop.order.pojo.Order;

public interface OrderService extends IService<Order> {

    /**
     * 创建订单：根据商品 id 远程查询商品信息后保存订单。
     *
     * @param pid 商品 id
     * @param uid 用户 id
     */
    Order createOrder(Long pid, Long uid);
}
