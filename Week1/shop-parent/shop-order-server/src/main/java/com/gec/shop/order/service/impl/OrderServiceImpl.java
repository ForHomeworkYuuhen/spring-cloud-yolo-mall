package com.gec.shop.order.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.gec.shop.order.feign.IProductFeginService;
import com.gec.shop.order.mapper.OrderMapper;
import com.gec.shop.order.pojo.Order;
import com.gec.shop.order.service.OrderService;
import com.gec.shop.product.pojo.Product;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.cloud.client.discovery.DiscoveryClient;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

/**
 * 订单业务实现。
 * <p>
 * 课程循序渐进给出了 5 种"订单服务调用商品服务"的方案，下面把演进过程都保留为注释，
 * 最终采用方案 5：Feign 声明式调用（默认集成 Ribbon 负载均衡，代码最优雅）。
 */
@Service
@Slf4j
public class OrderServiceImpl extends ServiceImpl<OrderMapper, Order> implements OrderService {

    @Autowired
    private RestTemplate restTemplate;

    @Autowired
    private DiscoveryClient discoveryClient;

    @Autowired
    private IProductFeginService productFeginService;

    @Override
    public Order createOrder(Long pid, Long uid) {
        Order order = new Order();

        // ---------- 商品信息的获取（5 种演进方案） ----------
        // 方案1：RestTemplate 直连写死地址 —— ip/端口变化就要改代码
        // String url = "http://localhost:8081/products/" + pid;
        // Product product = restTemplate.getForObject(url, Product.class);

        // 方案2：DiscoveryClient 从 Nacos 取地址 —— 解决地址写死，但只取第一个实例
        // List<ServiceInstance> instances = discoveryClient.getInstances("shop-product-service");
        // ServiceInstance instance = instances.get(0);
        // String url = "http://" + instance.getHost() + ":" + instance.getPort() + "/products/" + pid;
        // Product product = restTemplate.getForObject(url, Product.class);

        // 方案3：DiscoveryClient + 随机负载均衡 —— 自己写负载均衡，太麻烦
        // List<ServiceInstance> instances = discoveryClient.getInstances("shop-product-service");
        // ServiceInstance instance = instances.get(new Random().nextInt(instances.size()));
        // String url = "http://" + instance.getHost() + ":" + instance.getPort() + "/products/" + pid;
        // Product product = restTemplate.getForObject(url, Product.class);

        // 方案4：Ribbon（@LoadBalanced RestTemplate）—— 用服务名替代 ip:port，自动负载均衡
        // String url = "http://shop-product-service/products/" + pid;
        // Product product = restTemplate.getForObject(url, Product.class);

        // 方案5：Feign 声明式调用（默认集成 Ribbon 负载均衡）—— 最终采用
        Product product = productFeginService.get(pid);

        order.setPid(pid);
        order.setProductName(product.getName());
        order.setProductPrice(product.getPrice());

        // 用户信息（演示固定为 dafei）
        order.setUid(uid == null ? 1L : uid);
        order.setUsername("dafei");
        order.setNumber(1);

        log.info("创建订单：{}", order);
        super.save(order);
        return order;
    }
}
