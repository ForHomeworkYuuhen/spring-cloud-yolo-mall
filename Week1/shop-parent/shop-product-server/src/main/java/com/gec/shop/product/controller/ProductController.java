package com.gec.shop.product.controller;

import com.gec.shop.product.pojo.Product;
import com.gec.shop.product.service.ProductService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 商品信息查询接口。访问路径：/products/{pid}
 */
@RestController
@RequestMapping("products")
@Slf4j
public class ProductController {

    @Autowired
    private ProductService productService;

    @Value("${server.port}")
    private String port;

    @GetMapping("/{pid}")
    public Product findByPid(@PathVariable("pid") Long pid) {
        log.info("接下来要进行{}号商品信息的查询", pid);
        Product product = productService.getById(pid);
        if (product == null) {
            log.warn("未查询到{}号商品", pid);
            return null;
        }
        // 在商品名后拼接端口号，便于在订单服务侧直观观察 Ribbon 负载均衡效果（Day02）
        product.setName(product.getName() + "—" + port);
        log.info("商品信息查询成功，内容为{}", product);
        return product;
    }
}
