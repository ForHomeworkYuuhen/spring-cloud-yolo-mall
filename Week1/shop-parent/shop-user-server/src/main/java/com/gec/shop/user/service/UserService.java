package com.gec.shop.user.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.gec.shop.user.pojo.User;

import java.util.Map;

/** 与商品/订单服务一致的分层：Service 接口继承 IService */
public interface UserService extends IService<User> {
    Map<String, Object> register(User u);
    Map<String, Object> login(User u);
}
