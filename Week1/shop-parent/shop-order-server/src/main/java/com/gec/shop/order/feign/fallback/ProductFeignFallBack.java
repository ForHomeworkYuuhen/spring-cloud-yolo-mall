package com.gec.shop.order.feign.fallback;

import com.gec.shop.order.feign.IProductFeginService;
import com.gec.shop.product.pojo.Product;
import org.springframework.stereotype.Component;

/**
 * Day03 6.15 Feign + Sentinel 容错类。
 * 当商品服务全部不可用时，返回兜底数据，保证订单服务不被拖垮。
 */
@Component
public class ProductFeignFallBack implements IProductFeginService {

    @Override
    public Product get(Long pid) {
        Product product = new Product();
        product.setId(-1L);
        product.setName("兜底数据");
        product.setPrice(0.0);
        product.setStock(0);
        return product;
    }
}
