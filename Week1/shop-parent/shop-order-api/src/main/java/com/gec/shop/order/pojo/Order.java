package com.gec.shop.order.pojo;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.io.Serializable;

/**
 * 订单实体，对应数据库 shop-order 库中的 t_order 表
 */
@Getter
@Setter
@ToString
@TableName("t_order")
public class Order implements Serializable {

    @TableId(type = IdType.AUTO)
    private Long id;          // 订单 id
    // 用户
    private Long uid;         // 用户 id
    private String username;  // 用户名
    // 商品
    private Long pid;         // 商品 id
    private String productName;  // 商品名称（映射 product_name）
    private Double productPrice; // 商品单价（映射 product_price）
    // 数量
    private Integer number;   // 购买数量
}
