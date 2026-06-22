package com.gec.shop.user.pojo;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import lombok.Getter;
import lombok.Setter;
import lombok.ToString;

import java.io.Serializable;

/** 用户实体，对应 shop-user 库 t_user 表 */
@Getter
@Setter
@ToString
@TableName("t_user")
public class User implements Serializable {
    @TableId(type = IdType.AUTO)
    private Long id;
    private String username;
    private String password;   // 演示明文；生产应 BCrypt 加盐
    private String phone;
    private String nickname;
}
