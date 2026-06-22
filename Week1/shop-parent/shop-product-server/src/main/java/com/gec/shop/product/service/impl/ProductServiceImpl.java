package com.gec.shop.product.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.gec.shop.product.mapper.ProductMapper;
import com.gec.shop.product.pojo.Product;
import com.gec.shop.product.service.ProductService;
import org.springframework.stereotype.Service;

@Service
public class ProductServiceImpl extends ServiceImpl<ProductMapper, Product> implements ProductService {
}
