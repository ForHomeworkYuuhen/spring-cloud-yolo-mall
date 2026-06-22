package com.gec.shop.order.feign;

import com.gec.shop.order.feign.fallback.ProductFeignFallBack;
import com.gec.shop.product.pojo.Product;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

/**
 * Day02 Feign 声明式远程调用接口。
 * <ul>
 *   <li>name 必须是商品服务在 Nacos 上注册的服务名 shop-product-service</li>
 *   <li>方法签名 / 路径必须与商品服务的 ProductController 一致</li>
 *   <li>fallback 为 Day03 6.15 Feign 整合 Sentinel 的容错类（需开启 feign.sentinel.enabled）</li>
 * </ul>
 */
@FeignClient(name = "shop-product-service", fallback = ProductFeignFallBack.class)
public interface IProductFeginService {

    @GetMapping("/products/{pid}")
    Product get(@PathVariable("pid") Long pid);
}
